import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, Tuple, Union, List
from pathlib import Path
import shutil
from kegganog.grouped_heatmap import function_groups
from .base import KgnPlotBase


class KgnStackedBarplot(KgnPlotBase):
    pass


def stacked_barplot(
    df,
    figsize: Tuple[int, int] = (14, 7),
    cmap: Optional[Union[str, List[str]]] = "tab20",
    bar_width: float = 0.6,
    edgecolor: str = "black",
    edge_linewidth: float = 0.3,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: str = "Samples",
    xlabel_fontsize: float = 12.0,
    xlabel_color: str = "black",
    xlabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel: str = "Total Completeness",
    ylabel_fontsize: float = 12.0,
    ylabel_color: str = "black",
    ylabel_weight: str = "normal",
    ylabel_style: str = "normal",
    xticks_rotation: float = 0.0,
    xticks_ha: str = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: str = "normal",
    xticks_style: str = "normal",
    background_color="white",
    grid: bool = True,
    grid_linestyle: str = "--",
    grid_alpha: float = 0.7,
    legend_fontsize: float = 9.0,
    legend_loc: str = "upper left",
    legend_bbox: Tuple[float, float] = (1.05, 1),
    show_legend: bool = True,
):
    """
    Generates a customizable stacked bar plot showing pathway group completeness values across samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - cmap: Colormap name (str) or list of colors.
    - bar_width: Width parameter for bars.
    - edgecolor: Color of the edges (borders) drawn around each stacked area in the stacked barplot.
    - edge_linewidth: Width of the edge lines around each stacked area.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - xlabel, ylabel: Axis labels.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_rotation, xticks_ha: Rotation angle and alignment of x-axis tick labels.
    - xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-axis tick label styling.
    - background_color: Background color of the figure.
    - grid: Whether to display a grid.
    - grid_color, grid_linestyle, grid_alpha: Grid styling.
    - legend_fontsize: Font size for legend labels.
    - legend_loc: Position of the legend.
    - legend_bbox: Position of the legend box.
    - show_legend: Whether to display the legend.

    Returns:
    - KgnStackedBarplot: An object containing the boxplot figure and axis for customization or saving.
    """

    function_to_group = {
        func.lower(): group
        for group, functions in function_groups.items()
        for func in functions
    }

    df = df.copy()
    df["Group"] = df["Function"].str.lower().map(function_to_group)
    df_grouped = df.dropna(subset=["Group"])
    df_grouped_sum = df_grouped.groupby("Group").sum(numeric_only=True)
    df_plot = df_grouped_sum.T

    # Handle colors
    if isinstance(cmap, list):
        colors = cmap
    else:
        colors = sns.color_palette(cmap, n_colors=len(df_plot.columns))

    # Plot
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)
    df_plot.plot(
        kind="bar",
        stacked=True,
        color=colors,
        ax=ax,
        edgecolor=edgecolor,
        linewidth=edge_linewidth,
        width=bar_width,
        zorder=3,
    )

    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )
    ax.set_xlabel(
        xlabel,
        fontsize=xlabel_fontsize,
        color=xlabel_color,
        weight=xlabel_weight,
        style=xlabel_style,
    )
    ax.set_ylabel(
        ylabel,
        fontsize=ylabel_fontsize,
        color=ylabel_color,
        weight=ylabel_weight,
        style=ylabel_style,
    )

    if show_legend:
        ax.legend(
            title="Pathway Group",
            bbox_to_anchor=legend_bbox,
            loc=legend_loc,
            fontsize=legend_fontsize,
        )

    if grid:
        ax.grid(axis="y", linestyle=grid_linestyle, alpha=grid_alpha, zorder=0)

    # Customize x-ticks
    positions = np.arange(len(df_plot.index))
    labels = df_plot.index.tolist()
    plt.xticks(
        positions,
        labels,
        rotation=xticks_rotation,
        ha=xticks_ha,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xticks_weight,
        style=xticks_style,
    )

    ax.set_xlim(-0.5, len(df_plot.index) - 0.5)

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnStackedBarplot(fig, ax)
