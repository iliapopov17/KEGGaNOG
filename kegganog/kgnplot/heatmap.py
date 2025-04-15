from kegganog.simple_heatmap import generate_heatmap
from kegganog.grouped_heatmap import generate_grouped_heatmap
from kegganog.simple_heatmap_multi import generate_heatmap_multi
from kegganog.grouped_heatmap_multi import generate_grouped_heatmap_multi
import tempfile
import os
import pandas as pd
import shutil
from pathlib import Path
import contextlib
import sys
import os
import io
import matplotlib.pyplot as plt
from .base import KgnPlotBase


@contextlib.contextmanager
def silent_plot_and_tqdm():
    import tqdm

    # Backup originals
    original_show = plt.show
    original_tqdm = tqdm.tqdm

    # Define no-op versions
    plt.show = lambda *args, **kwargs: None

    class SilentTqdm(tqdm.tqdm):
        def __init__(self, *args, **kwargs):
            kwargs["disable"] = True
            super().__init__(*args, **kwargs)

    tqdm.tqdm = SilentTqdm

    # Optionally silence stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
        io.StringIO()
    ):
        try:
            yield
        finally:
            # Restore originals
            plt.show = original_show
            tqdm.tqdm = original_tqdm


class KgnHeatmap(KgnPlotBase):
    pass


def heatmap(
    df,
    figsize: tuple = None,
    color: str = None,
    group: bool = False,
    sample_name: str = None,
    annot: bool = True,
):
    """
    Universal heatmap wrapper for KEGGaNOG heatmap generators.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - color: Colormap name (str) (e.g. "Greens" or "Blues" etc.) or list of colors.
    - group: Whether to use grouped heatmap functions.
    - sample_name: Optional sample name (ignored for multi-heatmaps).
    - annot: Whether to annotate heatmap cells (ignored for multi-heatmaps).

    Returns:
    - KgnHeatmap: An object containing the radar plot figure and axis for customization or saving.
    """

    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp_file:
        df.to_csv(temp_file, sep="\t", index=False)
        temp_file_path = temp_file.name

    is_single = df.shape[0] == 1
    is_multi = df.shape[0] > 1

    if not (is_single or is_multi):
        raise ValueError(
            "DataFrame does not fit the expected dimensions for heatmap generation"
        )

    heatmap_function = {
        (False, True): generate_grouped_heatmap,
        (False, False): generate_heatmap,
        (True, True): generate_grouped_heatmap_multi,
        (True, False): generate_heatmap_multi,
    }[(not is_single, group)]

    # Use temporary output folder
    output_folder = tempfile.mkdtemp()

    # Run selected function
    with silent_plot_and_tqdm():
        if heatmap_function in [generate_heatmap, generate_grouped_heatmap]:
            fig, ax = heatmap_function(
                kegg_decoder_file=temp_file_path,
                output_folder=output_folder,
                dpi=300,
                color=color,
                sample_name=sample_name,
                figsize=figsize,
                annot=annot,
            )
        else:
            print(
                "Remember: The 'sample_name' and 'annot' arguments are ignored for multi-heatmaps."
            )
            fig, ax = heatmap_function(
                kegg_decoder_file=df,
                output_folder=output_folder,
                dpi=300,
                color=color,
                figsize=figsize,
            )

    shutil.rmtree(output_folder, ignore_errors=True)

    # Clean up __pycache__
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnHeatmap(fig, ax)
