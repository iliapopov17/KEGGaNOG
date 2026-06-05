"""Tests for Pydantic models in kegganog.schemas.

Pure validation — no I/O, no fixtures, fully deterministic.
Each class tests one schema; sections go: defaults → valid variants →
boundary values → invalid inputs → field-specific constraints.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from kegganog.schemas import CLIParams, JobStatus, WebParams

# ===========================================================================
# CLIParams
# ===========================================================================


class TestCLIParams:
    # --- defaults and valid construction ---

    def test_valid_defaults(self):
        p = CLIParams(input_path="in.tsv", output_dir="out/")
        assert p.dpi == 300
        assert p.color == "Blues"
        assert p.sample_name == "SAMPLE"
        assert p.multi is False
        assert p.group is False
        assert p.overwrite is False

    def test_valid_all_fields_explicit(self):
        p = CLIParams(
            input_path="in.tsv",
            output_dir="out/",
            dpi=150,
            color="Greens",
            sample_name="MySample",
            multi=True,
            group=True,
            overwrite=True,
        )
        assert p.dpi == 150
        assert p.color == "Greens"
        assert p.sample_name == "MySample"
        assert p.multi is True
        assert p.group is True
        assert p.overwrite is True

    # --- dpi ---

    def test_dpi_boundary_low_is_valid(self):
        assert CLIParams(input_path="in.tsv", output_dir="out/", dpi=72).dpi == 72

    def test_dpi_boundary_high_is_valid(self):
        assert CLIParams(input_path="in.tsv", output_dir="out/", dpi=600).dpi == 600

    def test_dpi_below_minimum_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(input_path="in.tsv", output_dir="out/", dpi=10)
        assert "dpi" in str(exc_info.value)

    def test_dpi_above_maximum_raises(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", dpi=700)

    # --- color ---

    def test_invalid_color_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(input_path="in.tsv", output_dir="out/", color="Rainbow")  # ty:ignore[invalid-argument-type]
        assert "color" in str(exc_info.value)

    @pytest.mark.parametrize(
        "color", ["Blues", "Greens", "Reds", "Purples", "Greys", "Oranges"]
    )
    def test_all_valid_colors_are_accepted(self, color):
        assert (
            CLIParams(input_path="in.tsv", output_dir="out/", color=color).color
            == color
        )

    # --- sample_name ---

    def test_sample_name_valid_with_hyphens_and_underscores(self):
        p = CLIParams(
            input_path="in.tsv", output_dir="out/", sample_name="My-Sample_2024"
        )
        assert p.sample_name == "My-Sample_2024"

    def test_sample_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="x" * 65)

    @pytest.mark.parametrize("bad_char", ["/", "\\", "*", ":"])
    def test_sample_name_unsafe_chars_raise(self, bad_char):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(
                input_path="in.tsv", output_dir="out/", sample_name=f"bad{bad_char}name"
            )
        assert "sample_name" in str(exc_info.value)


# ===========================================================================
# WebParams
# ===========================================================================


class TestWebParams:
    def test_valid_defaults(self):
        p = WebParams()
        assert p.dpi == 300
        assert p.color == "Blues"
        assert p.sample_name == "SAMPLE"
        assert p.group is False

    def test_group_flag_can_be_set(self):
        assert WebParams(group=True).group is True

    def test_dpi_below_minimum_raises(self):
        with pytest.raises(ValidationError):
            WebParams(dpi=50)

    def test_invalid_color_raises(self):
        with pytest.raises(ValidationError):
            WebParams(color="Viridis")  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize("bad_char", ["/", "?", "|"])
    def test_sample_name_unsafe_chars_raise(self, bad_char):
        with pytest.raises(ValidationError) as exc_info:
            WebParams(sample_name=f"bad{bad_char}name")
        assert "sample_name" in str(exc_info.value)


# ===========================================================================
# JobStatus
# ===========================================================================


class TestJobStatus:
    def test_valid_pending_with_empty_message(self):
        js = JobStatus(job_id="abc", status="pending")
        assert js.job_id == "abc"
        assert js.message == ""

    def test_error_status_carries_message(self):
        js = JobStatus(job_id="abc", status="error", message="Something went wrong")
        assert js.message == "Something went wrong"

    @pytest.mark.parametrize("status", ["pending", "running", "done", "error"])
    def test_all_valid_statuses_accepted(self, status):
        assert JobStatus(job_id="x", status=status).status == status

    def test_unknown_status_raises(self):
        with pytest.raises(ValidationError):
            JobStatus(job_id="x", status="unknown")  # ty:ignore[invalid-argument-type]
