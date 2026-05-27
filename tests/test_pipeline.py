"""Tests for kegganog.processing.pipeline."""

from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kegganog.processing.pipeline import (
    PipelineResult,
    _pack_results,
    _secure_temp_path,
    run_multi,
    run_single,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_output_dir_with_png(tmp_path: Path) -> Path:
    """Create a minimal output dir with a PNG so _pack_results succeeds."""
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = tmp_path / "output"
    out.mkdir()
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(1, 1))
    fig.savefig(buf, format="png", dpi=72)
    plt.close(fig)
    (out / "heatmap_figure.png").write_bytes(buf.getvalue())
    return out


def _fake_heatmap(tsv_or_df, output_folder, dpi, color, sample_name=None, **kwargs):
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(1, 1))
    fig.savefig(buf, format="png", dpi=72)
    plt.close(fig)
    (Path(output_folder) / "heatmap_figure.png").write_bytes(buf.getvalue())


# ---------------------------------------------------------------------------
# _secure_temp_path
# ---------------------------------------------------------------------------


def test_secure_temp_path_returns_path():
    p = _secure_temp_path(".tsv")
    assert p.suffix == ".tsv"
    assert p.exists()
    p.unlink()


def test_secure_temp_path_unique():
    p1 = _secure_temp_path(".png")
    p2 = _secure_temp_path(".png")
    assert p1 != p2
    p1.unlink()
    p2.unlink()


# ---------------------------------------------------------------------------
# _pack_results
# ---------------------------------------------------------------------------


def test_pack_results_creates_zip_and_png(tmp_path):
    out = _make_output_dir_with_png(tmp_path)
    zip_path, png_path = _pack_results(out)

    assert Path(zip_path).exists()
    assert Path(png_path).exists()
    assert Path(zip_path).suffix == ".zip"
    assert Path(png_path).suffix == ".png"


def test_pack_results_raises_when_no_png(tmp_path):
    out = tmp_path / "empty"
    out.mkdir()
    with pytest.raises(FileNotFoundError, match="no PNG"):
        _pack_results(out)


def test_pack_results_zip_contains_files(tmp_path):
    out = _make_output_dir_with_png(tmp_path)
    (out / "extra.tsv").write_text("data")
    zip_path, _ = _pack_results(out)

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    assert any("heatmap_figure.png" in n for n in names)
    assert any("extra.tsv" in n for n in names)


# ---------------------------------------------------------------------------
# PipelineResult
# ---------------------------------------------------------------------------


def test_pipeline_result_fields():
    r = PipelineResult(
        zip_path="/tmp/a.zip",
        png_path="/tmp/a.png",
        tsv_path="/tmp/a.tsv",
        samples=["S1", "S2"],
        pathways=["glycolysis"],
    )
    assert r.zip_path == "/tmp/a.zip"
    assert r.samples == ["S1", "S2"]
    assert r.pathways == ["glycolysis"]


def test_pipeline_result_default_lists():
    r = PipelineResult(zip_path="z", png_path="p", tsv_path="t")
    assert r.samples == []
    assert r.pathways == []


# ---------------------------------------------------------------------------
# run_single — web mode (output_dir=None)
# ---------------------------------------------------------------------------


def test_run_single_web_mode_returns_pipeline_result(tmp_path):
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def fake_run_single_in_dir(file_bytes, sample_name, dpi, color, group, output_dir):
        tsv = output_dir / "SAMPLE_pathways.tsv"
        tsv.write_text("Function\ta1\na1\t0.5\n")

        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(1, 1))
        fig.savefig(buf, format="png", dpi=72)
        plt.close(fig)
        (output_dir / "heatmap_figure.png").write_bytes(buf.getvalue())

        return ["SAMPLE"], ["a1"], str(tsv)

    with patch(
        "kegganog.processing.pipeline._run_single_in_dir", fake_run_single_in_dir
    ):
        result = run_single(
            file_bytes=b"dummy",
            sample_name="SAMPLE",
            dpi=72,
            color="Blues",
            group=False,
        )

    assert isinstance(result, PipelineResult)
    assert result.samples == ["SAMPLE"]
    assert result.pathways == ["a1"]
    assert Path(result.zip_path).exists()
    assert Path(result.png_path).exists()
    assert Path(result.tsv_path).exists()


def test_run_single_cli_mode_writes_to_output_dir(tmp_path):
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = tmp_path / "output"
    out.mkdir()

    def fake_run_single_in_dir(file_bytes, sample_name, dpi, color, group, output_dir):
        tsv = output_dir / "SAMPLE_pathways.tsv"
        tsv.write_text("Function\ta1\na1\t0.5\n")

        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(1, 1))
        fig.savefig(buf, format="png", dpi=72)
        plt.close(fig)
        (output_dir / "heatmap_figure.png").write_bytes(buf.getvalue())

        return ["SAMPLE"], ["a1"], str(tsv)

    with patch(
        "kegganog.processing.pipeline._run_single_in_dir", fake_run_single_in_dir
    ):
        result = run_single(
            file_bytes=b"dummy",
            sample_name="SAMPLE",
            dpi=72,
            color="Blues",
            group=False,
            output_dir=str(out),
        )

    assert isinstance(result, PipelineResult)
    assert (out / "heatmap_figure.png").exists()


# ---------------------------------------------------------------------------
# run_multi — web mode and CLI mode
# ---------------------------------------------------------------------------


def _fake_run_multi_in_dir(named_files, dpi, color, group, output_dir):
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    merged_tsv = output_dir / "merged_pathways.tsv"
    merged_tsv.write_text("Function\tS1\tS2\nglycoly\t0.5\t0.3\n")

    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(1, 1))
    fig.savefig(buf, format="png", dpi=72)
    plt.close(fig)
    (output_dir / "heatmap_figure.png").write_bytes(buf.getvalue())

    return ["S1", "S2"], ["glycoly"], str(merged_tsv)


def test_run_multi_web_mode_returns_pipeline_result():
    with patch(
        "kegganog.processing.pipeline._run_multi_in_dir", _fake_run_multi_in_dir
    ):
        result = run_multi(
            named_files=[("s1.annotations", b"dummy"), ("s2.annotations", b"dummy")],
            dpi=72,
            color="Blues",
            group=False,
        )

    assert isinstance(result, PipelineResult)
    assert result.samples == ["S1", "S2"]
    assert result.pathways == ["glycoly"]
    assert Path(result.zip_path).exists()


def test_run_multi_cli_mode_writes_to_output_dir(tmp_path):
    out = tmp_path / "output"
    out.mkdir()

    with patch(
        "kegganog.processing.pipeline._run_multi_in_dir", _fake_run_multi_in_dir
    ):
        result = run_multi(
            named_files=[("s1.annotations", b"dummy")],
            dpi=72,
            color="Blues",
            group=False,
            output_dir=str(out),
        )

    assert isinstance(result, PipelineResult)
    assert (out / "heatmap_figure.png").exists()


# ---------------------------------------------------------------------------
# _run_single_in_dir
# ---------------------------------------------------------------------------


def test_run_single_in_dir_simple(tmp_path):
    from kegganog.processing.pipeline import _run_single_in_dir

    out = tmp_path / "output"
    out.mkdir()
    temp = out / "temp_files"
    temp.mkdir()

    def fake_parse(input_file, temp_folder):
        return str(tmp_path / "parsed.txt")

    def fake_decoder(parsed, output_folder, sample_name):
        tsv = Path(output_folder) / f"{sample_name}_pathways.tsv"
        tsv.write_text("Function\ta1\na1\t0.5\n")
        return str(tsv)

    with (
        patch("kegganog.processing.pipeline.parse_emapper", fake_parse),
        patch("kegganog.processing.pipeline.run_kegg_decoder", fake_decoder),
        patch("kegganog.cheatmaps.simple_heatmap.generate_heatmap", _fake_heatmap),
    ):
        samples, pathways, tsv_path = _run_single_in_dir(
            file_bytes=b"dummy",
            sample_name="SAMPLE",
            dpi=72,
            color="Blues",
            group=False,
            output_dir=out,
        )

    assert samples == ["SAMPLE"]
    assert "a1" in pathways
    assert Path(tsv_path).exists()


def test_run_single_in_dir_grouped(tmp_path):
    from kegganog.processing.pipeline import _run_single_in_dir

    out = tmp_path / "output"
    out.mkdir()

    def fake_parse(input_file, temp_folder):
        return str(tmp_path / "parsed.txt")

    def fake_decoder(parsed, output_folder, sample_name):
        tsv = Path(output_folder) / f"{sample_name}_pathways.tsv"
        tsv.write_text("Function\ta1\na1\t0.5\n")
        return str(tsv)

    with (
        patch("kegganog.processing.pipeline.parse_emapper", fake_parse),
        patch("kegganog.processing.pipeline.run_kegg_decoder", fake_decoder),
        patch(
            "kegganog.cheatmaps.grouped_heatmap.generate_grouped_heatmap",
            _fake_heatmap,
        ),
    ):
        samples, pathways, tsv_path = _run_single_in_dir(
            file_bytes=b"dummy",
            sample_name="SAMPLE",
            dpi=72,
            color="Blues",
            group=True,
            output_dir=out,
        )

    assert samples == ["SAMPLE"]


# ---------------------------------------------------------------------------
# _run_multi_in_dir
# ---------------------------------------------------------------------------


def test_run_multi_in_dir_simple(tmp_path):
    from kegganog.processing.pipeline import _run_multi_in_dir

    out = tmp_path / "output"
    out.mkdir()

    def fake_parse_multi(input_file, sample_folder, file_prefix):
        return str(tmp_path / "parsed.txt")

    def fake_decoder_multi(parsed, sample_folder, file_prefix):
        return str(tmp_path / "decoder.tsv")

    def fake_merge(output_folder):
        import pandas as pd

        df = pd.DataFrame(
            {
                "Function": ["glycolysis", "TCA Cycle"],
                "S1": [0.5, 0.7],
                "S2": [0.3, 0.8],
            }
        )
        merged = Path(output_folder) / "merged_pathways.tsv"
        df.to_csv(merged, sep="\t", index=False)
        return df

    def fake_heatmap_multi(df, output_folder, dpi, color, **kwargs):
        _fake_heatmap(df, output_folder, dpi, color)

    with (
        patch("kegganog.processing.pipeline.parse_emapper_multi", fake_parse_multi),
        patch(
            "kegganog.processing.pipeline.run_kegg_decoder_multi", fake_decoder_multi
        ),
        patch("kegganog.processing.pipeline.merge_outputs", fake_merge),
        patch(
            "kegganog.cheatmaps.simple_heatmap_multi.generate_heatmap_multi",
            fake_heatmap_multi,
        ),
    ):
        samples, pathways, merged_tsv = _run_multi_in_dir(
            named_files=[
                ("s1.emapper.annotations", b"x"),
                ("s2.emapper.annotations", b"x"),
            ],
            dpi=72,
            color="Blues",
            group=False,
            output_dir=out,
        )

    assert "S1" in samples
    assert "S2" in samples
    assert "glycolysis" in pathways


def test_run_multi_in_dir_grouped(tmp_path):
    from kegganog.processing.pipeline import _run_multi_in_dir

    out = tmp_path / "output"
    out.mkdir()

    def fake_parse_multi(input_file, sample_folder, file_prefix):
        return str(tmp_path / "parsed.txt")

    def fake_decoder_multi(parsed, sample_folder, file_prefix):
        return str(tmp_path / "decoder.tsv")

    def fake_merge(output_folder):
        import pandas as pd

        df = pd.DataFrame(
            {
                "Function": ["glycolysis"],
                "S1": [0.5],
            }
        )
        merged = Path(output_folder) / "merged_pathways.tsv"
        df.to_csv(merged, sep="\t", index=False)
        return df

    def fake_heatmap_grouped(df, output_folder, dpi, color, **kwargs):
        _fake_heatmap(df, output_folder, dpi, color)

    with (
        patch("kegganog.processing.pipeline.parse_emapper_multi", fake_parse_multi),
        patch(
            "kegganog.processing.pipeline.run_kegg_decoder_multi", fake_decoder_multi
        ),
        patch("kegganog.processing.pipeline.merge_outputs", fake_merge),
        patch(
            "kegganog.cheatmaps.grouped_heatmap_multi.generate_grouped_heatmap_multi",
            fake_heatmap_grouped,
        ),
    ):
        samples, pathways, merged_tsv = _run_multi_in_dir(
            named_files=[("s1.emapper.annotations", b"x")],
            dpi=72,
            color="Blues",
            group=True,
            output_dir=out,
        )

    assert samples == ["S1"]
