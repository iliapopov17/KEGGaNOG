import argparse
import warnings
import os
import shutil
from pathlib import Path
import sys

from .processing import data_processing
from .cheatmaps import simple_heatmap, grouped_heatmap
from . import kegganog_multi
from .version import __version__

warnings.filterwarnings("ignore", category=UserWarning, message=".*tight_layout.*")

# Citation message
CITATION_MESSAGE = """
Thank you for using KEGGaNOG! If you use it in your research, please cite:

    Popov, I.V., Chikindas, M.L., Venema, K., Ermakov, A.M. and Popov, I.V., 2025. 
    KEGGaNOG: A Lightweight Tool for KEGG Module Profiling From Orthology-Based Annotations. 
    Molecular Nutrition & Food Research, p.e70269.
    doi.org/10.1002/mnfr.70269
"""


def print_citation():
    print(CITATION_MESSAGE, file=sys.stderr)


# Main function to run the tool
def main():
    print("KEGGaNOG by Ilia V. Popov")
    parser = argparse.ArgumentParser(
        description="KEGGaNOG: Link eggNOG-mapper and KEGG-Decoder for pathway visualization."
    )
    parser.add_argument(
        "-M",
        "--multi",
        action="store_true",
        help="Run KEGGaNOG in multi mode with multiple eggNOG-mapper annotation files",
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to eggNOG-mapper annotation file"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Output folder to save results"
    )
    parser.add_argument(
        "-overwrite",
        "--overwrite",
        action="store_true",
        help="Overwrite the output directory if it already exists",
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
        help="Cmap for seaborn heatmap (default: Blues)",
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
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    try:
        if os.path.exists(args.output):
            if not args.overwrite:
                raise FileExistsError(
                    f"Output directory '{args.output}' already exists. Use --overwrite to overwrite it."
                )
            else:
                shutil.rmtree(args.output)

        os.makedirs(args.output)
        temp_folder = os.path.join(args.output, "temp_files")
        os.makedirs(temp_folder, exist_ok=True)

        if args.multi:
            kegganog_multi.main()
        else:
            parsed_filtered_file = data_processing.parse_emapper(
                args.input, temp_folder
            )
            kegg_decoder_file = data_processing.run_kegg_decoder(
                parsed_filtered_file, args.output, args.name
            )

            if args.group:
                grouped_heatmap.generate_grouped_heatmap(
                    kegg_decoder_file, args.output, args.dpi, args.color, args.name
                )
            else:
                simple_heatmap.generate_heatmap(
                    kegg_decoder_file, args.output, args.dpi, args.color, args.name
                )

        print(f"Heatmap saved in {args.output}/heatmap_figure.png")

        print_citation()

    finally:
        # Remove __pycache__ on exit (also runs on Ctrl+C)
        current_dir = Path(__file__).resolve().parent
        pycache_dir = current_dir / "__pycache__"
        if pycache_dir.exists() and pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Print citation also when user interrupts
        print("\nExecution interrupted by user.", file=sys.stderr)
        print_citation()
        sys.exit(1)
