import matplotlib.pyplot as plt
import numpy as np
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from .base import KgnPlotBase


class KgnRadar(KgnPlotBase):
    pass


def radarplot(
    df,
    pathways: List[str],
    figsize: Tuple[int, int] = (8, 8),
    colors: Optional[List[str]] = None,
    sample_order: Optional[List[str]] = None,
    title: Optional[str] = None,
    title_fontsize: float = 14.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    title_y: float = 1.1,
    label_fontsize: float = 10.0,
    label_color: str = "black",
    label_weight: str = "normal",
    label_style: str = "normal",
    label_background: Optional[str] = None,
    label_edgecolor: Optional[str] = None,
    label_pad: float = 1.05,
    ytick_fontsize: float = 8.0,
    ytick_color: str = "black",
    ytick_weight: str = "normal",
    ytick_alpha: float = 0.5,
    yticklabels: Optional[List[str]] = None,
    fill_alpha: float = 0.25,
    line_width: float = 2.0,
    line_style: str = "solid",
    background_color="white",
    legend_loc: str = "upper right",
    legend_bbox: Tuple[int, int] = (1.3, 1.1),
    show_legend: bool = True,
):
    """
    Generates a customizable radar (spider) plot for one or more KEGG pathways.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - pathways: List of pathway names to be plotted.
    - figsize: Tuple (width, height) of the figure.
    - colors: List of colors for each pathway. If None, default matplotlib colors are used.
    - sample_order: Optional list of sample names. If None, the columns of df will be used.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - title_y: Position of the title on the y-axis.
    - label_fontsize, label_color, label_weight,
      label_style, label_background, label_edgecolor, label_pad: label styling.
    - ytick_fontsize, ytick_color, ytick_weight, ytick_alpha: Y-axis tick label styling.
    - yticklabels: Custom list of labels for the y-axis ticks.
    - fill_alpha: Transparency of the filled areas.
    - line_width, line_style: Line styling.
    - background_color: Background color of the figure.
    - legend_loc: Location of the legend.
    - legend_bbox: Bounding box for the legend.
    - show_legend: Whether to display the legend.

    Returns:
    - KgnRadar: An object containing the radar plot figure and axis for customization or saving.
    """
    if len(pathways) > 4:
        raise ValueError("Maximum of 4 pathways can be plotted at once.")

    if sample_order is None:
        sample_order = [col for col in df.columns if col != "Function"]

    num_vars = len(sample_order)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=figsize, subplot_kw=dict(polar=True), facecolor=background_color
    )

    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # Plot data
    for i, function in enumerate(pathways):
        row = df[df["Function"] == function]
        if row.empty:
            print(f"Warning: Pathway '{function}' not found in DataFrame. Skipping.")
            continue
        values = row[sample_order].values.flatten().tolist()
        values += values[:1]

        ax.plot(
            angles,
            values,
            label=function,
            linewidth=line_width,
            linestyle=line_style,
            color=colors[i % len(colors)],
        )
        ax.fill(
            angles,
            values,
            color=colors[i % len(colors)],
            alpha=fill_alpha,
        )

    ax.set_xticks([])

    for angle in angles[:-1]:
        ax.plot(
            [angle, angle],
            [0, 1],
            color="lightgray",
            linewidth=1,
            linestyle="solid",
            zorder=0,
        )

    for angle, label in zip(angles[:-1], sample_order):
        ax.text(
            angle,
            label_pad,
            label,
            ha="center",
            va="center",
            fontsize=label_fontsize,
            color=label_color,
            fontweight=label_weight,
            style=label_style,
            bbox=(
                dict(
                    facecolor=label_background if label_background else "none",
                    edgecolor=label_edgecolor if label_edgecolor else "none",
                    boxstyle="round,pad=0.2",
                )
                if label_background or label_edgecolor
                else None
            ),
        )

    grid_vals = np.linspace(0.2, 1.0, 5)
    ax.set_yticks(grid_vals)
    ax.set_ylim(0, 1.0)

    if yticklabels is None:
        yticklabels = [""] * len(grid_vals)
        yticklabels[grid_vals.tolist().index(0.2)] = "0.2"
        yticklabels[grid_vals.tolist().index(1.0)] = "1.0"

    ax.set_yticklabels(
        yticklabels,
        fontsize=ytick_fontsize,
        color=ytick_color,
        fontweight=ytick_weight,
        alpha=ytick_alpha,
    )

    ax.set_yticks(grid_vals)
    ax.set_yticklabels(
        yticklabels,
        fontsize=ytick_fontsize,
        color=ytick_color,
        fontweight=ytick_weight,
        alpha=ytick_alpha,
    )

    plt.title(
        title,
        size=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
        y=title_y,
    )
    if show_legend:
        ax.legend(loc=legend_loc, bbox_to_anchor=legend_bbox)

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnRadar(fig, ax)
