import argparse
import os
import shutil
import sys
import warnings
from pathlib import Path

from pydantic import ValidationError

from .schemas import CLIParams
from .version import __version__
from .processing import data_processing
from .cheatmaps import simple_heatmap, grouped_heatmap
from . import kegganog_multi

warnings.filterwarnings("ignore", category=UserWarning, message=".*tight_layout.*")

CITATION_MESSAGE = """
Thank you for using KEGGaNOG! If you use it in your research, please cite:

    Popov, I.V., Chikindas, M.L., Venema, K., Ermakov, A.M. and Popov, I.V., 2025.
    KEGGaNOG: A Lightweight Tool for KEGG Module Profiling From Orthology-Based Annotations.
    Molecular Nutrition & Food Research, p.e70269.
    doi.org/10.1002/mnfr.70269
"""


def print_citation():
    print(CITATION_MESSAGE, file=sys.stderr)


def main():
    print("KEGGaNOG by Ilia V. Popov")

    parser = argparse.ArgumentParser(
        description="KEGGaNOG: Link eggNOG-mapper and KEGG-Decoder for pathway visualization."
    )

    # ------------------------------------------------------------------
    # Existing arguments — unchanged
    # ------------------------------------------------------------------
    parser.add_argument(
        "-M",
        "--multi",
        action="store_true",
        help="Run KEGGaNOG in multi mode with multiple eggNOG-mapper annotation files",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=False,  # Changed: not required when --web is used
        default=None,
        help="Path to eggNOG-mapper annotation file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,  # Changed: not required when --web is used
        default=None,
        help="Output folder to save results",
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
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # ------------------------------------------------------------------
    # New argument: --web
    # Launches the local browser UI instead of running the CLI pipeline.
    # ------------------------------------------------------------------
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch local web UI in browser at http://localhost:8000",
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # --web mode: start FastAPI server and open browser, then exit
    # ------------------------------------------------------------------
    if args.web:
        from .web import launch

        launch()
        return  # launch() blocks until the user presses Ctrl+C

    # ------------------------------------------------------------------
    # CLI mode: -i and -o are required when not using --web
    # ------------------------------------------------------------------
    if args.input is None or args.output is None:
        parser.error("Arguments -i/--input and -o/--output are required in CLI mode.")

    # ------------------------------------------------------------------
    # Pydantic validation
    #
    # argparse has already converted types (e.g. --dpi 300 → int 300).
    # Pydantic now checks the values themselves:
    #   - dpi is between 72 and 600
    #   - color is one of the six allowed colormaps
    #   - sample_name has no filesystem-unsafe characters
    #
    # If validation fails, we print each error clearly and exit —
    # no Python traceback shown to the user.
    # ------------------------------------------------------------------
    try:
        params = CLIParams(
            input_path=args.input,
            output_dir=args.output,
            multi=args.multi,
            overwrite=args.overwrite,
            dpi=args.dpi,
            color=args.color,
            sample_name=args.name,
            group=args.group,
        )
    except ValidationError as e:
        print("KEGGaNOG: invalid argument value(s):", file=sys.stderr)
        for error in e.errors():
            # error["loc"] is a tuple like ("dpi",) or ("sample_name",)
            field = error["loc"][0]
            message = error["msg"]
            print(f"  --{field}: {message}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Pipeline — identical to the original, params.X instead of args.X
    # ------------------------------------------------------------------
    try:
        if os.path.exists(params.output_dir):
            if not params.overwrite:
                raise FileExistsError(
                    f"Output directory '{params.output_dir}' already exists. "
                    "Use --overwrite to overwrite it."
                )
            else:
                shutil.rmtree(params.output_dir)

        os.makedirs(params.output_dir)
        temp_folder = os.path.join(params.output_dir, "temp_files")
        os.makedirs(temp_folder, exist_ok=True)

        if params.multi:
            kegganog_multi.main()
        else:
            parsed_filtered_file = data_processing.parse_emapper(
                params.input_path, temp_folder
            )
            kegg_decoder_file = data_processing.run_kegg_decoder(
                parsed_filtered_file, params.output_dir, params.sample_name
            )

            if params.group:
                grouped_heatmap.generate_grouped_heatmap(
                    kegg_decoder_file,
                    params.output_dir,
                    params.dpi,
                    params.color,
                    params.sample_name,
                )
            else:
                simple_heatmap.generate_heatmap(
                    kegg_decoder_file,
                    params.output_dir,
                    params.dpi,
                    params.color,
                    params.sample_name,
                )

        print(f"Heatmap saved in {params.output_dir}/heatmap_figure.png")
        print_citation()

    finally:
        # Remove __pycache__ on exit (runs even on Ctrl+C)
        current_dir = Path(__file__).resolve().parent
        pycache_dir = current_dir / "__pycache__"
        if pycache_dir.exists() and pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.", file=sys.stderr)
        print_citation()
        sys.exit(1)
