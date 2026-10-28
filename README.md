# Panaroo 1.8.1

TAFFISH app for [Panaroo](https://github.com/gtonkinhill/panaroo), a bacterial
pangenome graph construction and cleaning pipeline. The default command passes arguments to `panaroo`; optional verified resource discovery is handled by the wrapper; TAFFISH automatic command mode also exposes
every console command registered by upstream.

## Package identity

- Name: `panaroo`
- Command: `taf-panaroo`
- Kind: `tool`
- TAFFISH version: `1.8.1-r1`
- Container image: `ghcr.io/taffish/panaroo:1.8.1-r1`
- App license: Apache-2.0
- Upstream tag: `v1.8.1`
- Upstream commit: `dbe596c3d24acfe2df1be64f76550b324d167243`
- Runtime version: `panaroo 1.8.1`
- Source SHA-256: `b909740a0e7ab371a871a18467f1eaa61d5d0581117c62f440bd16c16b37c302`
- Container platforms: `linux/amd64`, `linux/arm64`
- Default command: `panaroo`

The app repository is Apache-2.0 licensed. Panaroo and `biocode` are MIT
licensed. Prokka, MUSCLE, and the bundled FAMSA binary are GPL-3.0 licensed.
Copied upstream license texts and Debian package copyright files remain in the
image.

## Included interfaces

The image preserves all 14 upstream console entry points:

- `panaroo`, `run_prokka`, `panaroo-qc`, `panaroo-merge`
- `panaroo-plot-abundance`, `panaroo-spydrpick`, `panaroo-img`, `panaroo-fmg`
- `panaroo-msa`, `panaroo-gene-neighbourhood`, `panaroo-integrate`
- `panaroo-filter-pa`, `panaroo-generate-gffs`, `panaroo-extract-gene`

Panaroo 1.8.1 also ships `scripts/convert_bakta_to_prokka_gff.py` without a
console entry point. This app adds the narrowly scoped
`panaroo-convert-bakta-to-prokka-gff` alias for that upstream script. Other
research and benchmark scripts are not exposed or copied into the runtime,
because many target unrelated external ecosystems not required by Panaroo.

## Runtime closure

The dual-architecture image installs Panaroo's Python dependencies plus the
external executables called by supported public paths:

- CD-HIT and CD-HIT-EST for clustering
- MAFFT, PRANK, Clustal Omega, MUSCLE 5, and FAMSA 2.4.1 for alignment
- Mash for `panaroo-qc` distance and optional contamination calculations
- Prokka 1.14.6, its complete indexed upstream database, Prodigal, Barrnap,
  and the source-bundled MinCED for `run_prokka`
- Matplotlib and Plotly for static PNG and interactive HTML QC artifacts
- `biocode` for Panaroo's GenBank-to-GFF conversion path

The dependency chain also includes Prokka's GNU Parallel, ARAGORN, HMMER,
BLAST, Infernal and table/conversion utilities, Barrnap's `nhmmer`/`bedtools`,
and the Perl/shell helpers. These installed entry points are explicitly listed
in the runtime smoke manifest. MAFFT's launcher uses Debian `file` to diagnose
UTF-16/UTF-32 input before alignment; that utility is included rather than
patching or bypassing the upstream encoding check.
The standard non-interactive MAFFT alignment/profile paths used by Panaroo are
covered. Optional MAFFT modes requiring MPI or separately installed external
or structure-aware aligners are not included. Manual-page rendering through
`mafft --man` is not packaged; use the upstream `--help` output instead.

MAFFT is retained even when another aligner is selected because Panaroo uses
it as a profile/codon-alignment fallback. FAMSA is installed from exact
architecture-specific v2.4.1 release assets. MUSCLE 5.3 is built natively from
its exact source after correcting upstream's AArch64 compiler-macro detection;
architecture-specific tuning is disabled so each binary remains portable
within its declared platform. Debian's native runtime packages avoid an
emulated amd64-only Conda environment on arm64. The exact Debian package set is recorded at
`/opt/panaroo/share/provenance/debian-packages.tsv` in each image.

`biocode` is installed as a Python dependency, but its large collection of
unrelated command-line scripts is not exposed. Upstream source archives are
checksum-verified during construction but omitted from the runtime. Source
identities and checksums remain in `/opt/panaroo/share/provenance/`, and copied
license texts remain under `/opt/panaroo/share/licenses/`.

## Image footprint

The image retains the complete indexed Prokka database, scientific Python
stack, six aligner modes and a native headless Java runtime for Prokka's MinCED.
No production Mash reference is embedded. Cytoscape, JavaFX, noVNC and the
desktop services are not bundled: graph browsing is provided by the separate
Cytoscape app described below.

Native final split-candidate measurements (2026-10-27): AMD64 2,044,537,473 bytes,
image ID `275d9a6de07b22c23fd05585ea2aee3cf1ae2b377272649ebee97f2147489ee9`;
ARM64 2,051,474,694 bytes, image ID
`2a3a71e899a326d14d7688e8ac1b3b5946f4f7788b76c2e15310712851744e0a`.
These are Docker image-inspect sizes, not compressed downloads or physical
disk usage. They replace the earlier combined and split-image measurements;
they do not include the independently installed Cytoscape image.

## Source stability

Fixed source/archive hashes reject changed bytes, not disappearing upstream
downloads. Debian suite packages, pip build-isolation dependencies and the
Dockerfile frontend can change independently of the pinned base image.
Resolved package lists and source provenance are retained in the image.
A future unavailable dependency needs a new review, not checksum bypasses.
Panaroo 1.8.1's upstream CD-HIT and genome-location fixes are included verbatim;
no Panaroo algorithm patch is applied.

## Installation

After refreshing the TAFFISH index, install the current release or request
this exact immutable package version:

```console
taf update
taf install panaroo
taf install panaroo 1.8.1-r1
```

## Usage

Show the installed-app guide, upstream help, and upstream version:

```console
taf-panaroo --help
taf-panaroo -- --help
taf-panaroo -- --version
```

Run the main pipeline on Prokka-style combined GFF3+FASTA inputs:

```console
taf-panaroo -i isolate1.gff isolate2.gff isolate3.gff \
  -o panaroo-results --clean-mode strict -t 8
```

Request a core-gene alignment:

```console
taf-panaroo -i *.gff -o panaroo-results --clean-mode strict \
  --alignment core --aligner mafft -t 8
```

Use an upstream secondary command through automatic command mode:

```console
taf-panaroo panaroo-merge --help
taf-panaroo run_prokka --help
taf-panaroo panaroo-convert-bakta-to-prokka-gff \
  --gff bakta.gff3 --out prokka-style.gff
```

The documented `taf-panaroo COMMAND ...` form is preferred for subcommands.
Use `taf-panaroo -- ...` when the first argument for the default `panaroo`
command begins with `-` and would otherwise be consumed by the wrapper.

## Inputs and operational boundaries

The normal input is two or more Prokka-style GFF3 files with an embedded
`##FASTA` section. Panaroo also accepts supported list-file, separate
GFF+FASTA, and GenBank forms; see upstream documentation for exact syntax.
Keep inputs and outputs under the working tree mounted by TAFFISH.

No external database is needed for the main pangenome pipeline. The optional
`panaroo-qc --ref_db` contamination path accepts a user-supplied Mash sketch.
The new helper only imports a local, checksummed, authorized file; it never
silently downloads a reference.

`run_prokka` is included because it is a public Panaroo entry point and calls
both Prokka and Prodigal. Its output directory must already exist. The full
official Prokka 1.14.6 database is pre-indexed in the image; no setup or
download is needed. Production annotation choices, taxonomy, and any optional
additional Prokka databases remain the user's responsibility.

Prokka's freely redistributable Barrnap and MinCED paths are available.
SignalP and RNAmmer are not bundled because their upstream distribution terms
do not permit treating them as ordinary open runtime dependencies; users who
are separately authorized to use them may provide them through Prokka's own
supported command options.

## Static browser artifacts

`panaroo-qc` is a headless CLI that creates PNG files and self-contained
Plotly HTML files. It is not a service GUI: there are no ports, authentication,
noVNC session, background daemon, or shutdown lifecycle. Create its output
directory first, run the command, then open the resulting HTML locally:

```console
mkdir -p panaroo-qc
taf-panaroo panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
  -o panaroo-qc --graph_type all --random_seed 1 -t 4
```

Automated smoke verifies nonempty PNGs, Plotly render calls, and absence of
remote script sources. Browser rendering is a separate visual acceptance gate;
the smoke does not establish biological validity for production data.

Use a QC output path without spaces or shell metacharacters, including every
parent directory visible inside the container. Upstream `panaroo-qc` builds
its internal `mash triangle` shell command without quoting those paths.
TAFFISH's literal-quote syntax preserves the argument passed to Panaroo but
cannot repair that upstream internal command. A spaced output path fails;
keep the failed output for diagnosis and retry in a new simple output path.
This does not change the independently supported quoted GML paths in Cytoscape.

For maintainers testing an uninstalled source checkout, run from the app root
and keep the inputs and new output directories in that tree. Choose an available
backend explicitly; each command below is a separate short-lived QC run, not
a background web service:

```console
mkdir -p qc-docker qc-podman qc-apptainer
taf run -b docker -- panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
  -o qc-docker --graph_type all --random_seed 1 -t 4
taf run -b podman -- panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
  -o qc-podman --graph_type all --random_seed 1 -t 4
taf run -b apptainer -- panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
  -o qc-apptainer --graph_type all --random_seed 1 -t 4
```

The same simple-path restriction applies to the checkout and output parents.
On 2026-10-26, real `taf run` generated all three HTML and PNG artifacts with
current-source isolated copies on xjp Docker/Podman/Apptainer and ARM64 Docker.
Missing input and unsupported spaced-output failures were separately recorded;
source files and production targets were unchanged. Installed-user commands
remain in `docs/help.md`.

## Validation coverage

Independent, offline smoke cases verify:

- exact Panaroo/Prokka/FAMSA/MUSCLE identity, Python imports, source checksums,
  and provenance
- all public command help surfaces and all declared external executables
- a complete three-isolate pangenome run with real CD-HIT execution
- real MAFFT, PRANK, Clustal Omega, MUSCLE, MUSCLE Super5, and FAMSA alignments
- GenBank conversion through `biocode` and the Bakta conversion helper
- Mash, Matplotlib, and self-contained Plotly output through `panaroo-qc`
- the `run_prokka` path through trained Prodigal and Prokka annotation, plus
  direct MinCED execution with the retained headless Java runtime

These fixtures are deliberately small and deterministic. They validate
packaging and representative execution paths, not scientific correctness,
cohort-scale performance, or every combination of upstream options.

## Citation

Tonkin-Hill G et al. *Producing polished prokaryotic pangenomes with the
Panaroo pipeline.* Genome Biology 21, 180 (2020).
[doi:10.1186/s13059-020-02090-4](https://doi.org/10.1186/s13059-020-02090-4),
PMID: 32698896.

Upstream manual: <https://gtonkinhill.github.io/panaroo/>

## Verified Mash resources

The upstream QC documentation links the historical RefSeq Mash sketch at
<https://gembox.cbcb.umd.edu/mash/refseq.genomes.k21s1000.msh>.
That approximately 754 MB resource is not bundled. The endpoint is not a
versioned release with an authoritative published SHA256, and a software license
does not grant rights over all reference data. Before acquisition, review the
source terms and [NCBI data policies](https://www.ncbi.nlm.nih.gov/home/about/policies/).
Keep the original source/version, actual checksum and applicable data notice.
The helper supports this reference or an authorized private sketch; private
references must not be promoted to public access without permission.

```console
mkdir -p shared
taf-panaroo panaroo-mash-resources prepare --resource-root shared/mash \
  --file reference.msh --sha256 ACTUAL_SHA256 --id YOUR_VERSION \
  --source urn:your-source:version --license-file LICENSE \
  --rights-reviewed --access personal --dry-run
```

Repeat without `--dry-run` after reviewing source identity, license and disk
space. The parent must exist. Preparation validates Mash structure, checks the
expected SHA256, reserves input size plus notice plus 16 MiB, copies to a private
transaction directory, validates every member, then atomically promotes without
replacing any existing path. No `--force` option exists. Complete identical
resources are reused. Corrupt/partial destinations, foreign locks and dangling
links are preserved and rejected; restore original bytes or use a new member
path. INT/TERM cleans only the transaction's own endpoints; SIGKILL can leave
inspectable staging/lock files and never authorizes blind deletion.

On filesystems without Linux no-replace directory rename (including the tested
Docker Desktop gRPC FUSE share), the helper exclusively creates a relative
symlink to the complete, verified hidden `.NAME.payload.*` directory. This is
an atomic publication, not a check-then-overwrite rename. The payload is then
permanent resource storage: keep it with its visible member link; do not remove
it as temporary data. If neither safe publication operation is available, setup
fails without replacing the old resource. Use a compatible filesystem/backend.

Set `TAFFISH_PANAROO_DB_PATH` to the prepared member, not its parent. The same
validator runs in the host wrapper and inside `panaroo-mash-resources verify`.
Discovery tries explicit DB_PATH, then
`~/.local/share/taffish/databases/panaroo/mash`,
`/usr/local/share/taffish/databases/panaroo/mash`, and
`/opt/taffish/databases/panaroo/mash`. The first existing invalid member fails;
it is not silently replaced with a lower-priority resource. Valid root symlinks
are resolved; symlinked member files are rejected. Host Python 3 is required for
automatic validation; `TAFFISH_PANAROO_DB_AUTO_MOUNT=0` disables discovery.

An administrator can install once into a site-wide member using `--access
public` (directories 0755, files 0644), with searchable parent directories.
Ordinary users discover it and read `/panaroo-mash/reference.msh` without another
download or write access. `personal` uses 0700/0600. This is explicit access
selection, not permission escalation by the helper.

Docker/Podman use a read-only volume; Apptainer uses a read-only bind. If host
Python is unavailable, disable discovery, verify through the container helper,
then provide an explicit bind:

```console
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_PANAROO_DB_AUTO_MOUNT=0 \
  TAFFISH_DOCKER_RUN_ARGS='-v /HOST/MEMBER:/panaroo-mash:ro' \
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PANAROO_DB_AUTO_MOUNT=0 \
  TAFFISH_PODMAN_RUN_ARGS='-v /HOST/MEMBER:/panaroo-mash:ro' \
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_PANAROO_DB_AUTO_MOUNT=0 \
  TAFFISH_APPTAINER_RUN_ARGS='--bind /HOST/MEMBER:/panaroo-mash:ro' \
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
```

For installation use a separate writable parent bind, with discovery disabled;
do not make an existing shared resource writable during normal analysis.
Paths containing colons/commas are rejected by automatic mount construction.
The main bundled Prokka database is immutable image content, already indexed;
it needs no external resource helper or system-wide download.

Resource regression validation uses a synthetic CC0 sketch, not a production
reference. It covers administrator-once public preparation, ordinary-user
read-only reuse, interruption/recovery/idempotence, broken members, valid and
dangling links, permissions, foreign locks and outside sentinels. Fresh
real-wrapper checks for the final image passed on native xjp AMD64
Docker/Podman/Apptainer and native ARM64 Docker/Podman. The isolated
administrator-once sharing test passed all 15 checks: installation/idempotence,
ordinary-user read-only reuse and write rejection across all three backends,
then ownership return. All backends reused the same root-owned resource.
No full RefSeq acquisition, real
system-directory installation or production reference analysis is claimed.

## Optional graph inspection with standalone Cytoscape

Panaroo writes `final_graph.gml` but does not call Cytoscape internally. The
two apps exchange this ordinary output file; there is no pipe, hidden desktop
dependency or running-service requirement for Panaroo analysis or QC. Keep the
GML with the analysis results. It is project data, not a shared reference
resource.

After installing the separate Cytoscape app, generate a graph with Panaroo
and open it in the other app:

```console
taf-panaroo -i isolate1.gff isolate2.gff isolate3.gff \
  -o panaroo-results --clean-mode strict -t 8
mkdir -p graph-exports
TAFFISH_CONTAINER_BACKEND=docker \
  TAFFISH_DOCKER_RUN_ARGS='-p 127.0.0.1:5800:5800' \
  taf-cytoscape cytoscape-gui \
  --network panaroo-results/final_graph.gml --outdir graph-exports
```

Open the URL printed by Cytoscape after it reports ready. For command-mode
paths containing spaces, preserve inner quotes, for example
`--network '"results with spaces/final_graph.gml"'` and
`--outdir '"graph exports"'`. The output directory must already exist.
Run `taf-cytoscape --help` for complete Docker, Podman and Apptainer launch,
loopback binding, SSH tunnel and stop instructions. Its GUI lifecycle,
temporary profile and desktop dependencies belong to that app, not Panaroo.

Layout, selection and exports are Cytoscape features. Saving a CYS session or
an image does not modify Panaroo's analysis outputs or feed a result back into
its pipeline. The native Panaroo QC HTML reports above remain independently
usable without installing or starting Cytoscape.

## Maintainer validation status

This unpublished 1.8.1-r1 candidate has been rebuilt natively for AMD64 and
ARM64 after splitting out the desktop and completing the MAFFT dependency
closure. As of 2026-10-27, native xjp AMD64 Docker/Podman/Apptainer and native
ARM64 Docker/Podman passed their fresh offline exact matrices and real wrappers.
Each direct matrix has 85 commands; Docker/Podman also passed separate non-root
read-only matrices, for 765 exact checks in total. Each of the five wrapper
runs passed 94 checks (470 total), including the CLI,
headless Java/MinCED, Prokka, QC and resource recovery/idempotence paths.
Their audits checked 28 official Panaroo source files, four local COPY inputs,
parent-directory access and the absence of the removed desktop payload.

Each of the five combinations also passed 12 encoding checks, four development
command checks and installed-help validation. The final AMD64 SIF is
624,300,032 bytes, SHA256
`6d38faf50ca8a9fc44971a5883ea3cfdb19b129758c688cd54c7a58c0baae478`.
The earlier temporary-space failure and local VM stoppages are retained;
successful final runs, not partial attempts or earlier SIFs, support these results.

The three final QC HTML files match the manually accepted split reports after
normalizing only their generated Plotly identifiers. The final GML files match
the graph opened in Cytoscape apart from membership ordering, not graph content.
Detailed source-bound receipts and final publication-plan/cleanup decisions
are retained in the maintainer handoff. The split does not change Panaroo
algorithms, its resource helper or the canonical Action. Runtime validation
is separate from publication, which remains a maintainer action.

ARM64 Apptainer remains a separate untested cross-combination; AMD64 SIF/bind
checks cannot establish ARM64 execution. Production databases, scientific
performance and public CI/GHCR/Index are not claimed. The maintainer must
publish manually and inspect the new public artifacts. Earlier merged-image
validation and failed/environmental runs remain historical evidence only.
