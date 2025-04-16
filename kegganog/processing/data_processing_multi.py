import os
import subprocess
import csv
import pandas as pd
from tqdm import tqdm
import glob
from pathlib import Path
import io


# Function to parse eggnog-mapper output and prepare for KEGG-Decoder
def parse_emapper(input_file, sample_folder, file_prefix):
    print(f"Parsing {input_file}...")

    # Read the input file with progress bar
    with tqdm(total=1, desc=f"Reading {file_prefix}") as pbar:
        df_filtered = pd.read_csv(input_file, sep="\t", skiprows=4)
        pbar.update(1)

    # Check if 'KEGG_ko' column exists
    if "KEGG_ko" not in df_filtered.columns:
        raise KeyError(
            f"'KEGG_ko' column not found in {input_file}. Please check the file format."
        )

    # Filter the 'KEGG_ko' column
    df_kegg_ko = df_filtered[["KEGG_ko"]]
    df_kegg_ko = df_kegg_ko[df_kegg_ko["KEGG_ko"] != "-"]

    # Format 'KEGG_ko' column for KEGG-Decoder
    with tqdm(total=1, desc=f"Formatting {file_prefix}") as pbar:
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(
            r"ko:(K\d+)", rf"{file_prefix} \1", regex=True
        )
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(",", "\n")
        pbar.update(1)

        buffer = io.StringIO()
        df_kegg_ko.to_csv(
            buffer,
            sep="\t",
            index=False,
            header=False,
            quoting=csv.QUOTE_MINIMAL,
            escapechar="\\",
        )
        buffer.seek(0)

        # Read the CSV content into a string and remove quotes
        content = buffer.read().replace('"', "")
        pbar.update(1)

    parsed_filtered_file = os.path.join(
        sample_folder, f"{file_prefix}_parsed_KO_terms.txt"
    )
    with open(parsed_filtered_file, "w") as file:
        file.write(content)

    return parsed_filtered_file


# Function to run KEGG-Decoder and process the output
def run_kegg_decoder(input_file, sample_folder, file_prefix):
    print(f"Running KEGG-Decoder on {file_prefix}...")

    output_file = os.path.join(sample_folder, f"{file_prefix}_pathways.tsv")

    package_dir = Path(__file__).resolve().parent  # Directory of the current script
    kegg_decoder_script = package_dir / "KEGG_decoder.py"

    # Run KEGG-Decoder via subprocess with progress bar
    with tqdm(total=1, desc="Executing KEGG-Decoder") as pbar:
        command = [
            "python",
            str(kegg_decoder_script),  # Path to KEGG_decoder.py
            "-i",
            input_file,
            "-o",
            output_file,
        ]
        # Run the command and wait for it to finish
        subprocess.run(command, check=True)
        pbar.update(1)

    with open(output_file, "r") as file:
        lines = file.readlines()

    if lines:
        first_line = lines[0].strip().split("\t")
        processed_first_line = [
            x.capitalize() if isinstance(x, str) and x.islower() else x
            for x in first_line
        ]
        lines[0] = "\t".join(processed_first_line) + "\n"

    content = "".join(lines)

    content = content.replace("SAMPLE", file_prefix)

    with open(output_file, "w") as file:
        file.write(content)

    return output_file


# Function to merge all output files into a single TSV file
def merge_outputs(output_folder):
    print("Merging all KEGG-Decoder output files...")

    # Initialize an empty DataFrame for the merged data
    merged_df = pd.DataFrame()

    # Path pattern for finding all *_pathways.tsv files
    output_files = glob.glob(
        os.path.join(output_folder, "temp_files", "*", "*_pathways.tsv")
    )

    # Iterate over each output file
    for file_path in output_files:
        # Extract sample name by getting the parent directory name
        file_prefix = os.path.splitext(os.path.basename(file_path))[0].replace(
            "_pathways", ""
        )

        # Read each file into a pandas DataFrame
        df = pd.read_csv(file_path, sep="\t", index_col=0)

        # Transpose the DataFrame so that the samples become columns
        df_transposed = df.T
        df_transposed.columns = [file_prefix]  # Use the cleaned sample name

        # Initialize the merged DataFrame with function names if empty
        if merged_df.empty:
            merged_df["Function"] = df_transposed.index

        # Merge current sample's data into the merged DataFrame
        merged_df = pd.merge(
            merged_df, df_transposed, left_on="Function", right_index=True, how="outer"
        )

    # Save the merged DataFrame
    merged_output_file = os.path.join(output_folder, "merged_pathways.tsv")
    merged_df.to_csv(merged_output_file, sep="\t", index=False)
    print(f"Files merged successfully into '{merged_output_file}'.")

    return merged_df
