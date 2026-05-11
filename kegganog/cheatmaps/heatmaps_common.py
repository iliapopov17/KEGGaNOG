"""Shared heatmap helpers and constants (single + multi, grouped layouts)."""

from __future__ import annotations

import os
from typing import Any, Sequence

import numpy as np
import pandas as pd
from tqdm import tqdm

# Group-category buckets for three-panel grouped heatmaps (must stay in lockstep).
GROUPED_PART1_GROUPS: list[str] = [
    "Amino acid metabolism",
    "Arsenic reduction",
    "Bacterial secretion systems",
    "Biofilm formation",
    "Carbohydrate metabolism",
    "Photosynthesis",
]
GROUPED_PART2_GROUPS: list[str] = [
    "Carbon degradation",
    "Carbon fixation",
    "Cell mobility",
    "Genetic competence",
    "Hydrogen redox",
    "Metal transporters",
    "Methanogenesis",
    "Miscellaneous",
]
GROUPED_PART3_GROUPS: list[str] = [
    "Nitrogen metabolism",
    "Oxidative phosphorylation",
    "Sulfur metabolism",
    "Transporters",
    "Vitamin biosynthesis",
]


def split_dataframe_into_three_row_segments(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split rows into three contiguous blocks (same floor-division logic as original)."""
    num_rows = len(df)
    split_size = num_rows // 3
    return (
        df.iloc[:split_size],
        df.iloc[split_size : 2 * split_size],
        df.iloc[2 * split_size :],
    )


def insert_split_rows_between_groups(
    df: pd.DataFrame, groups: Sequence[str]
) -> pd.DataFrame:
    """Insert spacer rows between group blocks (grouped heatmaps only)."""
    new_rows: list[pd.DataFrame] = []
    for group in groups:
        group_rows = df[df["Group"] == group]
        new_rows.append(group_rows)
        if group != groups[-1]:
            empty_row = pd.DataFrame(
                [["split_" + f"{group}"] + [np.nan] * (df.shape[1] - 1)],
                columns=df.columns,
            )
            new_rows.append(empty_row)
    return pd.concat(new_rows, ignore_index=True)


def create_three_panel_heatmap_figure(
    figsize: tuple[float, float],
) -> tuple[Any, Any, Any]:
    """One row of three axes plus a fixed colorbar axis (simple heatmaps)."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=figsize)
    cbar_ax = fig.add_axes([0.92, 0.4, 0.02, 0.2])
    return fig, axes, cbar_ax


def save_heatmap_png(output_folder: str, dpi: int) -> str:
    """Write ``heatmap_figure.png`` and show (matches original tqdm + savefig sequence)."""
    import matplotlib.pyplot as plt

    output_file = os.path.join(output_folder, "heatmap_figure.png")
    with tqdm(total=1, desc="Saving plot") as pbar:
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
        pbar.update(1)
    plt.show()
    return output_file
