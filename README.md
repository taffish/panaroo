# Panaroo 1.8.0

TAFFISH app for [Panaroo](https://github.com/gtonkinhill/panaroo), a bacterial
pangenome graph construction and cleaning pipeline. The default wrapper is a
thin pass-through to `panaroo`; TAFFISH automatic command mode also exposes
every console command registered by upstream.

## Package identity

- Name: `panaroo`
- Command: `taf-panaroo`
- Kind: `tool`
- TAFFISH version: `1.8.0-r1`
- Container image: `ghcr.io/taffish/panaroo:1.8.0-r1`
- App license: Apache-2.0
- Upstream tag: `v1.8.0`
- Upstream commit: `e96b4978327536256b5c663f741138fc7aabed64`
- Runtime version: `panaroo 1.8.0`
- Source SHA-256: `3890a71c140a17c69fb3a1dd52598ee375a05fcbd10e0e283a59016ec027ef4f`
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

Panaroo 1.8.0 also ships `scripts/convert_bakta_to_prokka_gff.py` without a
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

The final local release candidates are 2,015,574,841 bytes on `linux/amd64`
and 2,022,148,524 bytes on `linux/arm64` (about 1.88 GiB each). The dominant
runtime components are the complete indexed Prokka database (607 MiB), the
Python scientific/plotting stack (about 381-393 MiB), Java headless for
MinCED (194 MiB), and native libraries (about 333-338 MiB).

Removing build toolchains, source archives, package caches, manuals,
non-license development documentation, and regenerable Python bytecode, plus
replacing duplicate runtime executables with symbolic links, reduced the first
function-complete arm64 candidate by 371,715,932 bytes (15.53%). Runtime Python
source remains intact; bytecode generation is disabled, trading a small amount
of process-start CPU time for the smaller immutable image. There is no
remaining large cache or build-only tree. A material further reduction would
require removing a documented public path, such as the full Prokka annotation
closure, an aligner, or static plotting support, so it is not treated as safe
slimming for this package.

## Installation

After refreshing the TAFFISH index, install the current release or request
this exact immutable package version:

```console
taf update
taf install panaroo
taf install panaroo 1.8.0-r1
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
`panaroo-qc --ref_db` contamination path requires a user-supplied Mash database
and does not download one at runtime. The image performs no automatic network
access in its tested paths.

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

## Validation coverage

Independent, offline smoke cases verify:

- exact Panaroo/Prokka/FAMSA/MUSCLE identity, Python imports, source checksums,
  and provenance
- all public command help surfaces and all declared external executables
- a complete three-isolate pangenome run with real CD-HIT execution
- real MAFFT, PRANK, Clustal Omega, MUSCLE, MUSCLE Super5, and FAMSA alignments
- GenBank conversion through `biocode` and the Bakta conversion helper
- Mash, Matplotlib, and self-contained Plotly output through `panaroo-qc`
- the `run_prokka` path through trained Prodigal and Prokka annotation

These fixtures are deliberately small and deterministic. They validate
packaging and representative execution paths, not scientific correctness,
cohort-scale performance, or every combination of upstream options.

## Citation

Tonkin-Hill G et al. *Producing polished prokaryotic pangenomes with the
Panaroo pipeline.* Genome Biology 21, 180 (2020).
[doi:10.1186/s13059-020-02090-4](https://doi.org/10.1186/s13059-020-02090-4),
PMID: 32698896.

Upstream manual: <https://gtonkinhill.github.io/panaroo/>
