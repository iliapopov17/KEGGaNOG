import logging
import shutil
import sys
from importlib.metadata import version as _metadata_version
from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError

from . import kegganog_multi
from .processing.pipeline import run_single
from .schemas import CLIParams

_log = logging.getLogger(__name__)

app = typer.Typer(
    name="kegganog",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

CITATION_MESSAGE = """
Thank you for using KEGGaNOG! If you use it in your research, please cite:

    Popov, I.V., Chikindas, M.L., Venema, K., Ermakov, A.M. and Popov, I.V., 2025.
    KEGGaNOG: A Lightweight Tool for KEGG Module Profiling From Orthology-Based Annotations.
    Molecular Nutrition & Food Research, p.e70269.
    doi.org/10.1002/mnfr.70269
"""


def print_citation() -> None:
    print(CITATION_MESSAGE)


def _version_callback(value: bool) -> None:
    if value:
        print(f"KEGGaNOG {_metadata_version('kegganog')}")
        raise typer.Exit()


def _validate_params(
    input_path: Optional[str],
    output_dir: Optional[str],
    multi: bool,
    overwrite: bool,
    dpi: int,
    color: str,
    sample_name: str,
    group: bool,
) -> CLIParams:
    """Validate parameters through Pydantic; print errors and exit on failure."""
    try:
        return CLIParams(
            input_path=input_path,
            output_dir=output_dir,
            multi=multi,
            overwrite=overwrite,
            dpi=dpi,
            color=color,
            sample_name=sample_name,
            group=group,
        )
    except ValidationError as e:
        print("KEGGaNOG: invalid argument value(s):", file=sys.stderr)
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            print(f"  --{field}: {message}", file=sys.stderr)
        raise typer.Exit(code=1)


def _prepare_output_dir(params: CLIParams) -> None:
    """Create the output directory, optionally wiping an existing one."""
    output_dir = Path(params.output_dir)
    if output_dir.exists():
        if not params.overwrite:
            raise FileExistsError(
                f"Output directory '{params.output_dir}' already exists. "
                "Use --overwrite to overwrite it."
            )
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)
    (output_dir / "temp_files").mkdir()


def _run_pipeline(params: CLIParams) -> None:
    """Execute the single-sample analysis pipeline."""
    input_path = Path(params.input_path)
    file_bytes = input_path.read_bytes()

    run_single(
        file_bytes=file_bytes,
        sample_name=params.sample_name,
        dpi=params.dpi,
        color=params.color,
        group=params.group,
        output_dir=params.output_dir,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


@app.command(
    help="KEGGaNOG: Link eggNOG-mapper and KEGG-Decoder for pathway visualization.",
)
def main(
    input_path: Optional[str] = typer.Option(
        None,
        "-i",
        "--input",
        help="Path to eggNOG-mapper annotation file.",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output folder to save results.",
    ),
    multi: bool = typer.Option(
        False,
        "-M",
        "--multi",
        help="Run KEGGaNOG in multi mode with multiple eggNOG-mapper annotation files.",
    ),
    overwrite: bool = typer.Option(
        False,
        "-overwrite",
        "--overwrite",
        help="Overwrite the output directory if it already exists.",
    ),
    dpi: int = typer.Option(
        300,
        "-dpi",
        "--dpi",
        help="DPI for the output image (default: 300).",
    ),
    color: str = typer.Option(
        "Blues",
        "-c",
        "--color",
        help="Cmap for seaborn heatmap (default: Blues).",
    ),
    sample_name: str = typer.Option(
        "SAMPLE",
        "-n",
        "--name",
        help="Sample name for labeling (default: SAMPLE).",
    ),
    group: bool = typer.Option(
        False,
        "-g",
        "--group",
        help="Group the heatmap based on predefined categories.",
    ),
    web: bool = typer.Option(
        False,
        "--web",
        help="Launch local web UI in browser at http://localhost:8000.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "-V",
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    print("KEGGaNOG by Ilia V. Popov")

    if web:
        from .web import launch

        launch()
        return

    if input_path is None or output_dir is None:
        print(
            "Error: --input and --output are required in CLI mode.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    params = _validate_params(
        input_path=input_path,
        output_dir=output_dir,
        multi=multi,
        overwrite=overwrite,
        dpi=dpi,
        color=color,
        sample_name=sample_name,
        group=group,
    )

    try:
        _prepare_output_dir(params)
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)

    if params.multi:
        kegganog_multi.MultiSampleRunner(
            input_path=params.input_path,
            output_dir=params.output_dir,
            dpi=params.dpi,
            color=params.color,
            group=params.group,
        ).run()
    else:
        _run_pipeline(params)

    _log.info("Heatmap saved in %s/heatmap_figure.png", params.output_dir)
    print_citation()


def entry_point() -> None:
    """Wraps typer app to handle KeyboardInterrupt gracefully."""
    try:
        app()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.", file=sys.stderr)
        print_citation()
        sys.exit(1)


if __name__ == "__main__":
    entry_point()
