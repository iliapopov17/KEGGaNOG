"""Tests for the KEGGaNOG CLI entry point (kegganog.kegganog.main)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kegganog.kegganog import main, print_citation


def test_print_citation(capsys):
    print_citation()
    captured = capsys.readouterr()
    assert "KEGGaNOG" in captured.err
    assert "doi" in captured.err.lower()


def test_version_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["kegganog", "--version"]):
            main()
    assert exc_info.value.code == 0


def test_missing_input_output_in_cli_mode(capsys):
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["kegganog"]):
            main()
    assert exc_info.value.code != 0


def test_invalid_dpi_exits_one(capsys):
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["kegganog", "-i", "in.tsv", "-o", "out/", "-dpi", "10"]):
            main()
    assert exc_info.value.code == 1
    assert "--dpi" in capsys.readouterr().err


def test_invalid_color_exits_one(capsys):
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["kegganog", "-i", "in.tsv", "-o", "out/", "-c", "Rainbow"]):
            main()
    assert exc_info.value.code == 1
    assert "--color" in capsys.readouterr().err


def test_unsafe_sample_name_exits_one(capsys):
    with pytest.raises(SystemExit) as exc_info:
        with patch(
            "sys.argv", ["kegganog", "-i", "in.tsv", "-o", "out/", "-n", "bad/name"]
        ):
            main()
    assert exc_info.value.code == 1
    assert "--sample_name" in capsys.readouterr().err


def test_web_mode_calls_launch():
    with patch("kegganog.web.launch") as mock_launch:
        with patch("sys.argv", ["kegganog", "--web"]):
            main()
    mock_launch.assert_called_once()


def test_output_dir_already_exists_no_overwrite(tmp_path, capsys):
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    with pytest.raises(FileExistsError):
        with patch("sys.argv", ["kegganog", "-i", "in.tsv", "-o", str(output_dir)]):
            main()


def test_output_dir_overwrite(tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "old_file.txt").write_text("old")

    with patch("sys.argv", ["kegganog", "-i", str(input_file), "-o", str(output_dir), "--overwrite"]):
        with patch("kegganog.kegganog.data_processing.parse_emapper", return_value=str(tmp_path / "parsed.txt")):
            with patch("kegganog.kegganog.data_processing.run_kegg_decoder", return_value=str(tmp_path / "decoder.tsv")):
                with patch("kegganog.kegganog.simple_heatmap.generate_heatmap"):
                    main()

    assert not (output_dir / "old_file.txt").exists()


def test_single_sample_pipeline(tmp_path, capsys):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"

    with patch("sys.argv", ["kegganog", "-i", str(input_file), "-o", str(output_dir)]):
        with patch("kegganog.kegganog.data_processing.parse_emapper", return_value="parsed.txt"):
            with patch("kegganog.kegganog.data_processing.run_kegg_decoder", return_value="decoder.tsv"):
                with patch("kegganog.kegganog.simple_heatmap.generate_heatmap"):
                    main()

    captured = capsys.readouterr()
    assert "heatmap" in captured.out.lower()


def test_single_sample_grouped_pipeline(tmp_path, capsys):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"

    with patch("sys.argv", ["kegganog", "-i", str(input_file), "-o", str(output_dir), "-g"]):
        with patch("kegganog.kegganog.data_processing.parse_emapper", return_value="parsed.txt"):
            with patch("kegganog.kegganog.data_processing.run_kegg_decoder", return_value="decoder.tsv"):
                with patch("kegganog.kegganog.grouped_heatmap.generate_grouped_heatmap"):
                    main()

    assert output_dir.exists()


def test_multi_mode_calls_kegganog_multi(tmp_path):
    input_file = tmp_path / "files.txt"
    input_file.write_text("sample1.tsv\n")
    output_dir = tmp_path / "output"

    with patch("sys.argv", ["kegganog", "-M", "-i", str(input_file), "-o", str(output_dir)]):
        with patch("kegganog.kegganog.kegganog_multi.main") as mock_multi:
            with patch("kegganog.kegganog.data_processing.parse_emapper", return_value="p.txt"):
                with patch("kegganog.kegganog.data_processing.run_kegg_decoder", return_value="d.tsv"):
                    with patch("kegganog.kegganog.simple_heatmap.generate_heatmap"):
                        main()
    mock_multi.assert_called_once()
