import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

function_groups = {
    "Carbon fixation": [
        "3-Hydroxypropionate Bicycle",
        "4-Hydroxybutyrate/3-hydroxypropionate",
        "CBB Cycle",
        "gluconeogenesis",
        "rTCA Cycle",
        "RuBisCo",
        "Wood-Ljungdahl",
    ],
    "Carbohydrate metabolism": [
        "Entner-Doudoroff Pathway",
        "glycolysis",
        "Sulfolipid biosynthesis",
        "TCA Cycle",
        "Glyoxylate shunt",
        "Mixed acid: Acetate",
        "Mixed acid: Ethanol, Acetate to Acetylaldehyde",
        "Mixed acid: Ethanol, Acetyl-CoA to Acetylaldehyde (reversible)",
        "Mixed acid: Ethanol, Acetylaldehyde to Ethanol",
        "Mixed acid: Formate",
        "Mixed acid: Formate to CO2 & H2",
        "Mixed acid: Lactate",
        "Mixed acid: PEP to Succinate via OAA, malate & fumarate",
        "alpha-amylase",
        "polyhydroxybutyrate synthesis",
        "starch/glycogen degradation",
        "starch/glycogen synthesis",
    ],
    "Carbon degradation": [
        "beta-glucosidase",
        "beta-N-acetylhexosaminidase",
        "chitinase",
        "D-galacturonate epimerase",
        "D-galacturonate isomerase",
        "diacetylchitobiose deacetylase",
        "glucoamylase",
        "pullulanase",
        "DMS dehydrogenase",
        "DMSP demethylation",
        "Naphthalene degradation to salicylate",
        "alcohol oxidase",
        "basic endochitinase B",
        "bifunctional chitinase/lysozyme",
        "cellulase",
        "dimethylamine/trimethylamine dehydrogenase",
        "oligogalacturonide lyase",
        "pectinesterase",
        "soluble methane monooxygenase",
    ],
    "Nitrogen metabolism": [
        "dissim nitrate reduction",
        "DNRA",
        "nitric oxide reduction",
        "nitrite oxidation",
        "nitrite reduction",
        "nitrogen fixation",
        "nitrous-oxide reduction",
        "ammonia oxidation (amo/pmmo)",
        "hydrazine dehydrogenase",
        "hydrazine synthase",
        "hydroxylamine oxidation",
    ],
    "Sulfur metabolism": [
        "alt thiosulfate oxidation tsdA",
        "dissimilatory sulfate < > APS",
        "dissimilatory sulfite < > APS",
        "dissimilatory sulfite < > sulfide",
        "DMSO reductase",
        "sulfide oxidation",
        "sulfite dehydrogenase",
        "sulfite dehydrogenase (quinone)",
        "sulfur dioxygenase",
        "thiosulfate oxidation",
        "thiosulfate/polysulfide reductase",
        "alt thiosulfate oxidation doxAD",
        "sulfhydrogenase",
        "sulfur assimilation",
        "sulfur disproportionation",
        "sulfur reductase sreABC",
    ],
    "Oxidative phosphorylation": [
        "Cytochrome bd complex",
        "Cytochrome c oxidase",
        "Cytochrome c oxidase, cbb3-type",
        "F-type ATPase",
        "Na-NADH-ubiquinone oxidoreductase",
        "NADH-quinone oxidoreductase",
        "Ubiquinol-cytochrome c reductase",
        "V-type ATPase",
        "Cytochrome aa3-600 menaquinol oxidase",
        "Cytochrome b6/f complex",
        "Cytochrome o ubiquinol oxidase",
        "NAD(P)H-quinone oxidoreductase",
    ],
    "Hydrogen redox": [
        "NAD-reducing hydrogenase",
        "NiFe hydrogenase Hyd-1",
        "Coenzyme B/Coenzyme M regeneration",
        "Coenzyme M reduction to methane",
        "NADP-reducing hydrogenase",
        "NiFe hydrogenase",
        "ferredoxin hydrogenase",
        "hydrogen:quinone oxidoreductase",
        "membrane-bound hydrogenase",
    ],
    "Amino acid metabolism": [
        "arginine",
        "asparagine",
        "glutamine",
        "histidine",
        "lysine",
        "serine",
        "threonine",
        "Serine pathway/formaldehyde assimilation",
        "alanine",
        "aspartate",
        "cysteine",
        "glutamate",
        "glycine",
        "isoleucine",
        "leucine",
        "methionine",
        "phenylalanine",
        "proline",
        "tryptophan",
        "tyrosine",
        "valine",
    ],
    "Vitamin biosynthesis": [
        "cobalamin biosynthesis",
        "riboflavin biosynthesis",
        "thiamin biosynthesis",
        "MEP-DOXP pathway",
        "Retinal biosynthesis",
        "Retinal from apo-carotenals",
        "carotenoids backbone biosynthesis",
        "end-product astaxanthin",
        "end-product myxoxanthophylls",
        "end-product nostoxanthin",
        "end-product zeaxanthin diglucoside",
        "mevalonate pathway",
    ],
    "Cell mobility": ["Chemotaxis", "Flagellum", "Adhesion"],
    "Biofilm formation": [
        "Biofilm PGA Synthesis protein",
        "Biofilm regulator BssS",
        "Colanic acid and Biofilm protein A",
        "Colanic acid and Biofilm transcriptional regulator",
        "Curli fimbriae biosynthesis",
    ],
    "Bacterial secretion systems": [
        "Sec-SRP",
        "Twin Arginine Targeting",
        "Type I Secretion",
        "Type II Secretion",
        "Type III Secretion",
        "Type IV Secretion",
        "Type Vabc Secretion",
        "Type VI Secretion",
    ],
    "Transporters": [
        "transporter: phosphate",
        "transporter: phosphonate",
        "transporter: thiamin",
        "transporter: urea",
        "C-P lyase cleavage PhnJ",
        "CP-lyase complex",
        "CP-lyase operon",
        "bidirectional polyphosphate",
        "transporter: vitamin B12",
    ],
    "Metal transporters": [
        "Cobalt transporter CbiMQ",
        "Cobalt transporter CorA",
        "Copper transporter CopA",
        "Fe-Mn transporter MntH",
        "Ferric iron ABC-type substrate-binding AfuA",
        "Ferrous iron transporter FeoB",
        "Cobalt transporter CbtA",
        "Nickel ABC-type substrate-binding NikA",
    ],
    "Arsenic reduction": ["Arsenic reduction"],
    "Methanogenesis": [
        "Methanogenesis via CO2",
        "Methanogenesis via acetate",
        "Methanogenesis via dimethylamine",
        "Methanogenesis via dimethylsulfide, methanethiol, methylpropanoate",
        "Methanogenesis via methanol",
        "Methanogenesis via methylamine",
        "Methanogenesis via trimethylamine",
    ],
    "Photosynthesis": [
        "Photosystem I",
        "Photosystem II",
        "anoxygenic type-I reaction center",
        "anoxygenic type-II reaction center",
    ],
    "Genetic competence": [
        "Competence factors",
        "Competence-related core components",
        "Competence-related related components",
    ],
    "Miscellaneous": [
        "Soluble methane monooxygenase",
        "Naphthalene degradation to salicylate",
        "alcohol oxidase",
        "DMS dehydrogenase",
        "ferredoxin hydrogenase",
    ],
}


# Function to generate groupped heatmap
def generate_grouped_heatmap(
    kegg_decoder_file, output_folder, dpi, color, sample_name, figsize=None, annot=True
):

    # Read the KEGG-Decoder output
    with open(kegg_decoder_file, "r") as file:
        lines = file.readlines()

    # Prepare the dataframe
    with tqdm(total=4, desc="Preparing heatmap data") as pbar:
        header = lines[0].strip().split("\t")
        values = lines[1].strip().split("\t")
        data = {"Function": header[1:], sample_name: [float(v) for v in values[1:]]}
        df = pd.DataFrame(data)
        pbar.update(1)

        function_groups_lower = {
            group: {func.lower() for func in funcs}
            for group, funcs in function_groups.items()
        }

        df["Group"] = df["Function"].apply(
            lambda x: next(
                (
                    group
                    for group, funcs in function_groups_lower.items()
                    if x.lower() in funcs
                ),
                "Miscellaneous",
            )
        )

        df = df.sort_values(by=["Group", "Function"]).reset_index(drop=True)

        df["Function"] = pd.Categorical(
            df["Function"], categories=df["Function"], ordered=True
        )

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
        part1 = df[df["Group"].isin(part1_groups)].reset_index(drop=True)
        pbar.update(1)
        part2 = df[df["Group"].isin(part2_groups)].reset_index(drop=True)
        pbar.update(1)
        part3 = df[df["Group"].isin(part3_groups)].reset_index(drop=True)
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
            df[df["Group"].isin(part1_groups)], part1_groups
        ).reset_index(drop=True)
        pbar.update(1)
        part2 = add_empty_rows(
            df[df["Group"].isin(part2_groups)], part2_groups
        ).reset_index(drop=True)
        pbar.update(1)
        part3 = add_empty_rows(
            df[df["Group"].isin(part3_groups)], part3_groups
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

    if figsize is None:
        figsize = (28, 20)

    # Create heatmaps for each part
    fig, axes = plt.subplots(
        1, 3, figsize=figsize
    )  # Adjust height for better visualization
    cbar_ax = fig.add_axes([0.92, 0.4, 0.02, 0.2])  # Colorbar axis on the right

    # Adjust the layout to make room for group labels
    plt.subplots_adjust(
        left=0.15, right=0.85, wspace=0.4
    )  # Adjust left, right, and space between plots

    # Function to add group labels to heatmap, now aligned to the right
    def add_group_labels(axes, part, group_labels):
        for i, group in enumerate(group_labels):
            group_indices = np.where(part["Group"] == group)[0]
            if len(group_indices) > 0:
                y_position = np.mean(group_indices) + 0.5  # Center the label vertically
                x_position = -0.075  # Position group labels to the left of the heatmap
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

    # Mask rows starting with 'split_' and hide y-tick labels for these rows
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
            annot=annot,
            linewidths=0.5,
            ax=ax,
            cbar=cbar,
            cbar_ax=cbar_ax,
            cbar_kws=cbar_kws,
            mask=np.tile(
                mask[:, None], (1, pivot_table.shape[1])
            ),  # Mask the entire row for 'split_'
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
        pbar.update(1)

        # Plot for Part 2
        plot_heatmap(part2, part2_groups, axes[1], cbar=False)
        axes[1].set_title("Part 2")
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

    return fig, axes
