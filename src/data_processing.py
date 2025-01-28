import os
import subprocess
import csv
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import io


# Function to parse eggnog-mapper output and prepare for KEGG-Decoder
def parse_emapper(input_file, temp_folder):

    # Read the input file with progress bar
    with tqdm(total=1, desc="Reading eggNOG-mapper annotations") as pbar:
        df_filtered = pd.read_csv(input_file, sep="\t", skiprows=4)
        pbar.update(1)

    # Filter the 'KEGG_ko' column
    df_kegg_ko = df_filtered[["KEGG_ko"]]
    df_kegg_ko = df_kegg_ko[df_kegg_ko["KEGG_ko"] != "-"]

    # Format 'KEGG_ko' column for KEGG-Decoder
    with tqdm(total=2, desc="Formatting KEGG_ko column") as pbar:
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(
            r"ko:(K\d+)", r"SAMPLE \1", regex=True
        )
        df_kegg_ko["KEGG_ko"] = df_kegg_ko["KEGG_ko"].str.replace(",", "\n")
        pbar.update(1)

        # Now, instead of saving to a file, we can directly handle the content as a string
        # Convert the DataFrame to a CSV string
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

    # Save the filtered content to a file (if needed)
    parsed_filtered_file = os.path.join(temp_folder, "parsed_KO_terms.txt")
    with open(parsed_filtered_file, "w") as file:
        file.write(content)

    return parsed_filtered_file


# Function to run KEGG-Decoder and process the output
def run_kegg_decoder(input_file, output_folder, sample_name):

    output_file = os.path.join(output_folder, f"{sample_name}_pathways.tsv")

    package_dir = Path(__file__).resolve().parent  # Directory of the current script
    kegg_decoder_script = package_dir / "KEGG_decoder.py"

    # Run KEGG-Decoder via subprocess with progress bar
    with tqdm(total=1, desc="Decoding KO terms") as pbar:
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
        content = file.read()

    content = content.replace("SAMPLE", f"{sample_name}")

    with open(output_file, "w") as file:
        file.write(content)

    return output_file
