import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm


# Function to generate the heatmap
def generate_heatmap_multi(kegg_decoder_file, output_folder, dpi, color, figsize=None):
    print("Generating heatmap...")

    # Process data for heatmap with progress bar
    with tqdm(total=3, desc="Preparing heatmap data") as pbar:
        df = pd.DataFrame(kegg_decoder_file)
        pbar.update(1)

        # Split into three parts for separate heatmaps
        # df1, df2, df3 = np.array_split(df, 3) - DEPRECATED

        # Get the number of rows
        num_rows = len(df)

        # Calculate the split indices for 3 parts
        split_size = num_rows // 3

        # Split the dataframe manually
        df1 = df.iloc[:split_size]
        df2 = df.iloc[split_size : 2 * split_size]
        df3 = df.iloc[2 * split_size :]
        pbar.update(2)

    fig_w = 0.5 * (df.shape[1] - 2) + 19.5
    if figsize is None:
        figsize = (fig_w, 20)

    # Create a grid for the heatmap and colorbar
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    cbar_ax = fig.add_axes([0.92, 0.4, 0.02, 0.2])  # Colorbar axis on the right

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

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    output_file = os.path.join(output_folder, "heatmap_figure.png")
    with tqdm(total=1, desc="Saving plot") as pbar:
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
        pbar.update(1)
    plt.show()

    return fig, axes
