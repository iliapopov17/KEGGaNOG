import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import re
import subprocess
import csv


# Function to parse eggnog-mapper output and prepare for KEGG-Decoder
def parse_emapper(input_file, temp_folder):
    # Read the input file
    df_filtered = pd.read_csv(input_file, sep="\t", skiprows=4)

    # Extract the 'KEGG_ko' column and clean it up
    df_kegg_ko = df_filtered[["KEGG_ko"]]
    df_kegg_ko = df_kegg_ko[df_kegg_ko["KEGG_ko"] != "-"]

    # Format the 'KEGG_ko' column for KEGG-Decoder
    df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(
        r"ko:(K\d+)", r"SAMPLE \1", regex=True
    )
    df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(",", "\n")

    # Save the parsed file with potential quotes
    parsed_file = os.path.join(temp_folder, "parsed.txt")
    df_kegg_ko.to_csv(
        parsed_file,
        sep="\t",
        index=False,
        header=False,
        quoting=csv.QUOTE_MINIMAL,
        escapechar="\\",
    )

    # Remove all quotation marks from the parsed file
    parsed_filtered_file = os.path.join(temp_folder, "parsed_filtered.txt")
    with open(parsed_file, "r") as file:
        content = file.read()

    # Replace any quotation marks
    content = content.replace('"', "")

    # Write the cleaned content to the parsed_filtered.txt file
    with open(parsed_filtered_file, "w") as file:
        file.write(content)

    return parsed_filtered_file


# Function to run KEGG-Decoder and process the output
def run_kegg_decoder(input_file, temp_folder):
    output_file = os.path.join(temp_folder, "output.list")

    # Run KEGG-Decoder via subprocess
    subprocess.run(
        ["KEGG-decoder", "-i", input_file, "-o", output_file, "-v", "static"]
    )

    return output_file


# Function to generate the heatmap
def generate_heatmap(kegg_decoder_file, output_folder, dpi, sample_name):
    # Read the KEGG-Decoder output
    with open(kegg_decoder_file, "r") as file:
        lines = file.readlines()

    # Prepare the dataframe
    header = lines[0].strip().split("\t")
    values = lines[1].strip().split("\t")
    data = {"Function": header[1:], sample_name: [float(v) for v in values[1:]]}
    df = pd.DataFrame(data)

    # Split into parts for separate heatmaps
    df1, df2, df3 = np.array_split(df, 3)

    # Rename the 'SAMPLE' column to 'Lpb. plantarum IS-10506'
    df1 = df1.rename(columns={"SAMPLE": rf"{sample_name}"})
    df2 = df2.rename(columns={"SAMPLE": rf"{sample_name}"})
    df3 = df3.rename(columns={"SAMPLE": rf"{sample_name}"})

    # Create a grid for the heatmap and colorbar
    fig, axes = plt.subplots(1, 3, figsize=(20, 20))
    cbar_ax = fig.add_axes([0.92, 0.4, 0.02, 0.2])  # Colorbar axis on the right

    # Plot each part
    sns.heatmap(
        df1.pivot_table(values=sample_name, index="Function", fill_value=0),
        cmap="Blues",
        annot=True,
        linewidths=0.5,
        ax=axes[0],
        cbar=False,
    )
    axes[0].set_title("Part 1")

    sns.heatmap(
        df2.pivot_table(values=sample_name, index="Function", fill_value=0),
        cmap="Blues",
        annot=True,
        linewidths=0.5,
        ax=axes[1],
        cbar=False,
    )
    axes[1].set_title("Part 2")

    sns.heatmap(
        df3.pivot_table(values=sample_name, index="Function", fill_value=0),
        cmap="Blues",
        annot=True,
        linewidths=0.5,
        ax=axes[2],
        cbar_ax=cbar_ax,
    )
    axes[2].set_title("Part 3")

    axes[1].set_ylabel("")
    axes[2].set_ylabel("")

    # Set layout and save the figure
    plt.tight_layout(rect=[0, 0, 0.9, 1])
    output_file = os.path.join(output_folder, "heatmap_figure.png")
    plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    plt.show()


# Main function to run the tool
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="KEGGaNOG: Link eggnog-mapper and KEGG-Decoder for pathway visualization."
    )
    parser.add_argument("--i", required=True, help="Path to eggnog-mapper output file")
    parser.add_argument("--o", required=True, help="Output folder to save results")
    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI for the output image (default: 300)"
    )
    parser.add_argument(
        "--n", default="SAMPLE", help="Sample name for labeling (default: SAMPLE)"
    )

    args = parser.parse_args()

    # Create output and temporary directories
    os.makedirs(args.o, exist_ok=True)
    temp_folder = os.path.join(args.o, "temp_files")
    os.makedirs(temp_folder, exist_ok=True)

    # Step 1: Parse eggnog-mapper output
    parsed_filtered_file = parse_emapper(args.i, temp_folder)

    # Step 2: Run KEGG-Decoder
    kegg_decoder_file = run_kegg_decoder(parsed_filtered_file, temp_folder)

    # Step 3: Generate the heatmap
    generate_heatmap(kegg_decoder_file, args.o, args.dpi, args.n)

    print(f"Heatmap saved in {args.o}")


if __name__ == "__main__":
    main()
