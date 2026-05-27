"""Tests for the KEGGaNOG CLI entry point (kegganog.kegganog)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from kegganog.kegganog import app, print_citation

runner = CliRunner()


# ---------------------------------------------------------------------------
# print_citation
# ---------------------------------------------------------------------------


def test_print_citation(capsys):
    print_citation()
    captured = capsys.readouterr()
    assert "KEGGaNOG" in captured.out
    assert "doi" in captured.out.lower()


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------


def test_version_exits_zero():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "KEGGaNOG" in result.output


# ---------------------------------------------------------------------------
# Missing --input / --output
# ---------------------------------------------------------------------------


def test_missing_input_output_in_cli_mode():
    result = runner.invoke(app, [])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


def test_invalid_dpi_exits_one():
    result = runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-dpi", "10"])
    assert result.exit_code == 1
    assert "--dpi" in result.output or "--dpi" in (result.stderr or "")


def test_invalid_color_exits_one():
    result = runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-c", "Rainbow"])
    assert result.exit_code == 1
    assert "--color" in result.output or "--color" in (result.stderr or "")


def test_unsafe_sample_name_exits_one():
    result = runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-n", "bad/name"])
    assert result.exit_code == 1
    assert "--sample_name" in result.output or "--sample_name" in (result.stderr or "")


# ---------------------------------------------------------------------------
# --web
# ---------------------------------------------------------------------------


def test_web_mode_calls_launch():
    with patch("kegganog.web.launch") as mock_launch:
        result = runner.invoke(app, ["--web"])
    mock_launch.assert_called_once()


# ---------------------------------------------------------------------------
# Output directory handling
# ---------------------------------------------------------------------------


def test_output_dir_already_exists_no_overwrite(tmp_path):
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    result = runner.invoke(app, ["-i", "in.tsv", "-o", str(output_dir)])
    assert result.exit_code == 1
    assert "already exists" in result.output or "already exists" in (
        result.stderr or ""
    )


def test_output_dir_overwrite(tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "old_file.txt").write_text("old")

    with patch("kegganog.kegganog.run_single") as mock_run:
        mock_run.return_value = None
        result = runner.invoke(
            app,
            ["-i", str(input_file), "-o", str(output_dir), "--overwrite"],
        )

    assert not (output_dir / "old_file.txt").exists()


# ---------------------------------------------------------------------------
# Single-sample pipeline
# ---------------------------------------------------------------------------


def test_single_sample_pipeline(tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"

    with patch("kegganog.kegganog.run_single") as mock_run:
        mock_run.return_value = None
        result = runner.invoke(
            app,
            ["-i", str(input_file), "-o", str(output_dir)],
        )

    mock_run.assert_called_once()


def test_single_sample_grouped_pipeline(tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"

    with patch("kegganog.kegganog.run_single") as mock_run:
        mock_run.return_value = None
        result = runner.invoke(
            app,
            ["-i", str(input_file), "-o", str(output_dir), "-g"],
        )

    mock_run.assert_called_once()
    assert output_dir.exists()


# ---------------------------------------------------------------------------
# Multi-sample pipeline
# ---------------------------------------------------------------------------


def test_multi_mode_calls_runner(tmp_path):
    input_file = tmp_path / "files.txt"
    input_file.write_text("sample1.tsv\n")
    output_dir = tmp_path / "output"

    with patch("kegganog.kegganog_multi.MultiSampleRunner.run") as mock_run:
        mock_run.return_value = None
        result = runner.invoke(
            app,
            ["-M", "-i", str(input_file), "-o", str(output_dir)],
        )

    mock_run.assert_called_once()


# ---------------------------------------------------------------------------
# MultiSampleRunner
# ---------------------------------------------------------------------------


def test_multisample_runner_collect_single_path(tmp_path):
    from kegganog.kegganog_multi import MultiSampleRunner

    f = tmp_path / "sample.annotations"
    f.write_bytes(b"x")
    runner_obj = MultiSampleRunner(input_path=str(f), output_dir=str(tmp_path))
    paths = runner_obj._collect_input_paths()
    assert paths == [str(f)]


def test_multisample_runner_collect_from_txt(tmp_path):
    from kegganog.kegganog_multi import MultiSampleRunner

    f1 = tmp_path / "s1.annotations"
    f2 = tmp_path / "s2.annotations"
    f1.write_bytes(b"x")
    f2.write_bytes(b"x")

    txt = tmp_path / "list.txt"
    txt.write_text(f"{f1}\n{f2}\n")

    runner_obj = MultiSampleRunner(input_path=str(txt), output_dir=str(tmp_path))
    paths = runner_obj._collect_input_paths()
    assert str(f1) in paths
    assert str(f2) in paths


def test_multisample_runner_load_files_skips_missing(tmp_path, caplog):
    import logging

    from kegganog.kegganog_multi import MultiSampleRunner

    runner_obj = MultiSampleRunner(
        input_path=str(tmp_path / "nonexistent.annotations"),
        output_dir=str(tmp_path),
    )
    with caplog.at_level(logging.WARNING):
        files = runner_obj._load_files()

    assert files == []
    assert "does not exist" in caplog.text


def test_multisample_runner_load_files_reads_bytes(tmp_path):
    from kegganog.kegganog_multi import MultiSampleRunner

    f = tmp_path / "sample.annotations"
    f.write_bytes(b"content")

    runner_obj = MultiSampleRunner(input_path=str(f), output_dir=str(tmp_path))
    files = runner_obj._load_files()

    assert len(files) == 1
    assert files[0] == ("sample.annotations", b"content")


def test_multisample_runner_run_calls_pipeline(tmp_path):
    from kegganog.kegganog_multi import MultiSampleRunner
    from kegganog.processing.pipeline import PipelineResult

    f = tmp_path / "sample.annotations"
    f.write_bytes(b"x")

    fake_result = PipelineResult(
        zip_path="z",
        png_path="p",
        tsv_path="t",
        samples=["sample"],
        pathways=["glycolysis"],
    )

    runner_obj = MultiSampleRunner(input_path=str(f), output_dir=str(tmp_path))

    with patch("kegganog.kegganog_multi.run_multi", return_value=fake_result) as mock:
        result = runner_obj.run()

    mock.assert_called_once()
    assert result is fake_result


def test_entry_point_keyboard_interrupt(capsys):
    from kegganog.kegganog import entry_point

    with patch("kegganog.kegganog.app") as mock_app:
        mock_app.side_effect = KeyboardInterrupt
        with pytest.raises(SystemExit) as exc_info:
            entry_point()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "interrupted" in captured.err.lower()
