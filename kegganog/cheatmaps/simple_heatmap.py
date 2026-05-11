import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

from .heatmaps_common import (
    create_three_panel_heatmap_figure,
    save_heatmap_png,
    split_dataframe_into_three_row_segments,
)


# Function to generate the heatmap
def generate_heatmap(
    kegg_decoder_file, output_folder, dpi, color, sample_name, figsize=None, annot=True
):

    # Read the KEGG-Decoder output
    with open(kegg_decoder_file, "r") as file:
        lines = file.readlines()

    # Process data for heatmap with progress bar
    with tqdm(total=3, desc="Preparing heatmap data") as pbar:
        header = lines[0].strip().split("\t")
        values = lines[1].strip().split("\t")
        data = {"Function": header[1:], sample_name: [float(v) for v in values[1:]]}
        df = pd.DataFrame(data)
        pbar.update(1)

        df1, df2, df3 = split_dataframe_into_three_row_segments(df)
        pbar.update(2)

    if figsize is None:
        figsize = (20, 20)

    fig, axes, cbar_ax = create_three_panel_heatmap_figure(figsize)

    with tqdm(total=3, desc="Creating heatmap parts") as pbar:
        sns.heatmap(
            df1.pivot_table(values=sample_name, index="Function", fill_value=0),
            cmap=f"{color}",
            annot=annot,
            linewidths=0.5,
            ax=axes[0],
            cbar=False,
        )
        axes[0].set_title("Part 1")
        pbar.update(1)

        sns.heatmap(
            df2.pivot_table(values=sample_name, index="Function", fill_value=0),
            cmap=f"{color}",
            annot=annot,
            linewidths=0.5,
            ax=axes[1],
            cbar=False,
        )
        axes[1].set_title("Part 2")
        pbar.update(1)

        sns.heatmap(
            df3.pivot_table(values=sample_name, index="Function", fill_value=0),
            cmap=f"{color}",
            annot=annot,
            linewidths=0.5,
            ax=axes[2],
            cbar_ax=cbar_ax,
            cbar_kws={"label": "Pathway completeness"},
        )
        axes[2].set_title("Part 3")
        pbar.update(1)

        axes[1].set_ylabel("")
        axes[2].set_ylabel("")

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    save_heatmap_png(output_folder, dpi)

    return fig, axes
