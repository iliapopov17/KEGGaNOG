import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from kegganog.grouped_heatmap import function_groups


def generate_grouped_heatmap_multi(kegg_decoder_file, output_folder, dpi, color):
    with tqdm(total=6, desc="Preparing heatmap data") as pbar:
        kegg_decoder_file["Group"] = kegg_decoder_file["Function"].apply(
            lambda x: next(
                (group for group, funcs in function_groups.items() if x in funcs),
                "Miscellaneous",
            )
        )
        pbar.update(1)

        kegg_decoder_file = kegg_decoder_file.sort_values(
            by=["Group", "Function"]
        ).reset_index(drop=True)
        pbar.update(1)

        kegg_decoder_file["Function"] = pd.Categorical(
            kegg_decoder_file["Function"],
            categories=kegg_decoder_file["Function"],
            ordered=True,
        )
        pbar.update(1)

        # Define the group ranges for each part
        part1_groups = [
            "Amino acid metabolism",
            "Arsenic reduction",
            "Bacterial secretion systems",
            "Biofilm formation",
            "Carbohydrate metabolism",
            "Photosynthesis",
        ]
        part2_groups = [
            "Carbon degradation",
            "Carbon fixation",
            "Cell mobility",
            "Genetic competence",
            "Hydrogen redox",
            "Metal transporters",
            "Methanogenesis",
            "Miscellaneous",
        ]
        part3_groups = [
            "Nitrogen metabolism",
            "Oxidative phosphorylation",
            "Sulfur metabolism",
            "Transporters",
            "Vitamin biosynthesis",
        ]

        # Split the dataframe into 3 parts based on the groupings
        part1 = kegg_decoder_file[
            kegg_decoder_file["Group"].isin(part1_groups)
        ].reset_index(drop=True)
        pbar.update(1)
        part2 = kegg_decoder_file[
            kegg_decoder_file["Group"].isin(part2_groups)
        ].reset_index(drop=True)
        pbar.update(1)
        part3 = kegg_decoder_file[
            kegg_decoder_file["Group"].isin(part3_groups)
        ].reset_index(drop=True)
        pbar.update(1)

    # Function to add empty rows between groups
    with tqdm(total=6, desc="Adding split between groups") as pbar:

        def add_empty_rows(df, groups):
            new_rows = []
            for group in groups:
                group_rows = df[df["Group"] == group]
                new_rows.append(group_rows)
                # Add an empty row if this is not the last group
                if group != groups[-1]:
                    # Create an empty row with 'split' in the 'Function' column
                    empty_row = pd.DataFrame(
                        [["split_" + f"{group}"] + [np.nan] * (df.shape[1] - 1)],
                        columns=df.columns,
                    )  # First column is 'Function'
                    # empty_row['Group'] = 'split'  # Set the group to 'split'
                    new_rows.append(empty_row)  # Append the empty row
            return pd.concat(new_rows, ignore_index=True)

        part1 = add_empty_rows(
            kegg_decoder_file[kegg_decoder_file["Group"].isin(part1_groups)],
            part1_groups,
        ).reset_index(drop=True)
        pbar.update(1)
        part2 = add_empty_rows(
            kegg_decoder_file[kegg_decoder_file["Group"].isin(part2_groups)],
            part2_groups,
        ).reset_index(drop=True)
        pbar.update(1)
        part3 = add_empty_rows(
            kegg_decoder_file[kegg_decoder_file["Group"].isin(part3_groups)],
            part3_groups,
        ).reset_index(drop=True)
        pbar.update(1)

        part1["Function"] = pd.Categorical(
            part1["Function"], categories=part1["Function"], ordered=True
        )
        pbar.update(1)
        part2["Function"] = pd.Categorical(
            part2["Function"], categories=part2["Function"], ordered=True
        )
        pbar.update(1)
        part3["Function"] = pd.Categorical(
            part3["Function"], categories=part3["Function"], ordered=True
        )
        pbar.update(1)

    fig_w = 0.5 * (part1.shape[1] - 2) + 27.5
    left_pad = (
        0.20 - 0.0020833 * (part1.shape[1] - 2) + 0.0020833 * (part1.shape[1] - 2) ** 2
    )

    # Create heatmaps for each part
    fig, axes = plt.subplots(1, 3, figsize=(fig_w, 20))
    cbar_ax = fig.add_axes([0.92, 0.4, 0.02, 0.2])

    plt.subplots_adjust(left=left_pad, right=0.85, wspace=0.4)

    def add_group_labels(axes, part, group_labels):
        for i, group in enumerate(group_labels):
            group_indices = np.where(part["Group"] == group)[0]
            if len(group_indices) > 0:
                y_position = np.mean(group_indices) + 0.5
                x_position = -(left_pad / 2)
                axes.text(
                    x_position,
                    y_position,
                    group,
                    fontsize=12,
                    ha="right",
                    va="center",
                    weight="bold",
                    bbox=dict(
                        boxstyle="round,pad=0.3", edgecolor="none", facecolor="white"
                    ),
                )

    def plot_heatmap(part, group_labels, ax, cbar, cbar_ax=None, cbar_kws=None):
        # Create the pivot table
        value_columns = part.columns[
            1:-1
        ]  # Adjust this based on your DataFrame structure

        # Fill NaN values in the selected columns
        part[value_columns] = part[value_columns].fillna(0)

        pivot_table = part.pivot_table(
            values=value_columns,
            index="Function",
            aggfunc="mean",
            fill_value=0,
            observed=False,
        )

        # Create a mask for rows starting with 'split_'
        mask = pivot_table.index.str.startswith("split_")

        # Create the heatmap
        sns.heatmap(
            pivot_table,
            cmap=f"{color}",
            annot=False,
            linewidths=0.5,
            ax=ax,
            cbar=cbar,
            cbar_ax=cbar_ax,
            cbar_kws=cbar_kws,
            # square=True,
            mask=np.tile(mask[:, None], (1, pivot_table.shape[1])),
        )
        ax.tick_params(axis="y", labelrotation=0)
        add_group_labels(ax, part, group_labels)

        # Hide ticks and labels for rows starting with 'split_'
        for tick, label in zip(ax.yaxis.get_major_ticks(), ax.get_yticklabels()):
            if label.get_text().startswith("split_"):
                label.set_visible(False)  # Hide the label
                tick.set_visible(False)  # Hide the tick completely
                tick.tick1line.set_visible(False)  # Hide major tick mark
                tick.tick2line.set_visible(False)  # Hide minor tick mark

    with tqdm(total=3, desc="Creating heatmap parts") as pbar:
        # Plot for Part 1
        plot_heatmap(part1, part1_groups, axes[0], cbar=False)
        axes[0].set_title("Part 1")
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

        # Plot for Part 2
        plot_heatmap(part2, part2_groups, axes[1], cbar=False)
        axes[1].set_title("Part 2")
        axes[1].tick_params(axis="x", rotation=45)
        axes[1].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

        # Plot for Part 3
        plot_heatmap(
            part3,
            part3_groups,
            axes[2],
            cbar=True,
            cbar_ax=cbar_ax,
            cbar_kws={"label": "Pathway completeness"},
        )
        axes[2].set_title("Part 3")
        axes[2].tick_params(axis="x", rotation=45)
        axes[2].set_xticklabels(axes[0].get_xticklabels(), ha="right")
        pbar.update(1)

    # Y-axis labels adjustments
    axes[0].set_ylabel("")
    axes[1].set_ylabel("")
    axes[2].set_ylabel("")

    # Adjusting function labels to the right
    for ax in axes:
        ax.yaxis.tick_right()  # Move y-ticks to the right
        ax.set_yticklabels(
            ax.get_yticklabels(), rotation=0, va="center", ha="left"
        )  # Align labels

    # Layout adjustments
    plt.tight_layout(rect=[0, 0, 0.9, 1])
    output_file = os.path.join(output_folder, "heatmap_figure.png")
    with tqdm(total=1, desc="Saving plot") as pbar:
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
        pbar.update(1)
    plt.show()
