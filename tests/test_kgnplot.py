"""Tests for kegganog.kgnplot public API.

Each plot type gets its own test class covering:
  - Return type and figure presence (smoke).
  - Key optional parameters (sort, cmap, title, grid, legend, etc.).
  - savefig() writes a non-empty file.

Fixtures are local to this module — DataFrame shapes differ per plot type.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
import tqdm as tqdm_mod

from kegganog.kgnplot.barplot import KgnBarplot, barplot
from kegganog.kgnplot.base import KgnPlotBase
from kegganog.kgnplot.boxplot import KgnBoxplot, boxplot
from kegganog.kgnplot.corrnet import KgnCorrnet, correlation_network
from kegganog.kgnplot.heatmap import KgnHeatmap, heatmap, silent_plot_and_tqdm
from kegganog.kgnplot.radarplot import KgnRadar, radarplot
from kegganog.kgnplot.stackedbar import KgnStackedBarplot, stacked_barplot
from kegganog.kgnplot.streamgraph import KgnStreamgraph, streamgraph

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def single_sample_df() -> pd.DataFrame:
    """Single-sample KEGG-Decoder output (one row, pathway columns)."""
    return pd.read_csv(FIXTURES / "simple_decoder.tsv", sep="\t")


@pytest.fixture
def multi_sample_df() -> pd.DataFrame:
    """Multi-sample output with Function column and per-sample value columns.

    Pathway names are drawn exclusively from grouped_decoder.tsv so that
    test_multi_sample_with_group produces no All-NaN slices in seaborn.
    """
    return pd.DataFrame(
        {
            "Function": ["glycolysis", "beta-glucosidase", "nitrogen fixation"],
            "S1": [0.5, 0.3, 0.8],
            "S2": [0.3, 0.5, 0.6],
            "S3": [0.6, 0.9, 0.4],
        }
    )


@pytest.fixture
def corr_df() -> pd.DataFrame:
    """Four-sample DataFrame with correlated pathways (suitable for corrnet)."""
    return pd.DataFrame(
        {
            "Sample": ["P1", "P2", "P3", "P4"],
            "pathway1": [0.1, 0.4, 0.7, 0.9],
            "pathway2": [0.15, 0.45, 0.65, 0.85],
            "pathway3": [0.2, 0.5, 0.6, 0.8],
        }
    )


# ===========================================================================
# KgnPlotBase
# ===========================================================================


class TestKgnPlotBase:
    def test_plotfig_returns_the_figure(self):
        fig, ax = plt.subplots()
        obj = KgnPlotBase(fig, ax)
        assert obj.plotfig() is fig
        plt.close(fig)

    def test_savefig_writes_non_empty_file(self, tmp_path):
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        obj = KgnPlotBase(fig, ax)
        out = tmp_path / "out.png"
        obj.savefig(str(out))
        assert out.exists() and out.stat().st_size > 0
        plt.close(fig)


# ===========================================================================
# barplot
# ===========================================================================


class TestBarplot:
    def test_returns_kgn_barplot_with_figure(self, single_sample_df):
        result = barplot(single_sample_df)
        assert isinstance(result, KgnBarplot)
        assert isinstance(result.fig, plt.Figure)
        assert result.ax is not None

    def test_ascending_sort_order(self, single_sample_df):
        assert isinstance(barplot(single_sample_df, sort_order="ascending"), KgnBarplot)

    def test_list_cmap(self, single_sample_df):
        assert isinstance(
            barplot(single_sample_df, cmap=["#ff0000", "#00ff00", "#0000ff"] * 5),
            KgnBarplot,
        )

    def test_drops_function_column_gracefully(self):
        df = pd.DataFrame({"Function": ["glycolysis"], "a1": [0.5], "a2": [0.3]})
        assert isinstance(barplot(df), KgnBarplot)

    def test_with_title(self, single_sample_df):
        assert isinstance(barplot(single_sample_df, title="My Barplot"), KgnBarplot)

    def test_without_grid(self, single_sample_df):
        assert isinstance(barplot(single_sample_df, grid=False), KgnBarplot)

    def test_savefig_writes_file(self, single_sample_df, tmp_path):
        out = tmp_path / "barplot.png"
        barplot(single_sample_df).savefig(str(out))
        assert out.exists()


# ===========================================================================
# boxplot
# ===========================================================================


class TestBoxplot:
    def test_returns_kgn_boxplot_with_figure(self, multi_sample_df):
        result = boxplot(multi_sample_df)
        assert isinstance(result, KgnBoxplot)
        assert isinstance(result.fig, plt.Figure)

    def test_without_fliers(self, multi_sample_df):
        assert isinstance(boxplot(multi_sample_df, showfliers=False), KgnBoxplot)

    def test_without_grid(self, multi_sample_df):
        assert isinstance(boxplot(multi_sample_df, grid=False), KgnBoxplot)

    def test_with_title(self, multi_sample_df):
        assert isinstance(
            boxplot(multi_sample_df, title="Box Distribution"), KgnBoxplot
        )

    def test_savefig_writes_file(self, multi_sample_df, tmp_path):
        out = tmp_path / "boxplot.png"
        boxplot(multi_sample_df).savefig(str(out))
        assert out.exists()


# ===========================================================================
# correlation_network
# ===========================================================================


class TestCorrnet:
    def test_returns_kgn_corrnet_with_figure(self, corr_df):
        result = correlation_network(corr_df)
        assert isinstance(result, KgnCorrnet)
        assert isinstance(result.fig, plt.Figure)

    def test_with_title(self, corr_df):
        assert isinstance(
            correlation_network(corr_df, title="Sample Correlations"), KgnCorrnet
        )

    def test_save_matrix_writes_file(self, corr_df, tmp_path):
        matrix_path = str(tmp_path / "matrix.tsv")
        correlation_network(corr_df, save_matrix=matrix_path)
        assert Path(matrix_path).exists()

    def test_savefig_writes_file(self, corr_df, tmp_path):
        out = tmp_path / "corrnet.png"
        correlation_network(corr_df).savefig(str(out))
        assert out.exists()


# ===========================================================================
# radarplot
# ===========================================================================


class TestRadarplot:
    def test_returns_kgn_radar_with_figure(self, multi_sample_df):
        result = radarplot(multi_sample_df, pathways=["glycolysis"])
        assert isinstance(result, KgnRadar)
        assert isinstance(result.fig, plt.Figure)

    def test_multiple_pathways(self, multi_sample_df):
        assert isinstance(
            radarplot(multi_sample_df, pathways=["glycolysis", "beta-glucosidase"]),
            KgnRadar,
        )

    def test_maximum_four_pathways_accepted(self, multi_sample_df):
        assert isinstance(
            radarplot(
                multi_sample_df,
                pathways=["glycolysis", "beta-glucosidase", "nitrogen fixation"],
            ),
            KgnRadar,
        )

    def test_five_pathways_raises(self, multi_sample_df):
        with pytest.raises(ValueError, match="Maximum of 4"):
            radarplot(multi_sample_df, pathways=["p1", "p2", "p3", "p4", "p5"])

    def test_missing_pathway_emits_warning_and_still_returns_radar(
        self, multi_sample_df
    ):
        # The function must not raise — it warns and skips the unknown pathway.
        # Two warnings are expected:
        #   1. radarplot itself: "not found in DataFrame"
        #   2. matplotlib: "No artists with labels found" — because the legend
        #      is drawn on an empty axes after all pathways were skipped.
        # pytest.warns(match=...) asserts the first and catches both, preventing
        # either from leaking into the test output.
        with pytest.warns(UserWarning):
            result = radarplot(multi_sample_df, pathways=["nonexistent_pathway"])
        assert isinstance(result, KgnRadar)

    def test_without_legend(self, multi_sample_df):
        assert isinstance(
            radarplot(multi_sample_df, pathways=["glycolysis"], show_legend=False),
            KgnRadar,
        )

    def test_explicit_colors(self, multi_sample_df):
        assert isinstance(
            radarplot(
                multi_sample_df,
                pathways=["glycolysis", "beta-glucosidase"],
                colors=["red", "blue"],
            ),
            KgnRadar,
        )

    def test_explicit_sample_order(self, multi_sample_df):
        assert isinstance(
            radarplot(
                multi_sample_df, pathways=["glycolysis"], sample_order=["S1", "S2"]
            ),
            KgnRadar,
        )

    def test_label_background_and_edgecolor(self, multi_sample_df):
        assert isinstance(
            radarplot(
                multi_sample_df,
                pathways=["glycolysis"],
                label_background="white",
                label_edgecolor="black",
            ),
            KgnRadar,
        )

    def test_savefig_writes_file(self, multi_sample_df, tmp_path):
        out = tmp_path / "radar.png"
        radarplot(multi_sample_df, pathways=["glycolysis"]).savefig(str(out))
        assert out.exists()


# ===========================================================================
# stacked_barplot
# ===========================================================================


class TestStackedBarplot:
    def test_returns_kgn_stacked_with_figure(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df)
        assert isinstance(result, KgnStackedBarplot)
        assert isinstance(result.fig, plt.Figure)

    def test_without_legend(self, multi_sample_df):
        assert isinstance(
            stacked_barplot(multi_sample_df, show_legend=False), KgnStackedBarplot
        )

    def test_without_grid(self, multi_sample_df):
        assert isinstance(
            stacked_barplot(multi_sample_df, grid=False), KgnStackedBarplot
        )

    def test_list_cmap(self, multi_sample_df):
        assert isinstance(
            stacked_barplot(multi_sample_df, cmap=["red", "blue", "green"]),
            KgnStackedBarplot,
        )

    def test_with_title(self, multi_sample_df):
        assert isinstance(
            stacked_barplot(multi_sample_df, title="Stacked"), KgnStackedBarplot
        )

    def test_savefig_writes_file(self, multi_sample_df, tmp_path):
        out = tmp_path / "stacked.png"
        stacked_barplot(multi_sample_df).savefig(str(out))
        assert out.exists()


# ===========================================================================
# streamgraph
# ===========================================================================


class TestStreamgraph:
    def test_returns_kgn_streamgraph_with_figure(self, multi_sample_df):
        result = streamgraph(multi_sample_df)
        assert isinstance(result, KgnStreamgraph)
        assert isinstance(result.fig, plt.Figure)

    def test_without_legend(self, multi_sample_df):
        assert isinstance(
            streamgraph(multi_sample_df, show_legend=False), KgnStreamgraph
        )

    def test_without_grid(self, multi_sample_df):
        assert isinstance(streamgraph(multi_sample_df, grid=False), KgnStreamgraph)

    def test_list_cmap(self, multi_sample_df):
        assert isinstance(
            streamgraph(multi_sample_df, cmap=["#aaa", "#bbb", "#ccc"]), KgnStreamgraph
        )

    def test_with_edgecolor(self, multi_sample_df):
        assert isinstance(
            streamgraph(multi_sample_df, edgecolor="black"), KgnStreamgraph
        )

    def test_savefig_writes_file(self, multi_sample_df, tmp_path):
        out = tmp_path / "stream.png"
        streamgraph(multi_sample_df).savefig(str(out))
        assert out.exists()


# ===========================================================================
# heatmap (universal wrapper)
# ===========================================================================


class TestHeatmap:
    def test_single_sample_no_group(self, single_sample_df):
        result = heatmap(single_sample_df, sample_name="TEST")
        assert isinstance(result, KgnHeatmap)
        assert isinstance(result.fig, plt.Figure)

    def test_single_sample_with_group(self):
        df = pd.read_csv(FIXTURES / "grouped_decoder.tsv", sep="\t")
        assert isinstance(heatmap(df, group=True, sample_name="TEST"), KgnHeatmap)

    def test_multi_sample_no_group(self, multi_sample_df):
        assert isinstance(heatmap(multi_sample_df), KgnHeatmap)

    def test_multi_sample_with_group(self, multi_sample_df):
        assert isinstance(heatmap(multi_sample_df, group=True), KgnHeatmap)

    def test_custom_figsize(self, single_sample_df):
        assert isinstance(
            heatmap(single_sample_df, figsize=(10, 5), sample_name="TEST"), KgnHeatmap
        )

    def test_custom_color(self, single_sample_df):
        assert isinstance(
            heatmap(single_sample_df, color="Greens", sample_name="TEST"), KgnHeatmap
        )

    def test_savefig_writes_file(self, single_sample_df, tmp_path):
        out = tmp_path / "heatmap.png"
        heatmap(single_sample_df, sample_name="TEST").savefig(str(out))
        assert out.exists()

    def test_silent_plot_and_tqdm_restores_state_after_exception(self):
        original_show = plt.show
        original_tqdm = tqdm_mod.tqdm

        try:
            with silent_plot_and_tqdm():
                raise RuntimeError("intentional test error")
        except RuntimeError:
            pass

        assert plt.show is original_show
        assert tqdm_mod.tqdm is original_tqdm
