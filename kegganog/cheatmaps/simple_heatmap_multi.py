import logging
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from .heatmaps_common import (
    create_three_panel_heatmap_figure,
    save_heatmap_png,
    split_dataframe_into_three_row_segments,
)

_log = logging.getLogger(__name__)


# Function to generate the heatmap
def generate_heatmap_multi(kegg_decoder_file, output_folder, dpi, color, figsize=None):
    _log.info("Generating heatmap...")

    # Process data for heatmap with progress bar
    with tqdm(total=3, desc="Preparing heatmap data") as pbar:
        df = pd.DataFrame(kegg_decoder_file)
        pbar.update(1)

        df1, df2, df3 = split_dataframe_into_three_row_segments(df)
        pbar.update(2)

    fig_w = 0.5 * (df.shape[1] - 2) + 19.5
    if figsize is None:
        figsize = (fig_w, 20)

    fig, axes, cbar_ax = create_three_panel_heatmap_figure(figsize)

    with tqdm(total=3, desc="Creating heatmap parts") as pbar:
        sns.heatmap(
            df1.set_index("Function"),
            cmap=f"{color}",
            annot=False,
            linewidths=0.5,
            ax=axes[0],
            cbar=False,
        )
        axes[0].set_title("Part 1")
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

        sns.heatmap(
            df2.set_index("Function"),
            cmap=f"{color}",
            annot=False,
            linewidths=0.5,
            ax=axes[1],
            cbar=False,
        )
        axes[1].set_title("Part 2")
        axes[1].tick_params(axis="x", rotation=45)
        axes[1].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

        sns.heatmap(
            df3.set_index("Function"),
            cmap=f"{color}",
            annot=False,
            linewidths=0.5,
            ax=axes[2],
            cbar_ax=cbar_ax,
            cbar_kws={"label": "Pathway completeness"},
        )
        axes[2].set_title("Part 3")
        axes[2].tick_params(axis="x", rotation=45)
        axes[2].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

        axes[1].set_ylabel("")
        axes[2].set_ylabel("")

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=UserWarning, message=".*tight_layout.*"
        )
        plt.tight_layout(rect=(0, 0, 0.9, 1))
    save_heatmap_png(output_folder, dpi)

    return fig, axes
