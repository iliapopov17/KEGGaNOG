"""Tests for the KEGGaNOG CLI entry point (kegganog.kegganog).

Sections
--------
1. print_citation        — stdout contains expected DOI reference.
2. --version             — exits 0, prints version string.
3. Validation errors     — bad dpi, bad color, unsafe sample name.
4. --web mode            — delegates to kegganog.web.launch.
5. Output directory      — overwrite protection and cleanup on --overwrite.
6. Single-sample mode    — run_single is called once with correct args.
7. Multi-sample mode     — MultiSampleRunner.run is called once.
8. MultiSampleRunner     — _collect_input_paths, _load_files, .run contract.
9. entry_point           — KeyboardInterrupt handled gracefully.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from kegganog.kegganog import app, print_citation

# ===========================================================================
# 1. print_citation
# ===========================================================================


def test_print_citation_contains_doi(capsys):
    print_citation()
    out = capsys.readouterr().out
    assert "KEGGaNOG" in out
    assert "doi" in out.lower()


# ===========================================================================
# 2. --version
# ===========================================================================


def test_version_exits_zero(cli_runner):
    result = cli_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "KEGGaNOG" in result.output


# ===========================================================================
# 3. Validation errors
# ===========================================================================


def test_no_args_exits_nonzero(cli_runner):
    assert cli_runner.invoke(app, []).exit_code != 0


def test_invalid_dpi_exits_one(cli_runner):
    result = cli_runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-dpi", "10"])
    assert result.exit_code == 1
    assert "--dpi" in result.output or "--dpi" in (result.stderr or "")


def test_invalid_color_exits_two(cli_runner):
    result = cli_runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-c", "Rainbow"])
    assert result.exit_code == 2


def test_unsafe_sample_name_exits_one(cli_runner):
    result = cli_runner.invoke(app, ["-i", "in.tsv", "-o", "out/", "-n", "bad/name"])
    assert result.exit_code == 1
    assert "--sample_name" in result.output or "--sample_name" in (result.stderr or "")


# ===========================================================================
# 4. --web mode
# ===========================================================================


def test_web_mode_calls_launch(cli_runner):
    with patch("kegganog.web.launch") as mock_launch:
        cli_runner.invoke(app, ["--web"])
    mock_launch.assert_called_once()


# ===========================================================================
# 5. Output directory
# ===========================================================================


def test_output_dir_already_exists_without_overwrite_exits_one(cli_runner, tmp_path):
    output_dir = tmp_path / "existing"
    output_dir.mkdir()
    result = cli_runner.invoke(app, ["-i", "in.tsv", "-o", str(output_dir)])
    assert result.exit_code == 1
    assert "already exists" in result.output or "already exists" in (
        result.stderr or ""
    )


def test_output_dir_overwrite_clears_old_contents(cli_runner, tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "old_file.txt").write_text("old")

    with patch("kegganog.kegganog.run_single", return_value=None):
        cli_runner.invoke(
            app, ["-i", str(input_file), "-o", str(output_dir), "--overwrite"]
        )

    assert not (output_dir / "old_file.txt").exists()


# ===========================================================================
# 6. Single-sample mode
# ===========================================================================


def test_single_sample_calls_run_single_once(cli_runner, tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")

    with patch("kegganog.kegganog.run_single", return_value=None) as mock_run:
        cli_runner.invoke(app, ["-i", str(input_file), "-o", str(tmp_path / "output")])

    mock_run.assert_called_once()


def test_single_sample_grouped_creates_output_dir(cli_runner, tmp_path):
    input_file = tmp_path / "sample.emapper.annotations"
    input_file.write_text("dummy")
    output_dir = tmp_path / "output"

    with patch("kegganog.kegganog.run_single", return_value=None):
        cli_runner.invoke(app, ["-i", str(input_file), "-o", str(output_dir), "-g"])

    assert output_dir.exists()


# ===========================================================================
# 7. Multi-sample mode
# ===========================================================================


def test_multi_mode_calls_multisample_runner(cli_runner, tmp_path):
    input_file = tmp_path / "files.txt"
    input_file.write_text("sample1.tsv\n")

    with patch(
        "kegganog.kegganog_multi.MultiSampleRunner.run", return_value=None
    ) as mock:
        cli_runner.invoke(
            app, ["-M", "-i", str(input_file), "-o", str(tmp_path / "output")]
        )

    mock.assert_called_once()


# ===========================================================================
# 8. MultiSampleRunner
# ===========================================================================


class TestMultiSampleRunner:
    def test_collect_single_file_path(self, tmp_path):
        from kegganog.kegganog_multi import MultiSampleRunner

        f = tmp_path / "sample.annotations"
        f.write_bytes(b"x")
        r = MultiSampleRunner(input_path=str(f), output_dir=str(tmp_path))
        assert r._collect_input_paths() == [str(f)]

    def test_collect_paths_from_txt_manifest(self, tmp_path):
        from kegganog.kegganog_multi import MultiSampleRunner

        f1, f2 = tmp_path / "s1.annotations", tmp_path / "s2.annotations"
        f1.write_bytes(b"x")
        f2.write_bytes(b"x")
        manifest = tmp_path / "list.txt"
        manifest.write_text(f"{f1}\n{f2}\n")

        paths = MultiSampleRunner(
            input_path=str(manifest), output_dir=str(tmp_path)
        )._collect_input_paths()

        assert str(f1) in paths
        assert str(f2) in paths

    def test_load_files_skips_missing_and_warns(self, tmp_path, caplog):
        import logging

        from kegganog.kegganog_multi import MultiSampleRunner

        r = MultiSampleRunner(
            input_path=str(tmp_path / "nonexistent.annotations"),
            output_dir=str(tmp_path),
        )
        with caplog.at_level(logging.WARNING):
            files = r._load_files()

        assert files == []
        assert "does not exist" in caplog.text

    def test_load_files_reads_bytes(self, tmp_path):
        from kegganog.kegganog_multi import MultiSampleRunner

        f = tmp_path / "sample.annotations"
        f.write_bytes(b"content")
        files = MultiSampleRunner(
            input_path=str(f), output_dir=str(tmp_path)
        )._load_files()

        assert len(files) == 1
        assert files[0] == ("sample.annotations", b"content")

    def test_run_delegates_to_run_multi(self, tmp_path):
        from kegganog.kegganog_multi import MultiSampleRunner
        from kegganog.processing.pipeline import PipelineResult

        f = tmp_path / "sample.annotations"
        f.write_bytes(b"x")
        fake_result = PipelineResult(
            zip_path=Path("z"),
            png_path=Path("p"),
            tsv_path=Path("t"),
            samples=["sample"],
            pathways=["glycolysis"],
        )

        with patch(
            "kegganog.kegganog_multi.run_multi", return_value=fake_result
        ) as mock:
            result = MultiSampleRunner(
                input_path=str(f), output_dir=str(tmp_path)
            ).run()

        mock.assert_called_once()
        assert result is fake_result


# ===========================================================================
# 9. entry_point
# ===========================================================================


def test_entry_point_keyboard_interrupt_exits_one(capsys):
    from kegganog.kegganog import entry_point

    with patch("kegganog.kegganog.app") as mock_app:
        mock_app.side_effect = KeyboardInterrupt
        with pytest.raises(SystemExit) as exc_info:
            entry_point()

    assert exc_info.value.code == 1
    assert "interrupted" in capsys.readouterr().err.lower()
