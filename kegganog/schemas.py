from typing import Literal
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Allowed values (defined once, reused in both models below)
# ---------------------------------------------------------------------------

# These are the colormaps supported by seaborn in KEGGaNOG.
# Literal["Blues", "Greens", ...] means Pydantic will reject anything else.
ValidColor = Literal["Blues", "Greens", "Reds", "Purples", "Greys", "Oranges"]


# ---------------------------------------------------------------------------
# Model 1: CLI parameters
# Used when the user runs: KEGGaNOG -i file.tsv -o output/ --dpi 300
# ---------------------------------------------------------------------------


class CLIParams(BaseModel):
    """
    Validated parameters for the KEGGaNOG command-line interface.

    This model is populated from argparse args and validated before
    the analysis pipeline starts.
    """

    input_path: str = Field(
        ...,  # ... means "required, no default"
        description="Path to eggNOG-mapper annotation file (or .txt list in multi mode).",
    )
    output_dir: str = Field(
        ...,
        description="Output folder to save results.",
    )
    multi: bool = Field(
        default=False,
        description="Run in multi-sample mode.",
    )
    overwrite: bool = Field(
        default=False,
        description="Overwrite output directory if it already exists.",
    )
    dpi: int = Field(
        default=300,
        ge=72,  # ge = greater than or equal — minimum sensible DPI
        le=600,  # le = less than or equal — above 600 is rarely useful
        description="DPI for the output image.",
    )
    color: ValidColor = Field(
        default="Blues",
        description="Colormap for the seaborn heatmap.",
    )
    sample_name: str = Field(
        default="SAMPLE",
        max_length=64,
        description="Sample name used for labeling (single mode only).",
    )
    group: bool = Field(
        default=False,
        description="Group the heatmap by predefined functional categories.",
    )

    @field_validator("sample_name")
    @classmethod
    def no_path_characters(cls, v: str) -> str:
        """
        Reject sample names that contain filesystem-unsafe characters.

        Why: sample_name is used to label output files. Characters like /
        or * would break file creation silently or cause confusing errors.
        """
        forbidden = set(r'\/:*?"<>|')
        bad_chars = forbidden & set(v)
        if bad_chars:
            raise ValueError(f"sample_name contains invalid characters: {bad_chars}")
        return v


# ---------------------------------------------------------------------------
# Model 2: Web form parameters
# Used when the user uploads a file via the browser interface.
# No input_path / output_dir here — the file arrives as an upload,
# and the output directory is managed by the server automatically.
# ---------------------------------------------------------------------------


class WebParams(BaseModel):
    """
    Validated parameters received from the KEGGaNOG web form.

    Identical validation rules as CLIParams, but without filesystem paths
    (those are handled server-side when the uploaded file is saved to a
    temporary directory).
    """

    dpi: int = Field(default=300, ge=72, le=600)
    color: ValidColor = Field(default="Blues")
    sample_name: str = Field(default="SAMPLE", max_length=64)
    group: bool = Field(default=False)

    @field_validator("sample_name")
    @classmethod
    def no_path_characters(cls, v: str) -> str:
        """Reject sample names with filesystem-unsafe characters."""
        forbidden = set(r'\/:*?"<>|')
        bad_chars = forbidden & set(v)
        if bad_chars:
            raise ValueError(f"sample_name contains invalid characters: {bad_chars}")
        return v


# ---------------------------------------------------------------------------
# Model 3: Job status response
# Used by FastAPI to tell the browser what is happening with an analysis job.
# ---------------------------------------------------------------------------


class JobStatus(BaseModel):
    """
    Status of a background analysis job.

    Returned by GET /status/{job_id}.
    The browser polls this endpoint every few seconds while waiting for results.
    """

    job_id: str
    status: Literal["pending", "running", "done", "error"]
    message: str = Field(
        default="",
        description="Human-readable message, populated on error.",
    )
