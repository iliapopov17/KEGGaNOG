import argparse
import warnings
import os
import shutil
import data_processing
import simple_heatmap
import grouped_heatmap

warnings.filterwarnings("ignore", category=UserWarning, message=".*tight_layout.*")


# Main function to run the tool
def main():
    print("KEGGaNOG v. 0.2.5 by Ilia V. Popov")
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="KEGGaNOG: Link eggnog-mapper and KEGG-Decoder for pathway visualization."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to eggnog-mapper output file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output folder to save results",
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
        "-n",
        "--name",
        default="SAMPLE",
        help="Sample name for labeling (default: SAMPLE)",
    )
    parser.add_argument(
        "-g",
        "--group",
        action="store_true",
        help="Group the heatmap based on predefined categories",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.5")

    args = parser.parse_args()

    # Create output and temporary directories
    os.makedirs(args.output, exist_ok=True)
    temp_folder = os.path.join(args.output, "temp_files")
    os.makedirs(temp_folder, exist_ok=True)

    # Step 1: Parse eggnog-mapper output
    parsed_filtered_file = data_processing.parse_emapper(args.input, temp_folder)

    # Step 2: Run KEGG-Decoder
    kegg_decoder_file = data_processing.run_kegg_decoder(
        parsed_filtered_file, temp_folder, args.name
    )

    # Step 3: Generate the heatmap

    if args.group:
        # Define group labels, for simplicity let's assume you have them in your dataset
        grouped_heatmap.generate_grouped_heatmap(
            kegg_decoder_file, args.output, args.dpi, args.color, args.name
        )
    else:
        # Otherwise, generate a normal heatmap
        simple_heatmap.generate_heatmap(
            kegg_decoder_file, args.output, args.dpi, args.color, args.name
        )

    print(f"Heatmap saved in {args.output}/heatmap_figure.png")


def clean_pycache(dir_path):
    for root, dirs, files in os.walk(dir_path):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))


if __name__ == "__main__":
    clean_pycache(os.path.dirname(__file__))
    main()
