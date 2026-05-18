"""Tests for kegganog.processing.data_processing_multi."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from kegganog.processing import data_processing_multi


def _write_emapper_file(path: Path, ko_entries: list[str]) -> None:
    lines = [
        "## header line 1",
        "## header line 2",
        "## header line 3",
        "## header line 4",
        "KEGG_ko\tOther",
    ]
    lines.extend(ko_entries)
    path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# parse_emapper (multi)
# ---------------------------------------------------------------------------


def test_parse_emapper_multi_formats_with_prefix(tmp_path):
    input_file = tmp_path / "sample.tsv"
    sample_folder = tmp_path / "sample_folder"
    sample_folder.mkdir()

    _write_emapper_file(
        input_file,
        ["ko:K00001,ko:K00002\tX", "-\tY", "ko:K00003\tZ"],
    )

    output_path = data_processing_multi.parse_emapper(
        str(input_file), str(sample_folder), "Sample1"
    )

    content = Path(output_path).read_text().strip().splitlines()
    assert content == ["Sample1 K00001", "Sample1 K00002", "Sample1 K00003"]


def test_parse_emapper_multi_output_file_named_with_prefix(tmp_path):
    input_file = tmp_path / "s.tsv"
    sample_folder = tmp_path / "folder"
    sample_folder.mkdir()

    _write_emapper_file(input_file, ["ko:K00001\tX"])

    output_path = data_processing_multi.parse_emapper(
        str(input_file), str(sample_folder), "SampleABC"
    )

    assert os.path.basename(output_path) == "SampleABC_parsed_KO_terms.txt"


def test_parse_emapper_multi_missing_kegg_ko_raises(tmp_path):
    input_file = tmp_path / "bad.tsv"
    sample_folder = tmp_path / "folder"
    sample_folder.mkdir()

    input_file.write_text("## header\nOtherCol\tAnotherCol\nval1\tval2\n")

    with pytest.raises(KeyError, match="KEGG_ko"):
        data_processing_multi.parse_emapper(str(input_file), str(sample_folder), "S1")


def test_parse_emapper_multi_skips_dash_entries(tmp_path):
    input_file = tmp_path / "s.tsv"
    sample_folder = tmp_path / "folder"
    sample_folder.mkdir()

    _write_emapper_file(input_file, ["-\tX", "-\tY"])

    output_path = data_processing_multi.parse_emapper(
        str(input_file), str(sample_folder), "S1"
    )

    content = Path(output_path).read_text().strip()
    assert content == ""


# ---------------------------------------------------------------------------
# run_kegg_decoder (multi)
# ---------------------------------------------------------------------------


def test_run_kegg_decoder_multi_replaces_sample_with_prefix(tmp_path):
    input_file = tmp_path / "ko_terms.txt"
    input_file.write_text("Sample1 K00001\n")
    file_prefix = "Sample1"

    output_file = tmp_path / f"{file_prefix}_pathways.tsv"
    output_file.write_text("SAMPLE\tglycoly\nSAMPLE\t0.5\n")

    with patch("kegganog.processing.data_processing_multi._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing_multi.run_kegg_decoder(
                str(input_file), str(tmp_path), file_prefix
            )

    content = Path(result).read_text()
    assert "Sample1" in content
    assert "SAMPLE" not in content


def test_run_kegg_decoder_multi_capitalizes_lowercase_headers(tmp_path):
    input_file = tmp_path / "ko_terms.txt"
    input_file.write_text("S2 K00001\n")
    file_prefix = "S2"

    output_file = tmp_path / f"{file_prefix}_pathways.tsv"
    output_file.write_text("SAMPLE\tglycoly\tTCA Cycle\nSAMPLE\t0.4\t0.9\n")

    with patch("kegganog.processing.data_processing_multi._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing_multi.run_kegg_decoder(
                str(input_file), str(tmp_path), file_prefix
            )

    content = Path(result).read_text()
    assert "Glycoly" in content
    assert "TCA Cycle" in content


def test_run_kegg_decoder_multi_returns_correct_path(tmp_path):
    input_file = tmp_path / "ko.txt"
    input_file.write_text("X K00001\n")
    file_prefix = "MyPrefix"

    output_file = tmp_path / f"{file_prefix}_pathways.tsv"
    output_file.write_text("SAMPLE\tpathway\nSAMPLE\t1.0\n")

    with patch("kegganog.processing.data_processing_multi._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing_multi.run_kegg_decoder(
                str(input_file), str(tmp_path), file_prefix
            )

    assert result == str(output_file)


# ---------------------------------------------------------------------------
# merge_outputs
# ---------------------------------------------------------------------------


def _write_pathways_tsv(path: Path, prefix: str, values: list[float]) -> None:
    """Write a minimal KEGG-Decoder-style pathways TSV."""
    headers = "\t".join(["Glycolysis", "TCA Cycle"])
    vals = "\t".join(str(v) for v in values)
    path.write_text(f"{prefix}\t{headers}\n{prefix}\t{vals}\n")


def test_merge_outputs_returns_empty_df_when_no_files(tmp_path):
    result = data_processing_multi.merge_outputs(str(tmp_path))
    assert result.empty


def test_merge_outputs_creates_merged_file(tmp_path):
    temp_files_dir = tmp_path / "temp_files"
    for prefix in ["S1", "S2"]:
        sample_dir = temp_files_dir / prefix
        sample_dir.mkdir(parents=True)
        _write_pathways_tsv(sample_dir / f"{prefix}_pathways.tsv", prefix, [0.5, 0.7])

    data_processing_multi.merge_outputs(str(tmp_path))

    merged_file = tmp_path / "merged_pathways.tsv"
    assert merged_file.exists()


def test_merge_outputs_merges_two_samples(tmp_path):
    temp_files_dir = tmp_path / "temp_files"

    s1_dir = temp_files_dir / "S1"
    s1_dir.mkdir(parents=True)
    _write_pathways_tsv(s1_dir / "S1_pathways.tsv", "S1", [0.5, 0.7])

    s2_dir = temp_files_dir / "S2"
    s2_dir.mkdir(parents=True)
    _write_pathways_tsv(s2_dir / "S2_pathways.tsv", "S2", [0.3, 0.8])

    result = data_processing_multi.merge_outputs(str(tmp_path))

    assert "Function" in result.columns
    assert "S1" in result.columns
    assert "S2" in result.columns
    assert "Glycolysis" in result["Function"].values
    assert "TCA Cycle" in result["Function"].values


def test_merge_outputs_single_sample(tmp_path):
    temp_files_dir = tmp_path / "temp_files" / "OnlySample"
    temp_files_dir.mkdir(parents=True)
    _write_pathways_tsv(
        temp_files_dir / "OnlySample_pathways.tsv", "OnlySample", [1.0, 0.0]
    )

    result = data_processing_multi.merge_outputs(str(tmp_path))

    assert "OnlySample" in result.columns
    assert len(result) == 2
