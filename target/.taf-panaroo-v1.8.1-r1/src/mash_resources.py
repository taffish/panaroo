#!/usr/bin/env python3
"""Offline, immutable import and verification of one authorized Mash sketch."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile

SCHEMA = 'taffish.panaroo.mash.v1'
FILES = {'reference.msh', 'LICENSE', 'resource.json', 'READY'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def regular(path):
    return stat.S_ISREG(path.lstat().st_mode)


def verify(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('missing resource directory')
    root = root.resolve(strict=True)  # A valid root symlink is supported.
    if {p.name for p in root.iterdir()} != FILES:
        raise ValueError('unexpected or missing resource members')
    for name in FILES:
        if not regular(root / name) or (root / name).stat().st_size == 0:
            raise ValueError('empty, symlinked or non-regular member: ' + name)
    if (root / 'READY').read_text().strip() != digest(root / 'resource.json'):
        raise ValueError('resource manifest digest mismatch')
    data = json.loads((root / 'resource.json').read_text())
    if set(data) != {'schema', 'id', 'source', 'sha256', 'bytes', 'license_sha256', 'access', 'mash_info'}:
        raise ValueError('invalid resource manifest fields')
    if data['schema'] != SCHEMA or not isinstance(data['id'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', data['id']):
        raise ValueError('invalid resource schema or ID')
    if not isinstance(data['source'], str) or not data['source'].startswith(('https://', 'urn:')) or any(ord(x) < 32 for x in data['source']):
        raise ValueError('invalid resource source')
    if data['access'] not in ('personal', 'public') or not isinstance(data['mash_info'], str) or not data['mash_info'].strip():
        raise ValueError('invalid access or Mash identity')
    if type(data['bytes']) is not int or data['bytes'] != (root / 'reference.msh').stat().st_size:
        raise ValueError('resource byte count mismatch')
    for key, name in [('sha256', 'reference.msh'), ('license_sha256', 'LICENSE')]:
        if not isinstance(data[key], str) or not re.fullmatch('[0-9a-f]{64}', data[key]) or data[key] != digest(root / name):
            raise ValueError('resource checksum mismatch: ' + name)
    dmode, fmode = (0o755, 0o644) if data['access'] == 'public' else (0o700, 0o600)
    if stat.S_IMODE(root.stat().st_mode) != dmode or any(stat.S_IMODE((root / n).stat().st_mode) != fmode for n in FILES):
        raise ValueError('resource permissions differ from recorded access scope')
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'verify'])
    p.add_argument('--resource-root', required=True, type=Path,
                   help='complete versioned member path; its parent must already exist')
    p.add_argument('--file', type=Path)
    p.add_argument('--sha256')
    p.add_argument('--id')
    p.add_argument('--source', help='fixed acquisition URL or local provenance urn:')
    p.add_argument('--license-file', type=Path)
    p.add_argument('--rights-reviewed', action='store_true')
    p.add_argument('--access', choices=['personal', 'public'], default='personal')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if a.mode == 'verify':
        if any([a.file, a.id, a.source, a.license_file, a.rights_reviewed, a.dry_run]) or a.access != 'personal':
            p.error('prepare-only option passed to verify')
        data = verify(a.resource_root)
        if a.sha256 and a.sha256 != data['sha256']:
            raise ValueError('unexpected resource SHA256')
        print('verified: ' + str(a.resource_root.resolve() / 'reference.msh'))
        return 0
    if not all([a.file, a.sha256, a.id, a.source, a.license_file, a.rights_reviewed]):
        p.error('prepare requires file, sha256, id, source, license-file and rights-reviewed')
    if not re.fullmatch('[0-9a-f]{64}', a.sha256) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', a.id):
        p.error('expected lowercase SHA256 and an alphanumeric-leading ID (letters/digits/._-, max 100)')
    if not a.source.startswith(('https://', 'urn:')) or any(ord(x) < 32 for x in a.source):
        p.error('source must be a fixed HTTPS URL or provenance URN without control characters')
    final = a.resource_root.absolute()
    if final.name in ('', '.', '..'):
        p.error('resource-root must name one new versioned member')
    parent = final.parent.resolve(strict=True)
    final = parent / final.name
    for path in (a.file, a.license_file):
        if not regular(path) or path.stat().st_size == 0:
            raise ValueError('input/notice must be nonempty regular files, not symlinks')
    if digest(a.file) != a.sha256:
        raise ValueError('input SHA256 mismatch')
    result = subprocess.run(['mash', 'info', str(a.file.resolve())], capture_output=True, text=True, timeout=60)
    if result.returncode or 'Sketches' not in result.stdout:
        raise ValueError('invalid Mash sketch: ' + result.stderr[-1000:])
    data = dict(schema=SCHEMA, id=a.id, source=a.source, sha256=a.sha256,
                bytes=a.file.stat().st_size, license_sha256=digest(a.license_file),
                access=a.access, mash_info=result.stdout)
    if os.path.lexists(final):
        existing = verify(final)
        if existing != data:
            raise ValueError('existing resource conflicts; preserve it and choose a new versioned path')
        print('already complete (unchanged): ' + str(final))
        return 0
    needed = data['bytes'] + a.license_file.stat().st_size + 16 * 1024 * 1024
    if shutil.disk_usage(parent).free < needed:
        raise ValueError('insufficient space for staged copy and 16 MiB reserve')
    print(json.dumps(dict(data, required_free_bytes=needed, destination=str(final), network='none'), sort_keys=True), flush=True)
    if a.dry_run:
        print('dry-run: no files changed; acquisition and sharing rights remain operator responsibilities')
        return 0
    lock = parent / ('.' + final.name + '.lock')
    stage = None
    owned_lock = owned_stage = None
    interrupted = 0
    def stop(number, frame):
        nonlocal interrupted
        interrupted = interrupted or (143 if number == signal.SIGTERM else 130)
    def check():
        if interrupted:
            raise InterruptedError()
    handlers = {s: signal.signal(s, stop) for s in (signal.SIGINT, signal.SIGTERM)}
    # Pin the parent; cleanup uses relative names and never follows replacements.
    parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    def identity(path):
        st = os.lstat(path)
        return st.st_dev, st.st_ino
    def cleanup():
        for path, owned, members in ((stage, owned_stage, FILES), (lock, owned_lock, set())):
            if path is None or owned is None:
                continue
            try:
                st = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                if not stat.S_ISDIR(st.st_mode) or (st.st_dev, st.st_ino) != owned:
                    continue
                fd = os.open(path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
                try:
                    opened = os.fstat(fd)
                    if (opened.st_dev, opened.st_ino) != owned:
                        continue
                    for name in members:
                        try:
                            os.unlink(name, dir_fd=fd)  # Symlinks themselves, never their targets.
                        except FileNotFoundError:
                            pass
                    current = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                    if (current.st_dev, current.st_ino) == owned:
                        os.rmdir(path.name, dir_fd=parent_fd)
                finally:
                    os.close(fd)
            except OSError as error:
                try:
                    print('cleanup retained owned endpoint for inspection: ' + str(error), file=sys.stderr)
                except OSError:
                    pass
    try:
        os.mkdir(lock.name, mode=0o700, dir_fd=parent_fd)
        owned_lock = identity(lock)
        check()
        if os.path.lexists(final):
            raise ValueError('destination appeared during setup; retry after verifying it')
        stage = Path(tempfile.mkdtemp(prefix='.' + final.name + '.payload.', dir=parent))
        owned_stage = identity(stage)
        check()
        for source, name in ((a.file, 'reference.msh'), (a.license_file, 'LICENSE')):
            check()
            with source.open('rb') as src, (stage / name).open('xb') as dst:
                while block := src.read(4 * 1024 * 1024):
                    check()
                    dst.write(block)
                dst.flush()
                os.fsync(dst.fileno())
            check()
        (stage / 'resource.json').write_text(json.dumps(data, indent=2) + '\n')
        (stage / 'READY').write_text(digest(stage / 'resource.json') + '\n')
        dmode, fmode = (0o755, 0o644) if a.access == 'public' else (0o700, 0o600)
        for name in FILES:
            os.chmod(stage / name, fmode)
        os.chmod(stage, dmode)
        if verify(stage) != data:
            raise ValueError('staging identity mismatch')
        check()
        # Linux renameat2(RENAME_NOREPLACE) prevents overwriting any old endpoint.
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        if rename(parent_fd, os.fsencode(stage.name), parent_fd, os.fsencode(final.name), 1):
            error = ctypes.get_errno()
            if error not in (errno.EINVAL, errno.ENOSYS, errno.EOPNOTSUPP):
                raise OSError(error, 'atomic no-replace promotion failed; old resource untouched')
            # Some host-sharing filesystems lack RENAME_NOREPLACE. Publishing a
            # relative symlink is also an atomic, exclusive operation: an old
            # directory/file/link is never replaced, and only complete verified
            # payloads become visible. The hidden payload is permanent storage,
            # not disposable staging. If symlinks are unsupported, fail closed.
            if identity(stage) != owned_stage or verify(stage) != data:
                raise ValueError('payload identity changed before publication')
            os.symlink(stage.name, final.name, dir_fd=parent_fd)
        owned_stage = None
        check()
        print('prepared: ' + str(final), flush=True)
        return 0
    except InterruptedError:
        print('interrupted; a complete promoted resource is retained, partial owned staging is cleaned', file=sys.stderr)
        return interrupted or 130
    finally:
        cleanup()
        os.close(parent_fd)
        for s, handler in handlers.items():
            signal.signal(s, handler)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print('panaroo-mash-resources: ' + str(error), file=sys.stderr)
        sys.exit(1)
