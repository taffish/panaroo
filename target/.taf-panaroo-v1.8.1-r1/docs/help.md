Panaroo 1.8.1 - bacterial pangenome analysis
TAFFISH package: panaroo 1.8.1-r1

Usage:
  taf-panaroo [PANAROO_OPTIONS...]
  taf-panaroo -- [PANAROO_OPTIONS...]
  taf-panaroo COMMAND [COMMAND_OPTIONS...]
  taf-panaroo --help                 Installed-app help
  taf-panaroo --version              Package version
  taf-panaroo -- --help              Upstream help
  taf-panaroo -- --version           Upstream version

Build a pangenome from combined Prokka-style GFF3+FASTA inputs:
  taf-panaroo -i isolate1.gff isolate2.gff isolate3.gff \
    -o panaroo-results --clean-mode strict -t 8
  taf-panaroo -i *.gff -o aligned --clean-mode strict \
    --alignment core --aligner mafft -t 8
Keep inputs/outputs under the working directory, or bind external directories.
For a path containing spaces, preserve inner quotes through command mode:
  taf-panaroo panaroo-convert-bakta-to-prokka-gff \
    --gff '"input file.gff3"' --out '"converted file.gff"'

Secondary commands:
  taf-panaroo panaroo-merge --help
  taf-panaroo run_prokka --help
  taf-panaroo panaroo-msa --help
The complete Prokka database is already indexed; no setup is needed.

Create offline QC reports (the output directory must already exist):
  mkdir -p qc
  taf-panaroo panaroo-qc -i isolate1.gff isolate2.gff isolate3.gff \
    -o qc --graph_type all --random_seed 1 -t 4
Open qc/*.html directly on the host; no server is needed for these reports.
Use a QC output path without spaces or shell metacharacters, including parents.
Inner quotes cannot fix the upstream QC command's internal Mash shell parsing.

Optional Mash reference: import a local authorized sketch, never auto-download.
  mkdir -p shared
  taf-panaroo panaroo-mash-resources prepare --resource-root shared/mash \
    --file reference.msh --sha256 ACTUAL_SHA256 --id YOUR_VERSION \
    --source urn:your-source:version --license-file LICENSE \
    --rights-reviewed --access public --dry-run
Review the plan, then repeat without --dry-run. The parent must already exist.
Use --access personal for private data; public requires permission to share.
Existing complete resources are reused; conflicting/broken resources are never
overwritten. Restore the original bytes or choose a new versioned path.
Keep any linked .NAME.payload.* directory: it is permanent resource storage.

Select a prepared member (host path); it mounts read-only at /panaroo-mash:
  export TAFFISH_PANAROO_DB_PATH="$PWD/shared/mash"
  taf-panaroo panaroo-qc -i *.gff -o qc --ref_db /panaroo-mash/reference.msh
Discovery order: explicit DB_PATH, ~/.local/share/taffish/databases/panaroo/mash,
/usr/local/share/taffish/databases/panaroo/mash, /opt/taffish/databases/panaroo/mash.
Set TAFFISH_PANAROO_DB_AUTO_MOUNT=0 during setup or for manual binds.
Automatic verification needs host Python 3. Invalid roots fail explicitly.
An administrator can prepare once with public access and searchable parents;
ordinary users reuse the verified system member without downloading again.
Manual read-only fallback: disable discovery, then choose one backend below.
  export TAFFISH_PANAROO_DB_AUTO_MOUNT=0
Docker:
  export TAFFISH_CONTAINER_BACKEND=docker
  export TAFFISH_DOCKER_RUN_ARGS="--volume \"$PWD/shared/mash:/panaroo-mash:ro\""
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
Podman:
  export TAFFISH_CONTAINER_BACKEND=podman
  export TAFFISH_PODMAN_RUN_ARGS="--volume \"$PWD/shared/mash:/panaroo-mash:ro\""
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
Apptainer:
  export TAFFISH_CONTAINER_BACKEND=apptainer
  export TAFFISH_APPTAINER_RUN_ARGS="--bind \"$PWD/shared/mash:/panaroo-mash:ro\""
  taf-panaroo panaroo-mash-resources verify --resource-root /panaroo-mash
After verification, use panaroo-qc --ref_db /panaroo-mash/reference.msh as above.

Optional graph browsing requires the separate Cytoscape app:
  Panaroo writes panaroo-results/final_graph.gml; it does not start a desktop.
  taf-cytoscape --help
Use that app's launch commands with --network panaroo-results/final_graph.gml.
For a command-mode path with spaces, use --network '"results with spaces/final_graph.gml"'.
Cytoscape is not needed for Panaroo analysis or the offline QC reports.

Troubleshooting:
  taf-panaroo panaroo-mash-resources --help
Keep existing results/resources when retrying; do not delete unknown lock files.
Upstream manual: https://gtonkinhill.github.io/panaroo/
