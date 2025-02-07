import argparse
import warnings
import os
import shutil
from pathlib import Path
from . import data_processing
from . import simple_heatmap
from . import grouped_heatmap
from . import kegganog_multi
from kegganog import __version__

warnings.filterwarnings("ignore", category=UserWarning, message=".*tight_layout.*")


# Main function to run the tool
def main():
    print("KEGGaNOG by Ilia V. Popov")
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="KEGGaNOG: Link eggNOG-mapper and KEGG-Decoder for pathway visualization."
    )
    parser.add_argument(
        "-M",
        "--multi",
        action="store_true",
        help="“Multi” mode allows to run KEGGaNOG on multiple eggNOG-mapper annotation files (a text file with file location paths must be passed to the input)",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to eggNOG-mapper annotation file",
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
        help="Sample name for labeling (default: SAMPLE) (not active in `--multi` mode)",
    )
    parser.add_argument(
        "-g",
        "--group",
        action="store_true",
        help="Group the heatmap based on predefined categories",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # Create output and temporary directories
    os.makedirs(args.output, exist_ok=True)
    temp_folder = os.path.join(args.output, "temp_files")
    os.makedirs(temp_folder, exist_ok=True)

    if args.multi:
        kegganog_multi.main()
    else:

        # Step 1: Parse eggNOG-mapper output
        parsed_filtered_file = data_processing.parse_emapper(args.input, temp_folder)

        # Step 2: Run KEGG-Decoder
        kegg_decoder_file = data_processing.run_kegg_decoder(
            parsed_filtered_file, args.output, args.name
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

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    main()
