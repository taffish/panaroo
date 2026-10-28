#!/bin/sh
set -eu

mode=${1:-}
fixture=/opt/panaroo/share/testdata/panaroo-smoke-fixtures.py

new_tmp() {
    mktemp -d "/tmp/taf-panaroo-${mode}-XXXXXX"
}

finish() {
    code=$?
    trap - 0
    if test "$code" -ne 0 && test -n "${tmp:-}"; then
        find "$tmp" -type f -name '*.log' -exec tail -n 60 {} \; >&2
    fi
    if test -n "${tmp:-}"; then rm -rf "$tmp"; fi
    exit "$code"
}
trap finish 0
trap 'exit 130' 2
trap 'exit 143' 15

case "$mode" in
    resources)
        tmp=$(new_tmp)
        python3 "$fixture" prokka "$tmp/ref"
        mash sketch -k 15 -s 100 -o "$tmp/ref/tiny" "$tmp/ref/prokka-smoke.fna"
        printf '%s\n' 'Synthetic fixture. CC0-1.0.' > "$tmp/LICENSE"
        sha=$(sha256sum "$tmp/ref/tiny.msh" | cut -d ' ' -f 1)
        panaroo-mash-resources prepare --resource-root "$tmp/member" \
            --file "$tmp/ref/tiny.msh" --sha256 "$sha" --id synthetic-v1 \
            --source urn:taffish:synthetic --license-file "$tmp/LICENSE" --rights-reviewed
        panaroo-mash-resources verify --resource-root "$tmp/member"
        ;;
    identity)
        panaroo --version | grep -Fx 'panaroo 1.8.1' >/dev/null
        python3 - <<'PY'
from importlib.metadata import version
import biocode
import dendropy
import edlib
import gffutils
import intbitset
import matplotlib
import networkx
import numba
import numpy
import plotly
import scipy
import sklearn
import panaroo
assert panaroo.__version__ == "1.8.1"
assert version("panaroo") == "1.8.1"
assert version("biocode") == "0.12.1"
assert version("taxadb") == "0.12.1"
PY
        grep -Fx 'panaroo_commit=dbe596c3d24acfe2df1be64f76550b324d167243' /opt/panaroo/share/provenance/source.txt >/dev/null
        grep -Fx 'panaroo_source_sha256=b909740a0e7ab371a871a18467f1eaa61d5d0581117c62f440bd16c16b37c302' /opt/panaroo/share/provenance/source.txt >/dev/null
        grep -Fx 'prokka_source_sha256=f730b5400ea9e507bfe6c5f3d22ce61960a897195c11571c2e1308ce2533faf8' /opt/panaroo/share/provenance/source.txt >/dev/null
        grep -Fx 'muscle_source_sha256=74b22a94e630b16015c2bd9ae83aa2be2c2048d3e41f560b2d4a954725c81968' /opt/panaroo/share/provenance/source.txt >/dev/null
        famsa -h 2>&1 | grep -E 'version 2\.4\.1([ -]|$)' >/dev/null
        muscle -version 2>&1 | grep -F 'muscle 5.3.' >/dev/null
        ;;
    interfaces)
        for command in \
            panaroo run_prokka panaroo-qc panaroo-merge panaroo-plot-abundance \
            panaroo-spydrpick panaroo-img panaroo-fmg panaroo-msa \
            panaroo-gene-neighbourhood panaroo-integrate panaroo-filter-pa \
            panaroo-generate-gffs panaroo-extract-gene \
            panaroo-convert-bakta-to-prokka-gff
        do
            command -v "$command" >/dev/null
            "$command" --help >/dev/null 2>&1
        done
        for command in cd-hit cd-hit-est mafft prank clustalo muscle famsa mash prokka prodigal barrnap minced bash
        do
            command -v "$command" >/dev/null
        done
        python3 - <<'PY'
from panaroo.generate_alignments import check_aligner_install
for aligner in ("mafft", "prank", "clustal", "muscle", "muscle-super5", "famsa"):
    assert check_aligner_install(aligner)
PY
        python3 - <<'PY'
import shutil
import subprocess

for name in ("cd-hit", "cd-hit-est", "mafft", "prank", "clustalo", "muscle",
             "famsa", "mash", "prokka", "prodigal", "barrnap"):
    path = shutil.which(name)
    assert path is not None
    with open(path, "rb") as handle:
        is_elf = handle.read(4) == b"\x7fELF"
    if is_elf:
        result = subprocess.run(["ldd", path], text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        assert "not found" not in result.stdout, (name, result.stdout)
PY
        barrnap --version 2>&1 | grep -E '[0-9]+\.[0-9]+' >/dev/null
        minced --version 2>&1 | grep -F 'minced' >/dev/null
        ;;
    core)
        tmp=$(new_tmp)
        python3 "$fixture" gffs "$tmp/input"
        panaroo -i "$tmp"/input/*.gff -o "$tmp/output" \
            --clean-mode sensitive --remove-invalid-genes --refind-mode off -t 1 \
            >"$tmp/panaroo.log" 2>&1
        test -s "$tmp/output/final_graph.gml"
        test -s "$tmp/output/gene_presence_absence.csv"
        test -s "$tmp/output/gene_data.csv"
        test -s "$tmp/output/struct_presence_absence.Rtab"
        grep -F 'sample_a' "$tmp/output/gene_presence_absence.csv" >/dev/null
        grep -F 'sample_b' "$tmp/output/gene_presence_absence.csv" >/dev/null
        grep -F 'sample_c' "$tmp/output/gene_presence_absence.csv" >/dev/null
        ;;
    aligners)
        tmp=$(new_tmp)
        python3 "$fixture" aligners "$tmp"
        mafft --auto --amino "$tmp/proteins.fa" >"$tmp/mafft.fa" 2>"$tmp/mafft.log"
        clustalo -i "$tmp/proteins.fa" -t Protein --threads 1 -o "$tmp/clustal.fa" --force
        muscle -align "$tmp/proteins.fa" -amino -threads 1 -output "$tmp/muscle.fa" >/dev/null 2>&1
        muscle -super5 "$tmp/proteins.fa" -amino -threads 1 -output "$tmp/muscle-super5.fa" >/dev/null 2>&1
        prank -d="$tmp/proteins.fa" -o="$tmp/prank" -f=8 >/dev/null 2>&1
        famsa -t 1 "$tmp/proteins.fa" "$tmp/famsa.fa" >/dev/null 2>&1
        for output in "$tmp/mafft.fa" "$tmp/clustal.fa" "$tmp/muscle.fa" "$tmp/muscle-super5.fa" "$tmp/prank.best.fas" "$tmp/famsa.fa"
        do
            test "$(grep -c '^>' "$output")" -eq 3
        done
        ;;
    formats)
        tmp=$(new_tmp)
        python3 "$fixture" formats "$tmp"
        python3 - "$tmp/sample.gbk" "$tmp/from-genbank.gff" <<'PY'
import sys
from panaroo.biocode_convert import convert_gbk_gff3
convert_gbk_gff3(sys.argv[1], sys.argv[2], True)
PY
        panaroo-convert-bakta-to-prokka-gff \
            --gff "$tmp/sample-bakta.gff3" --out "$tmp/from-bakta.gff"
        for output in "$tmp/from-genbank.gff" "$tmp/from-bakta.gff"
        do
            test -s "$output"
            grep -Fx '##gff-version 3' "$output" >/dev/null
            grep -Fx '##FASTA' "$output" >/dev/null
            grep -F 'CDS' "$output" >/dev/null
        done
        ;;
    qc)
        tmp=$(new_tmp)
        python3 "$fixture" gffs "$tmp/input"
        mkdir "$tmp/output"
        panaroo-qc -i "$tmp"/input/*.gff -o "$tmp/output" \
            --graph_type all --random_seed 1 -t 1 >"$tmp/qc.log" 2>&1
        for output in \
            MDS_mash_plot.html MDS_mash_plot.png mds_coords.txt mash_dist.txt \
            ngenes_boxplot.html ngenes_barplot.png ngenes.txt \
            ncontigs_boxplot.html ncontigs_barplot.png ncontigs.txt
        do
            test -s "$tmp/output/$output"
        done
        python3 - "$tmp/output" <<'PY'
from pathlib import Path
import re
import sys
root = Path(sys.argv[1])
for name in ("MDS_mash_plot.html", "ngenes_boxplot.html", "ncontigs_boxplot.html"):
    text = (root / name).read_text(errors="replace")
    assert "Plotly.newPlot" in text
    assert not re.search(r"<script[^>]+src=[\"']https?://", text, re.I)
for name in ("MDS_mash_plot.png", "ngenes_barplot.png", "ncontigs_barplot.png"):
    assert (root / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
PY
        ;;
    prokka)
        tmp=$(new_tmp)
        python3 "$fixture" prokka "$tmp/input"
        # Exercise the retained headless Java runtime, not only MinCED's banner.
        minced "$tmp/input/prokka-smoke.fna" "$tmp/minced.txt" >"$tmp/minced.log" 2>&1
        test -f "$tmp/minced.txt"
        mkdir "$tmp/output"
        if ! run_prokka -i "$tmp/input/prokka-smoke.fna" -o "$tmp/output" \
            --num_training 1 --force -t 1 >"$tmp/run-prokka.log" 2>&1
        then
            cat "$tmp/run-prokka.log" >&2
            find "$tmp/output" -type f -name '*prokka.log' \
                -exec sh -c 'for log do cat "$log" >&2; done' sh {} +
            exit 1
        fi
        test -s "$tmp/output/prokka-smoke/prokka-smoke.gff"
        grep -F '##FASTA' "$tmp/output/prokka-smoke/prokka-smoke.gff" >/dev/null
        grep -F "Looking for 'barrnap' - found" "$tmp/output/prokka-smoke_prokka.log" >/dev/null
        grep -F "Looking for 'minced' - found" "$tmp/output/prokka-smoke_prokka.log" >/dev/null
        grep -F 'Annotation finished successfully.' "$tmp/output/prokka-smoke_prokka.log" >/dev/null
        ;;
    *)
        echo "usage: panaroo-smoke {identity|interfaces|core|aligners|formats|qc|prokka|resources}" >&2
        exit 2
        ;;
esac
