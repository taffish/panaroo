Panaroo 1.8.0 - bacterial pangenome analysis
TAFFISH package: panaroo 1.8.0-r1

Usage:
  taf-panaroo [PANAROO_OPTIONS...]
  taf-panaroo -- [PANAROO_OPTIONS...]
  taf-panaroo COMMAND [COMMAND_OPTIONS...]

Wrapper options:
  -h, --help       Show this installed-app guide
  -v, --version    Show the TAFFISH package version
  --compile        Print generated shell code instead of running it
  --               Pass option-leading arguments to Panaroo

Show upstream help and version:
  taf-panaroo -- --help
  taf-panaroo -- --version

Main input:
  Panaroo normally reads two or more Prokka-style GFF3 files. Each file must
  contain annotations followed by an ##FASTA section. GenBank files and list
  files are also supported by Panaroo's upstream input parser.

Basic analysis:
  taf-panaroo -i isolate1.gff isolate2.gff isolate3.gff \
    -o panaroo-results --clean-mode strict -t 8

Core-gene alignment:
  taf-panaroo -i *.gff -o panaroo-results --clean-mode strict \
    --alignment core --aligner mafft -t 8

Inputs and outputs should be under the current working tree so the container
can see them. Panaroo creates the main output directory; avoid reusing a
nonempty result directory unless the selected upstream command permits it.

Packaged Panaroo commands:
  panaroo                    Main pangenome pipeline
  panaroo-qc                 Pre-run QC tables, PNGs, and interactive HTML
  run_prokka                 Re-run Prokka with Panaroo-trained Prodigal
  panaroo-merge              Merge Panaroo graphs
  panaroo-msa                Generate alignments after a Panaroo run
  panaroo-integrate          Integrate additional genomes
  panaroo-filter-pa          Filter presence/absence matrices
  panaroo-generate-gffs      Generate post-run GFF outputs
  panaroo-extract-gene       Extract gene FASTA sequences

Additional installed interfaces include panaroo-plot-abundance,
panaroo-spydrpick, panaroo-img, panaroo-fmg,
panaroo-gene-neighbourhood, and the Bakta converter.

Run a secondary command through automatic command mode:
  taf-panaroo panaroo-qc --help
  taf-panaroo panaroo-merge --help
  taf-panaroo run_prokka --help

Convert a Bakta combined GFF3 file:
  taf-panaroo panaroo-convert-bakta-to-prokka-gff \
    --gff bakta.gff3 --out prokka-style.gff

Generate QC reports:
  mkdir -p panaroo-qc
  taf-panaroo panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
    -o panaroo-qc --graph_type all -t 4

panaroo-qc requires its output directory to exist. It writes self-contained
Plotly HTML files and PNG images; open the HTML files directly on the host.
There is no web server, port, login, noVNC session, or bundled browser.

External tools included for supported paths:
  CD-HIT/CD-HIT-EST, Mash, Prokka, Prodigal, MAFFT, PRANK, Clustal Omega,
  MUSCLE 5, and FAMSA 2.4.1. MAFFT remains required by some profile/codon
  alignment paths even when another aligner is selected.

  The complete Prokka 1.14.6 database is already indexed in the image; users
  do not need to download or initialize it before running run_prokka. Barrnap
  and MinCED annotation paths are included. SignalP and RNAmmer are not bundled
  because their upstream distribution terms require separate authorization.

Boundaries:
  --ref_db for contamination QC is user-supplied; no database is downloaded.
  Large cohorts and whole-pangenome alignments can require substantial RAM,
  disk, and time. Set -t according to resources available to the container.
  Scientific interpretation and production-data validation remain the user's
  responsibility; bundled smoke tests exercise only small synthetic inputs.

Upstream documentation:
  https://gtonkinhill.github.io/panaroo/
