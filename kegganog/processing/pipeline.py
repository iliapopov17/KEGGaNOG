from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .data_processing import parse_emapper, run_kegg_decoder
from .data_processing_multi import merge_outputs
from .data_processing_multi import parse_emapper as parse_emapper_multi
from .data_processing_multi import run_kegg_decoder as run_kegg_decoder_multi

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class PipelineResult:
    zip_path: str
    png_path: str
    tsv_path: str
    samples: list[str] = field(default_factory=list)
    pathways: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _secure_temp_path(suffix: str) -> Path:
    """Return a closed temp file path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return Path(path)


def _pack_results(output_dir: Path) -> tuple[str, str]:
    """Pack all output files into a ZIP and copy the first PNG to a stable path."""
    png_files = list(output_dir.rglob("*.png"))
    if not png_files:
        raise FileNotFoundError(
            "KEGGaNOG finished but produced no PNG file. "
            "Check that the input file is a valid eggNOG-mapper annotation."
        )
    stable_png = _secure_temp_path(".png")
    shutil.copy2(png_files[0], stable_png)

    stable_zip = _secure_temp_path(".zip")
    with zipfile.ZipFile(stable_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for result_file in output_dir.rglob("*"):
            if result_file.is_file():
                zf.write(result_file, result_file.relative_to(output_dir))

    return str(stable_zip), str(stable_png)


def _run_single_in_dir(
    file_bytes: bytes,
    sample_name: str,
    dpi: int,
    color: str,
    group: bool,
    output_dir: Path,
) -> tuple[list[str], list[str], str]:
    """
    Core single-sample logic — writes results into output_dir.
    Returns (samples, pathways, kegg_decoder_file_path).
    """
    from ..cheatmaps import grouped_heatmap, simple_heatmap

    temp_folder = output_dir / "temp_files"
    temp_folder.mkdir(exist_ok=True)

    input_file = temp_folder / "input.annotations"
    input_file.write_bytes(file_bytes)

    kegg_decoder_file = run_kegg_decoder(
        parse_emapper(str(input_file), str(temp_folder)),
        str(output_dir),
        sample_name,
    )

    if group:
        grouped_heatmap.generate_grouped_heatmap(
            kegg_decoder_file, str(output_dir), dpi, color, sample_name
        )
    else:
        simple_heatmap.generate_heatmap(
            kegg_decoder_file, str(output_dir), dpi, color, sample_name
        )

    df = pd.read_csv(kegg_decoder_file, sep="\t", index_col=0)
    pathways = list(df.columns)

    return [sample_name], pathways, kegg_decoder_file


def _run_multi_in_dir(
    named_files: list[tuple[str, bytes]],
    dpi: int,
    color: str,
    group: bool,
    output_dir: Path,
) -> tuple[list[str], list[str], str]:
    """
    Core multi-sample logic — writes results into output_dir.
    Returns (samples, pathways, merged_tsv_path).
    """
    from ..cheatmaps import grouped_heatmap_multi, simple_heatmap_multi

    temp_folder = output_dir / "temp_files"
    temp_folder.mkdir(exist_ok=True)

    for filename, file_bytes in named_files:
        file_prefix = filename.replace(".emapper.annotations", "")
        file_prefix = Path(file_prefix).stem if "." in file_prefix else file_prefix

        sample_folder = temp_folder / file_prefix
        sample_folder.mkdir(exist_ok=True)

        input_file = sample_folder / filename
        input_file.write_bytes(file_bytes)

        parsed_file = parse_emapper_multi(
            str(input_file), str(sample_folder), file_prefix
        )
        run_kegg_decoder_multi(parsed_file, str(sample_folder), file_prefix)

    merged_df = merge_outputs(str(output_dir))

    if group:
        grouped_heatmap_multi.generate_grouped_heatmap_multi(
            merged_df, str(output_dir), dpi, color
        )
    else:
        simple_heatmap_multi.generate_heatmap_multi(
            merged_df, str(output_dir), dpi, color
        )

    samples = [c for c in merged_df.columns if c != "Function"]
    pathways = list(merged_df["Function"].dropna().unique())
    merged_tsv = str(output_dir / "merged_pathways.tsv")

    return samples, pathways, merged_tsv


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_single(
    file_bytes: bytes,
    sample_name: str,
    dpi: int,
    color: str,
    group: bool,
    output_dir: str | None = None,
) -> PipelineResult:
    """
    Full single-sample pipeline.

    Parameters:
    - file_bytes: Raw bytes of the eggNOG-mapper annotation file.
    - sample_name: Label used for the sample in outputs.
    - dpi: Resolution of the output image.
    - color: Seaborn colormap name.
    - group: Whether to use grouped heatmap layout.
    - output_dir: If provided, write results here (CLI mode).
                  If None, use a temp directory (web mode).

    Returns:
    - PipelineResult with paths to ZIP, PNG, TSV and metadata.
    """
    if output_dir is not None:
        # CLI mode — write directly to user-specified directory
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        samples, pathways, kegg_decoder_file = _run_single_in_dir(
            file_bytes, sample_name, dpi, color, group, out
        )
        stable_tsv = _secure_temp_path(".tsv")
        shutil.copy2(kegg_decoder_file, stable_tsv)
        zip_path, png_path = _pack_results(out)
        return PipelineResult(
            zip_path=zip_path,
            png_path=png_path,
            tsv_path=str(stable_tsv),
            samples=samples,
            pathways=pathways,
        )

    # Web mode — use temp directory, results survive via stable copies
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "output"
        out.mkdir()
        samples, pathways, kegg_decoder_file = _run_single_in_dir(
            file_bytes, sample_name, dpi, color, group, out
        )
        stable_tsv = _secure_temp_path(".tsv")
        shutil.copy2(kegg_decoder_file, stable_tsv)
        zip_path, png_path = _pack_results(out)

    return PipelineResult(
        zip_path=zip_path,
        png_path=png_path,
        tsv_path=str(stable_tsv),
        samples=samples,
        pathways=pathways,
    )


def run_multi(
    named_files: list[tuple[str, bytes]],
    dpi: int,
    color: str,
    group: bool,
    output_dir: str | None = None,
) -> PipelineResult:
    """
    Full multi-sample pipeline.

    Parameters:
    - named_files: List of (filename, file_bytes) tuples.
    - dpi: Resolution of the output image.
    - color: Seaborn colormap name.
    - group: Whether to use grouped heatmap layout.
    - output_dir: If provided, write results here (CLI mode).
                  If None, use a temp directory (web mode).

    Returns:
    - PipelineResult with paths to ZIP, PNG, TSV and metadata.
    """
    if output_dir is not None:
        # CLI mode — write directly to user-specified directory
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        samples, pathways, merged_tsv = _run_multi_in_dir(
            named_files, dpi, color, group, out
        )
        stable_tsv = _secure_temp_path(".tsv")
        shutil.copy2(merged_tsv, stable_tsv)
        zip_path, png_path = _pack_results(out)
        return PipelineResult(
            zip_path=zip_path,
            png_path=png_path,
            tsv_path=str(stable_tsv),
            samples=samples,
            pathways=pathways,
        )

    # Web mode — use temp directory, results survive via stable copies
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "output"
        out.mkdir()
        samples, pathways, merged_tsv = _run_multi_in_dir(
            named_files, dpi, color, group, out
        )
        stable_tsv = _secure_temp_path(".tsv")
        shutil.copy2(merged_tsv, stable_tsv)
        zip_path, png_path = _pack_results(out)

    return PipelineResult(
        zip_path=zip_path,
        png_path=png_path,
        tsv_path=str(stable_tsv),
        samples=samples,
        pathways=pathways,
    )
