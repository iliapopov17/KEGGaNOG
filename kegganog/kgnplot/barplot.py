import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Union
import shutil
from pathlib import Path
from .base import KgnPlotBase


class KgnBarplot(KgnPlotBase):
    pass


def barplot(
    df,
    figsize: Tuple[int, int] = (8, 12),
    cmap: Optional[Union[str, list]] = "Greens",
    cmap_range: Tuple[int, int] = (8, 30),
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: str = "Pathway completeness",
    xlabel_fontsize: float = 14.0,
    xlabel_color: str = "black",
    xlabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel: str = "Pathway",
    ylabel_fontsize: float = 14.0,
    ylabel_color: str = "black",
    ylabel_weight: str = "normal",
    ylabel_style: str = "normal",
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xticks_weight: str = "normal",
    xticks_style: str = "normal",
    yticks_fontsize: float = 12.0,
    yticks_color: str = "black",
    yticks_weight: str = "normal",
    yticks_style: str = "normal",
    grid: bool = True,
    grid_linestyle: str = "--",
    grid_alpha: float = 0.7,
    background_color: str = "white",
    sort_order: str = "descending",
):
    """
    Generates a customizable horizontal barplot showing pathway completeness.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - cmap: Colormap name (str) or list of colors.
    - cmap_range: Tuple (start, end) to subset the colormap.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - xlabel, ylabel: Labels for axes.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_fontsize, xticks_color, xticks_weight, xticks_style: X-ticks styling.
    - yticks_fontsize, yticks_color, yticks_weight, yticks_style: Y-ticks styling.
    - grid: Whether to show grid lines.
    - grid_linestyle, grid_alpha: Grid styling.
    - background_color: Figure background color.
    - sort_order: "ascending" or "descending" sort of completeness scores.

    Returns:
    - KgnBarplot: An object containing the radar plot figure and axis for customization or saving.
    """

    # Load and process data
    df = df.drop(columns=["Function"], errors="ignore")
    df = df.loc[:, (df > 0).any(axis=0)]
    df_melted = df.melt(var_name="Pathway", value_name="Score")

    # Sort by score
    df_melted = df_melted.sort_values(
        by="Score", ascending=(sort_order == "ascending")
    ).reset_index(drop=True)

    # Capitalize lowercase pathway names
    df_melted["Pathway"] = df_melted["Pathway"].apply(
        lambda x: x.capitalize() if isinstance(x, str) and x.islower() else x
    )

    # Set figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    # Color palette
    if isinstance(cmap, str):
        palette = sns.color_palette(cmap, n_colors=cmap_range[1])[cmap_range[0] :]
    else:
        palette = cmap

    sns.barplot(
        data=df_melted,
        x="Score",
        y="Pathway",
        hue="Score",
        palette=palette,
        dodge=False,
        legend=False,
        ax=ax,
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

    for label in ax.get_xticklabels():
        label.set_fontsize(xticks_fontsize)
        label.set_color(xticks_color)
        label.set_weight(xticks_weight)
        label.set_style(xticks_style)

    for label in ax.get_yticklabels():
        label.set_fontsize(yticks_fontsize)
        label.set_color(yticks_color)
        label.set_weight(yticks_weight)
        label.set_style(yticks_style)

    if grid:
        ax.grid(axis="x", linestyle=grid_linestyle, alpha=grid_alpha, zorder=0)

    ax.invert_yaxis()
    ax.set_xlim(0, 1.0)
    ax.set_axisbelow(True)

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnBarplot(fig, ax)
