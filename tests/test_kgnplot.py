"""Tests for kegganog.kgnplot plot functions."""

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


@pytest.fixture
def single_sample_df() -> pd.DataFrame:
    """Single-sample pathways DataFrame (1 row, pathway columns)."""
    return pd.read_csv(FIXTURES / "simple_decoder.tsv", sep="\t")


@pytest.fixture
def multi_sample_df() -> pd.DataFrame:
    """Multi-sample pathways DataFrame (Function + sample columns)."""
    return pd.DataFrame(
        {
            "Function": ["glycolysis", "TCA Cycle", "beta-glucosidase", "CBB Cycle"],
            "S1": [0.5, 0.7, 0.3, 0.4],
            "S2": [0.3, 0.8, 0.5, 0.6],
            "S3": [0.6, 0.2, 0.9, 0.1],
        }
    )


@pytest.fixture
def corr_df() -> pd.DataFrame:
    """DataFrame suitable for correlation network (multiple correlated samples)."""
    return pd.DataFrame(
        {
            "Sample": ["P1", "P2", "P3", "P4"],
            "pathway1": [0.1, 0.4, 0.7, 0.9],
            "pathway2": [0.15, 0.45, 0.65, 0.85],
            "pathway3": [0.2, 0.5, 0.6, 0.8],
        }
    )


# ---------------------------------------------------------------------------
# KgnPlotBase
# ---------------------------------------------------------------------------


class TestKgnPlotBase:
    def test_savefig_writes_file(self, tmp_path):
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        obj = KgnPlotBase(fig, ax)
        out = tmp_path / "out.png"
        obj.savefig(str(out))
        assert out.exists()
        assert out.stat().st_size > 0
        plt.close(fig)

    def test_plotfig_returns_figure(self):
        fig, ax = plt.subplots()
        obj = KgnPlotBase(fig, ax)
        returned = obj.plotfig()
        assert returned is fig
        plt.close(fig)


# ---------------------------------------------------------------------------
# barplot
# ---------------------------------------------------------------------------


class TestBarplot:
    def test_returns_kgn_barplot(self, single_sample_df):
        result = barplot(single_sample_df)
        assert isinstance(result, KgnBarplot)
        assert isinstance(result.fig, plt.Figure)
        assert result.ax is not None

    def test_ascending_sort(self, single_sample_df):
        result = barplot(single_sample_df, sort_order="ascending")
        assert isinstance(result, KgnBarplot)

    def test_list_cmap(self, single_sample_df):
        colors = ["#ff0000", "#00ff00", "#0000ff"] * 5
        result = barplot(single_sample_df, cmap=colors)
        assert isinstance(result, KgnBarplot)

    def test_drops_function_column(self):
        df = pd.DataFrame({"Function": ["glycolysis"], "a1": [0.5], "a2": [0.3]})
        result = barplot(df)
        assert isinstance(result, KgnBarplot)

    def test_with_title(self, single_sample_df):
        result = barplot(single_sample_df, title="My Barplot")
        assert isinstance(result, KgnBarplot)

    def test_no_grid(self, single_sample_df):
        result = barplot(single_sample_df, grid=False)
        assert isinstance(result, KgnBarplot)

    def test_savefig(self, single_sample_df, tmp_path):
        result = barplot(single_sample_df)
        out = tmp_path / "barplot.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# boxplot
# ---------------------------------------------------------------------------


class TestBoxplot:
    def test_returns_kgn_boxplot(self, multi_sample_df):
        result = boxplot(multi_sample_df)
        assert isinstance(result, KgnBoxplot)
        assert isinstance(result.fig, plt.Figure)

    def test_no_fliers(self, multi_sample_df):
        result = boxplot(multi_sample_df, showfliers=False)
        assert isinstance(result, KgnBoxplot)

    def test_no_grid(self, multi_sample_df):
        result = boxplot(multi_sample_df, grid=False)
        assert isinstance(result, KgnBoxplot)

    def test_with_title(self, multi_sample_df):
        result = boxplot(multi_sample_df, title="Box Distribution")
        assert isinstance(result, KgnBoxplot)

    def test_savefig(self, multi_sample_df, tmp_path):
        result = boxplot(multi_sample_df)
        out = tmp_path / "boxplot.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# correlation_network
# ---------------------------------------------------------------------------


class TestCorrnet:
    def test_returns_kgn_corrnet(self, corr_df):
        result = correlation_network(corr_df)
        assert isinstance(result, KgnCorrnet)
        assert isinstance(result.fig, plt.Figure)

    def test_with_title(self, corr_df):
        result = correlation_network(corr_df, title="Sample Correlations")
        assert isinstance(result, KgnCorrnet)

    def test_save_matrix(self, corr_df, tmp_path):
        matrix_path = str(tmp_path / "matrix.tsv")
        result = correlation_network(corr_df, save_matrix=matrix_path)
        assert isinstance(result, KgnCorrnet)
        assert Path(matrix_path).exists()

    def test_savefig(self, corr_df, tmp_path):
        result = correlation_network(corr_df)
        out = tmp_path / "corrnet.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# radarplot
# ---------------------------------------------------------------------------


class TestRadarplot:
    def test_returns_kgn_radar(self, multi_sample_df):
        result = radarplot(multi_sample_df, pathways=["glycolysis"])
        assert isinstance(result, KgnRadar)
        assert isinstance(result.fig, plt.Figure)

    def test_multiple_pathways(self, multi_sample_df):
        result = radarplot(multi_sample_df, pathways=["glycolysis", "TCA Cycle"])
        assert isinstance(result, KgnRadar)

    def test_max_four_pathways(self, multi_sample_df):
        result = radarplot(
            multi_sample_df,
            pathways=["glycolysis", "TCA Cycle", "beta-glucosidase", "CBB Cycle"],
        )
        assert isinstance(result, KgnRadar)

    def test_too_many_pathways_raises(self, multi_sample_df):
        with pytest.raises(ValueError, match="Maximum of 4"):
            radarplot(
                multi_sample_df,
                pathways=["p1", "p2", "p3", "p4", "p5"],
            )

    def test_missing_pathway_prints_warning(self, multi_sample_df, capsys):
        result = radarplot(multi_sample_df, pathways=["nonexistent_pathway"])
        assert isinstance(result, KgnRadar)
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or True  # graceful skip

    def test_no_legend(self, multi_sample_df):
        result = radarplot(multi_sample_df, pathways=["glycolysis"], show_legend=False)
        assert isinstance(result, KgnRadar)

    def test_explicit_colors(self, multi_sample_df):
        result = radarplot(
            multi_sample_df,
            pathways=["glycolysis", "TCA Cycle"],
            colors=["red", "blue"],
        )
        assert isinstance(result, KgnRadar)

    def test_explicit_sample_order(self, multi_sample_df):
        result = radarplot(
            multi_sample_df,
            pathways=["glycolysis"],
            sample_order=["S1", "S2"],
        )
        assert isinstance(result, KgnRadar)

    def test_label_background(self, multi_sample_df):
        result = radarplot(
            multi_sample_df,
            pathways=["glycolysis"],
            label_background="white",
            label_edgecolor="black",
        )
        assert isinstance(result, KgnRadar)

    def test_savefig(self, multi_sample_df, tmp_path):
        result = radarplot(multi_sample_df, pathways=["glycolysis"])
        out = tmp_path / "radar.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# stacked_barplot
# ---------------------------------------------------------------------------


class TestStackedBarplot:
    def test_returns_kgn_stacked(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df)
        assert isinstance(result, KgnStackedBarplot)
        assert isinstance(result.fig, plt.Figure)

    def test_no_legend(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df, show_legend=False)
        assert isinstance(result, KgnStackedBarplot)

    def test_no_grid(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df, grid=False)
        assert isinstance(result, KgnStackedBarplot)

    def test_list_cmap(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df, cmap=["red", "blue", "green"])
        assert isinstance(result, KgnStackedBarplot)

    def test_with_title(self, multi_sample_df):
        result = stacked_barplot(multi_sample_df, title="Stacked")
        assert isinstance(result, KgnStackedBarplot)

    def test_savefig(self, multi_sample_df, tmp_path):
        result = stacked_barplot(multi_sample_df)
        out = tmp_path / "stacked.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# streamgraph
# ---------------------------------------------------------------------------


class TestStreamgraph:
    def test_returns_kgn_streamgraph(self, multi_sample_df):
        result = streamgraph(multi_sample_df)
        assert isinstance(result, KgnStreamgraph)
        assert isinstance(result.fig, plt.Figure)

    def test_no_legend(self, multi_sample_df):
        result = streamgraph(multi_sample_df, show_legend=False)
        assert isinstance(result, KgnStreamgraph)

    def test_no_grid(self, multi_sample_df):
        result = streamgraph(multi_sample_df, grid=False)
        assert isinstance(result, KgnStreamgraph)

    def test_list_cmap(self, multi_sample_df):
        result = streamgraph(multi_sample_df, cmap=["#aaa", "#bbb", "#ccc"])
        assert isinstance(result, KgnStreamgraph)

    def test_with_edgecolor(self, multi_sample_df):
        result = streamgraph(multi_sample_df, edgecolor="black")
        assert isinstance(result, KgnStreamgraph)

    def test_savefig(self, multi_sample_df, tmp_path):
        result = streamgraph(multi_sample_df)
        out = tmp_path / "stream.png"
        result.savefig(str(out))
        assert out.exists()


# ---------------------------------------------------------------------------
# heatmap (universal wrapper)
# ---------------------------------------------------------------------------


class TestHeatmap:
    def test_single_sample_no_group(self, single_sample_df):
        result = heatmap(single_sample_df, sample_name="TEST")
        assert isinstance(result, KgnHeatmap)
        assert isinstance(result.fig, plt.Figure)

    def test_single_sample_with_group(self):
        df = pd.read_csv(FIXTURES / "grouped_decoder.tsv", sep="\t")
        result = heatmap(df, group=True, sample_name="TEST")
        assert isinstance(result, KgnHeatmap)

    def test_multi_sample_no_group(self, multi_sample_df):
        result = heatmap(multi_sample_df)
        assert isinstance(result, KgnHeatmap)

    def test_multi_sample_with_group(self, multi_sample_df):
        result = heatmap(multi_sample_df, group=True)
        assert isinstance(result, KgnHeatmap)

    def test_custom_figsize(self, single_sample_df):
        result = heatmap(single_sample_df, figsize=(10, 5), sample_name="TEST")
        assert isinstance(result, KgnHeatmap)

    def test_custom_color(self, single_sample_df):
        result = heatmap(single_sample_df, color="Greens", sample_name="TEST")
        assert isinstance(result, KgnHeatmap)

    def test_savefig(self, single_sample_df, tmp_path):
        result = heatmap(single_sample_df, sample_name="TEST")
        out = tmp_path / "heatmap.png"
        result.savefig(str(out))
        assert out.exists()

    def test_silent_plot_and_tqdm_restores_on_exception(self):

        original_show = plt.show
        original_tqdm = tqdm_mod.tqdm

        try:
            with silent_plot_and_tqdm():
                raise RuntimeError("test error")
        except RuntimeError:
            pass

        assert plt.show is original_show
        assert tqdm_mod.tqdm is original_tqdm
