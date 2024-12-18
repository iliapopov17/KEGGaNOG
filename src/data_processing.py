import os
import subprocess
import csv
import pandas as pd
from tqdm import tqdm


# Function to parse eggnog-mapper output and prepare for KEGG-Decoder
def parse_emapper(input_file, temp_folder):
    print("Parsing eggnog-mapper output...")

    # Read the input file with progress bar
    with tqdm(total=1, desc="Reading eggnog-mapper file") as pbar:
        df_filtered = pd.read_csv(input_file, sep="\t", skiprows=4)
        pbar.update(1)

    # Filter the 'KEGG_ko' column
    df_kegg_ko = df_filtered[["KEGG_ko"]]
    df_kegg_ko = df_kegg_ko[df_kegg_ko["KEGG_ko"] != "-"]

    # Format 'KEGG_ko' column for KEGG-Decoder
    with tqdm(total=1, desc="Formatting KEGG_ko column") as pbar:
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(
            r"ko:(K\d+)", r"SAMPLE \1", regex=True
        )
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(",", "\n")
        pbar.update(1)

    # Save the parsed file
    parsed_file = os.path.join(temp_folder, "parsed.txt")
    with tqdm(total=1, desc="Saving parsed file") as pbar:
        df_kegg_ko.to_csv(
            parsed_file,
            sep="\t",
            index=False,
            header=False,
            quoting=csv.QUOTE_MINIMAL,
            escapechar="\\",
        )
        pbar.update(1)

    # Remove all quotation marks from the parsed file
    parsed_filtered_file = os.path.join(temp_folder, "parsed_filtered.txt")
    with open(parsed_file, "r") as file:
        content = file.read()

    content = content.replace('"', "")
    with open(parsed_filtered_file, "w") as file:
        file.write(content)

    return parsed_filtered_file


# Function to run KEGG-Decoder and process the output
def run_kegg_decoder(input_file, temp_folder, sample_name):
    print("Running KEGG-Decoder...")

    output_file = os.path.join(temp_folder, "pathways.tsv")

    # Run KEGG-Decoder via subprocess with progress bar
    with tqdm(total=1, desc="Executing KEGG-Decoder") as pbar:
        command = [
        "python", 
        "src/KEGG_decoder.py",  # Path to KEGG_decoder.py
        "-i", input_file,
        "-o", output_file
        ]
        # Run the command and wait for it to finish
        subprocess.run(command, check=True)
        pbar.update(1)

    with open(output_file, "r") as file:
        content = file.read()

    content = content.replace("SAMPLE", f"{sample_name}")

    with open(output_file, "w") as file:
        file.write(content)

    return output_file
