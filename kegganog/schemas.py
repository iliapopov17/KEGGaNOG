from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------

ValidColor = Literal["Blues", "Greens", "Reds", "Purples", "Greys", "Oranges"]


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class BaseParams(BaseModel):
    """Shared parameters for both CLI and web form."""

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
# Model 1: CLI parameters
# ---------------------------------------------------------------------------


class CLIParams(BaseParams):
    """
    Validated parameters for the KEGGaNOG command-line interface.

    Extends BaseParams with filesystem paths and CLI-only flags.
    """

    input_path: str = Field(
        ...,
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


# ---------------------------------------------------------------------------
# Model 2: Web form parameters
# ---------------------------------------------------------------------------


class WebParams(BaseParams):
    """
    Validated parameters received from the KEGGaNOG web form.

    Inherits all shared fields from BaseParams.
    No filesystem paths — those are managed server-side.
    """


# ---------------------------------------------------------------------------
# Model 3: Job status response
# ---------------------------------------------------------------------------


class JobStatus(BaseModel):
    """
    Status of a background analysis job.

    Returned by GET /status/{job_id}.
    """

    job_id: str
    status: Literal["pending", "running", "done", "error"]
    message: str = Field(
        default="",
        description="Human-readable message, populated on error.",
    )
