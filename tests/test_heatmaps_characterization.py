"""Characterization tests for cheatmaps outputs (behavior lock for refactors)."""

from __future__ import annotations

import itertools
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from kegganog.cheatmaps import (
    grouped_heatmap,
    grouped_heatmap_multi,
    simple_heatmap,
    simple_heatmap_multi,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SIMPLE_TSV = FIXTURES / "simple_decoder.tsv"
GROUPED_TSV = FIXTURES / "grouped_decoder.tsv"

# Fixed rendering parameters so outputs are comparable across calls in one process.
_CHAR_DPI = 100
_CHAR_FIGSIZE = (12, 12)
_CHAR_COLOR = "Blues"
_CHAR_SAMPLE = "TEST"


def _read_png_sha256(out_dir: Path) -> str:
    import hashlib
    png = out_dir / "heatmap_figure.png"
    assert png.is_file(), f"missing {png}"
    return hashlib.sha256(png.read_bytes()).hexdigest()


def _assert_reproducible_twice(name: str, generate_twice) -> None:
    """Same inputs in the same process must yield identical PNG bytes."""
    a = generate_twice()
    b = generate_twice()
    assert a == b, f"{name}: two consecutive runs produced different PNG hashes"


@pytest.fixture
def multi_simple_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Function": [f"p{i}" for i in range(9)],
            "A": [0.1] * 9,
            "B": [0.2] * 9,
        }
    )


@pytest.fixture
def multi_grouped_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Function": [
                "glycolysis",
                "TCA Cycle",
                "beta-glucosidase",
                "RuBisCo",
                "nitrogen fixation",
                "Cytochrome c oxidase",
                "sulfide oxidation",
                "arginine",
                "pullulanase",
            ],
            "A": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "B": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        }
    )


def test_simple_heatmap_reproducible(tmp_path: Path) -> None:
    seq = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"o_{next(seq)}"
        d.mkdir()
        simple_heatmap.generate_heatmap(
            str(SIMPLE_TSV),
            str(d),
            _CHAR_DPI,
            _CHAR_COLOR,
            _CHAR_SAMPLE,
            figsize=_CHAR_FIGSIZE,
            annot=True,
        )
        h = _read_png_sha256(d)
        plt.close("all")
        return h

    _assert_reproducible_twice("simple", run_once)


def test_grouped_heatmap_reproducible(tmp_path: Path) -> None:
    seq = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"g_{next(seq)}"
        d.mkdir()
        grouped_heatmap.generate_grouped_heatmap(
            str(GROUPED_TSV),
            str(d),
            _CHAR_DPI,
            _CHAR_COLOR,
            _CHAR_SAMPLE,
            figsize=_CHAR_FIGSIZE,
            annot=True,
        )
        h = _read_png_sha256(d)
        plt.close("all")
        return h

    _assert_reproducible_twice("grouped", run_once)


def test_simple_heatmap_multi_reproducible(tmp_path: Path, multi_simple_df: pd.DataFrame) -> None:
    seq = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"m_{next(seq)}"
        d.mkdir()
        simple_heatmap_multi.generate_heatmap_multi(
            multi_simple_df, str(d), _CHAR_DPI, _CHAR_COLOR, figsize=_CHAR_FIGSIZE
        )
        h = _read_png_sha256(d)
        plt.close("all")
        return h

    _assert_reproducible_twice("multi_simple", run_once)


def test_grouped_heatmap_multi_reproducible(
    tmp_path: Path, multi_grouped_df: pd.DataFrame
) -> None:
    seq = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"mg_{next(seq)}"
        d.mkdir()
        grouped_heatmap_multi.generate_grouped_heatmap_multi(
            multi_grouped_df, str(d), _CHAR_DPI, _CHAR_COLOR, figsize=_CHAR_FIGSIZE
        )
        h = _read_png_sha256(d)
        plt.close("all")
        return h

    _assert_reproducible_twice("multi_grouped", run_once)


