from pathlib import Path
from typing import Optional, Tuple, Union
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
import pandas as pd
from .base import KgnPlotBase


class KgnBoxplot(KgnPlotBase):
    pass


def boxplot(
    df,
    figsize: Tuple[int, int] = (12, 6),
    color: Optional[str] = "blue",
    showfliers: bool = True,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: str = "Samples",
    xlabel_fontsize: float = 14.0,
    xlabel_color: str = "black",
    xlabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel: str = "Completeness Value",
    ylabel_fontsize: float = 14.0,
    ylabel_color: str = "black",
    ylabel_weight: str = "normal",
    ylabel_style: str = "normal",
    xticks_rotation: float = 45.0,
    xticks_ha: str = "center",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: str = "normal",
    xticks_style: str = "normal",
    yticks_fontsize: float = 12.0,
    yticks_color: str = "black",
    yticks_weight: str = "normal",
    yticks_style: str = "normal",
    grid: bool = True,
    grid_color: str = "gray",
    grid_linestyle: str = "--",
    grid_linewidth: float = 0.5,
    background_color: str = "white",
):
    """
    Generates a customizable boxplot to visualize the distribution of pathway completeness across samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - color: Color used for all boxes in the plot. Can be a named color (e.g., "blue"), hex code (e.g., "#1f77b4").
    - showfliers: Whether to display outlier points.
    - title: Main title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title text styling.
    - xlabel, ylabel: Axis labels.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_rotation, xticks_ha: Rotation angle and alignment of x-axis tick labels.
    - xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-axis tick label styling.
    - yticks_fontsize, yticks_color, yticks_weight, yticks_style: Y-axis tick label styling.
    - grid: Whether to display a grid.
    - grid_color, grid_linestyle, grid_linewidth: Grid styling.
    - background_color: Background color of the figure.

    Returns:
    - KgnBoxplot: An object containing the boxplot figure and axis for customization or saving.
    """

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    # Create boxplot
    sns.boxplot(data=df.iloc[:, 1:], color=color, showfliers=showfliers, ax=ax)

    # Customize title
    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )

    # Customize x-axis label
    ax.set_xlabel(
        xlabel,
        fontsize=xlabel_fontsize,
        color=xlabel_color,
        weight=xlabel_weight,
        style=xlabel_style,
    )

    # Customize y-axis label
    ax.set_ylabel(
        ylabel,
        fontsize=ylabel_fontsize,
        color=ylabel_color,
        weight=ylabel_weight,
        style=ylabel_style,
    )

    # Customize x-ticks
    plt.xticks(
        rotation=xticks_rotation,
        ha=xticks_ha,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xticks_weight,
        style=xticks_style,
    )

    # Customize y-ticks
    plt.yticks(
        fontsize=yticks_fontsize,
        color=yticks_color,
        weight=yticks_weight,
        style=yticks_style,
    )

    # Grid settings
    if grid:
        plt.grid(color=grid_color, linestyle=grid_linestyle, linewidth=grid_linewidth)

    # Clean up __pycache__
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnBoxplot(fig, ax)
