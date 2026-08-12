#!/usr/bin/env python3
"""Generate deterministic, tiny Panaroo runtime fixtures."""

from pathlib import Path
import random
import sys

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord


def write_prokka_gff(path: Path, sample: str, seed: int) -> None:
    random.seed(seed)
    length = 9000
    sequence = [random.choice("ACGT") for _ in range(length)]
    starts = [301, 1801, 3301, 4801, 6301]
    codons = ["GCT", "GGT", "CTG", "AAA", "TTC"]
    lines = ["##gff-version 3", f"##sequence-region {sample}_contig 1 {length}"]
    for index, (start, codon) in enumerate(zip(starts, codons), 1):
        cds = "ATG" + codon * 98 + "TAA"
        end = start + len(cds) - 1
        sequence[start - 1 : end] = cds
        locus = f"{sample}_{index:04d}"
        lines.append(
            "\t".join(
                [
                    f"{sample}_contig",
                    "Prodigal:2.6.3",
                    "CDS",
                    str(start),
                    str(end),
                    ".",
                    "+",
                    "0",
                    f"ID={locus};locus_tag={locus};gene=gene{index};product=smoke protein {index}",
                ]
            )
        )
    lines.extend(["##FASTA", f">{sample}_contig"])
    seq = "".join(sequence)
    lines.extend(seq[i : i + 70] for i in range(0, len(seq), 70))
    path.write_text("\n".join(lines) + "\n")


def write_genbank(path: Path) -> None:
    seq = Seq("A" * 300 + "ATG" + "GCT" * 98 + "TAA" + "C" * 300)
    record = SeqRecord(seq, id="SMOKE_GBK", name="SMOKE_GBK", description="Panaroo smoke")
    record.annotations["molecule_type"] = "DNA"
    record.annotations["topology"] = "linear"
    gene_location = FeatureLocation(300, 600, strand=1)
    record.features = [
        SeqFeature(FeatureLocation(0, len(seq), strand=1), type="source"),
        SeqFeature(gene_location, type="gene", qualifiers={"locus_tag": ["GBK_0001"]}),
        SeqFeature(
            gene_location,
            type="CDS",
            qualifiers={
                "locus_tag": ["GBK_0001"],
                "gene": ["smoke"],
                "product": ["smoke protein"],
                "translation": ["M" + "A" * 98],
            },
        ),
    ]
    SeqIO.write(record, path, "genbank")


def write_bakta(path: Path) -> None:
    cds = "ATG" + "GGT" * 98 + "TAA"
    seq = "A" * 300 + cds + "C" * 300
    path.write_text(
        "##gff-version 3\n"
        "# Bakta smoke annotation\n"
        f"##sequence-region SMOKE_BAKTA 1 {len(seq)}\n"
        "SMOKE_BAKTA\tBakta\tCDS\t301\t600\t.\t+\t0\t"
        "ID=SMOKE_BAKTA_0001;Name=smoke;product=smoke protein\n"
        "##FASTA\n"
        "# Bakta FASTA preamble\n"
        ">SMOKE_BAKTA\n"
        + "\n".join(seq[i : i + 70] for i in range(0, len(seq), 70))
        + "\n"
    )


def write_alignments(root: Path) -> None:
    (root / "proteins.fa").write_text(
        ">protein_a\nMKTAYIAKQRQISFVKSHFSRQDILDLWIYHTQGYFP\n"
        ">protein_b\nMKTAYIAKQRQISFVKSHFSRQDILDLWVYHTQGYFP\n"
        ">protein_c\nMKTAYIAKQRQISFVKSHFSRQNILDLWIYHTQGYFP\n"
    )


def write_prokka_fasta(path: Path) -> None:
    random.seed(104729)
    seq = [random.choice("ACGT") for _ in range(120000)]
    for start, codon in [(3000, "GCT"), (30000, "GGT"), (60000, "CTG"), (90000, "AAA")]:
        cds = "ATG" + codon * 398 + "TAA"
        seq[start : start + len(cds)] = cds
    sequence = "".join(seq)
    path.write_text(">panaroo_prokka_smoke\n" + "\n".join(sequence[i : i + 70] for i in range(0, len(sequence), 70)) + "\n")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: panaroo-smoke-fixtures.py MODE OUTDIR")
    mode, outdir = sys.argv[1:]
    root = Path(outdir)
    root.mkdir(parents=True, exist_ok=True)
    if mode in {"gffs", "all"}:
        for index, sample in enumerate(("sample_a", "sample_b", "sample_c"), 1):
            write_prokka_gff(root / f"{sample}.gff", sample, 1000 + index)
    if mode in {"formats", "all"}:
        write_genbank(root / "sample.gbk")
        write_bakta(root / "sample-bakta.gff3")
    if mode in {"aligners", "all"}:
        write_alignments(root)
    if mode in {"prokka", "all"}:
        write_prokka_fasta(root / "prokka-smoke.fna")


if __name__ == "__main__":
    main()
