import pathlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kegganog.processing import data_processing
from kegganog.processing.data_processing import _ensure_kegg_decoder


def test_parse_emapper_filters_and_formats_kegg_ko(tmp_path):
    input_file = tmp_path / "emapper.tsv"
    temp_folder = tmp_path / "temp"
    temp_folder.mkdir()

    input_file.write_text(
        "\n".join(
            [
                "## header line 1",
                "## header line 2",
                "## header line 3",
                "## header line 4",
                "KEGG_ko\tOther",
                "ko:K00001,ko:K00002\tX",
                "-\tY",
                "ko:K00003\tZ",
            ]
        )
        + "\n"
    )

    output_path = data_processing.parse_emapper(str(input_file), str(temp_folder))

    content = pathlib.Path(output_path).read_text().strip().splitlines()
    assert content == ["SAMPLE K00001", "SAMPLE K00002", "SAMPLE K00003"]


# ---------------------------------------------------------------------------
# _ensure_kegg_decoder
# ---------------------------------------------------------------------------


def test_ensure_kegg_decoder_existing_file_no_download(tmp_path):
    script_path = tmp_path / "KEGG_decoder.py"
    script_path.write_text("# fake")

    with patch("requests.get") as mock_get:
        _ensure_kegg_decoder(script_path)

    mock_get.assert_not_called()
    assert script_path.exists()


def test_ensure_kegg_decoder_downloads_when_missing(tmp_path):
    script_path = tmp_path / "KEGG_decoder.py"

    mock_response = MagicMock()
    mock_response.content = b"# fake kegg decoder"
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response) as mock_get:
        _ensure_kegg_decoder(script_path)

    mock_get.assert_called_once()
    assert script_path.exists()
    assert script_path.read_bytes() == b"# fake kegg decoder"


def test_ensure_kegg_decoder_raises_on_download_failure(tmp_path):
    script_path = tmp_path / "KEGG_decoder.py"

    with patch("requests.get", side_effect=Exception("network error")):
        with pytest.raises(RuntimeError, match="Failed to download"):
            _ensure_kegg_decoder(script_path)

    assert not script_path.exists()


# ---------------------------------------------------------------------------
# run_kegg_decoder
# ---------------------------------------------------------------------------


def test_run_kegg_decoder_replaces_sample_name(tmp_path):
    input_file = tmp_path / "ko_terms.txt"
    input_file.write_text("SAMPLE K00001\n")
    sample_name = "MySample"

    output_file = tmp_path / f"{sample_name}_pathways.tsv"
    output_file.write_text("SAMPLE\tglycoly\tTCA Cycle\nSAMPLE\t0.5\t0.7\n")

    with patch("kegganog.processing.data_processing._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing.run_kegg_decoder(
                str(input_file), str(tmp_path), sample_name
            )

    content = Path(result).read_text()
    assert "MySample" in content
    assert "SAMPLE" not in content


def test_run_kegg_decoder_capitalizes_lowercase_pathway_headers(tmp_path):
    input_file = tmp_path / "ko_terms.txt"
    input_file.write_text("SAMPLE K00001\n")
    sample_name = "S1"

    output_file = tmp_path / f"{sample_name}_pathways.tsv"
    output_file.write_text("SAMPLE\tglycoly\tTCA Cycle\nSAMPLE\t0.5\t0.7\n")

    with patch("kegganog.processing.data_processing._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing.run_kegg_decoder(
                str(input_file), str(tmp_path), sample_name
            )

    content = Path(result).read_text()
    # "glycoly" is all-lowercase → capitalize() → "Glycoly"
    assert "Glycoly" in content
    # "TCA Cycle" is mixed-case → islower() is False → unchanged
    assert "TCA Cycle" in content


def test_run_kegg_decoder_returns_correct_path(tmp_path):
    input_file = tmp_path / "ko_terms.txt"
    input_file.write_text("SAMPLE K00001\n")
    sample_name = "TestSample"

    output_file = tmp_path / f"{sample_name}_pathways.tsv"
    output_file.write_text("SAMPLE\tpathway\nSAMPLE\t1.0\n")

    with patch("kegganog.processing.data_processing._ensure_kegg_decoder"):
        with patch("subprocess.run"):
            result = data_processing.run_kegg_decoder(
                str(input_file), str(tmp_path), sample_name
            )

    assert result == str(output_file)
