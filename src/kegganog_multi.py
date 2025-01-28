import argparse
import warnings
import os
import shutil
from pathlib import Path
from . import data_processing_multi
from . import simple_heatmap_multi
from . import grouped_heatmap_multi


# Main function to handle different types of inputs and manage output locations
def main():
    parser = argparse.ArgumentParser(
        description="Process eggnog-mapper outputs with KEGG-Decoder."
    )
    parser.add_argument(
        "-M",
        "--multi",
        action="store_true",
        help="Multiple inputs",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input file or text file with paths to input files.",
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Directory for final output files."
    )
    parser.add_argument(
        "-dpi",
        "--dpi",
        type=int,
        default=300,
        help="DPI for the output image (default: 300)",
    )
    parser.add_argument(
        "-c",
        "--color",
        "--colour",
        default="Blues",
        help="Cmap for seaborn heatmap. Recommended options: Greys, Purples, Blues, Greens, Oranges, Reds (default: Blues)",
    )
    parser.add_argument(
        "-g",
        "--group",
        action="store_true",
        help="Group the heatmap based on predefined categories",
    )
    args = parser.parse_args()

    # Create output and temp directories
    os.makedirs(args.output, exist_ok=True)
    temp_folder = os.path.join(args.output, "temp_files")
    os.makedirs(temp_folder, exist_ok=True)

    # Check if input is a list of files or a single annotation file
    if args.input.endswith(".txt"):
        with open(args.input, "r") as f:
            file_paths = [line.strip() for line in f if line.strip()]
    else:
        file_paths = [args.input]

    # Process each annotation file in the list
    for file_path in file_paths:
        # Check if the file exists to avoid errors
        if not os.path.isfile(file_path):
            print(f"Error: Input file {file_path} does not exist. Skipping.")
            continue

        # Extract the file prefix (e.g., "D1" from "D1.emapper.annotations")
        file_prefix = os.path.basename(file_path).replace(".emapper.annotations", "")

        # Create a subdirectory for each file prefix in temp_files
        sample_folder = os.path.join(temp_folder, file_prefix)
        os.makedirs(sample_folder, exist_ok=True)

        # Parse and run KEGG-Decoder
        parsed_file = data_processing_multi.parse_emapper(
            file_path, sample_folder, file_prefix
        )
        data_processing_multi.run_kegg_decoder(parsed_file, sample_folder, file_prefix)

    # Merge all KEGG-Decoder output files
    kegg_decoder_file = data_processing_multi.merge_outputs(args.output)

    # grouped_heatmap_multi.generate_grouped_heatmap_multi(
    # kegg_decoder_file, args.output, args.dpi, args.color
    # )

    if args.group:
        # Define group labels, for simplicity let's assume you have them in your dataset
        grouped_heatmap_multi.generate_grouped_heatmap_multi(
            kegg_decoder_file, args.output, args.dpi, args.color
        )
    else:
        # Otherwise, generate a normal heatmap
        simple_heatmap_multi.generate_heatmap_multi(
            kegg_decoder_file, args.output, args.dpi, args.color
        )

    print(f"Heatmap saved in {args.output}/heatmap_figure.png")

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    main()
