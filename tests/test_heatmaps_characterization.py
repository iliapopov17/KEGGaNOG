"""Characterization tests for cheatmap rendering — behaviour lock for refactors.

Each test asserts that two consecutive calls with identical inputs produce
bit-identical PNG output. A hash mismatch means a rendering change that must
be explicitly acknowledged before merging.

Fixtures for multi-sample DataFrames live here (not in conftest) because
they are only needed by this module.
"""

from __future__ import annotations

import hashlib
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

_DPI = 100
_FIGSIZE = (12, 12)
_COLOR = "Blues"
_SAMPLE = "TEST"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256_of_heatmap_png(out_dir: Path) -> str:
    png = out_dir / "heatmap_figure.png"
    assert png.is_file(), f"Expected heatmap PNG at {png}"
    return hashlib.sha256(png.read_bytes()).hexdigest()


def _assert_reproducible(label: str, generate_fn) -> None:
    """Call generate_fn twice; assert both runs yield the same PNG hash."""
    a, b = generate_fn(), generate_fn()
    assert a == b, f"{label}: consecutive runs produced different PNG hashes"


# ---------------------------------------------------------------------------
# Local fixtures (not shared — only used by this module)
# ---------------------------------------------------------------------------


@pytest.fixture
def multi_simple_df() -> pd.DataFrame:
    return pd.DataFrame(
        {"Function": [f"p{i}" for i in range(9)], "A": [0.1] * 9, "B": [0.2] * 9}
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


# ===========================================================================
# Reproducibility characterization tests
# ===========================================================================


def test_simple_heatmap_is_reproducible(tmp_path: Path) -> None:
    counter = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"s_{next(counter)}"
        d.mkdir()
        simple_heatmap.generate_heatmap(
            str(SIMPLE_TSV),
            str(d),
            _DPI,
            _COLOR,
            _SAMPLE,
            figsize=_FIGSIZE,
            annot=True,
        )
        result = _sha256_of_heatmap_png(d)
        plt.close("all")
        return result

    _assert_reproducible("simple_heatmap", run_once)


def test_grouped_heatmap_is_reproducible(tmp_path: Path) -> None:
    counter = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"g_{next(counter)}"
        d.mkdir()
        grouped_heatmap.generate_grouped_heatmap(
            str(GROUPED_TSV),
            str(d),
            _DPI,
            _COLOR,
            _SAMPLE,
            figsize=_FIGSIZE,
            annot=True,
        )
        result = _sha256_of_heatmap_png(d)
        plt.close("all")
        return result

    _assert_reproducible("grouped_heatmap", run_once)


def test_simple_heatmap_multi_is_reproducible(
    tmp_path: Path, multi_simple_df: pd.DataFrame
) -> None:
    counter = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"ms_{next(counter)}"
        d.mkdir()
        simple_heatmap_multi.generate_heatmap_multi(
            multi_simple_df, str(d), _DPI, _COLOR, figsize=_FIGSIZE
        )
        result = _sha256_of_heatmap_png(d)
        plt.close("all")
        return result

    _assert_reproducible("simple_heatmap_multi", run_once)


def test_grouped_heatmap_multi_is_reproducible(
    tmp_path: Path, multi_grouped_df: pd.DataFrame
) -> None:
    counter = itertools.count()

    def run_once() -> str:
        d = tmp_path / f"mg_{next(counter)}"
        d.mkdir()
        grouped_heatmap_multi.generate_grouped_heatmap_multi(
            multi_grouped_df, str(d), _DPI, _COLOR, figsize=_FIGSIZE
        )
        result = _sha256_of_heatmap_png(d)
        plt.close("all")
        return result

    _assert_reproducible("grouped_heatmap_multi", run_once)
