"""Tests for Pydantic models in kegganog.schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from kegganog.schemas import CLIParams, JobStatus, WebParams


class TestCLIParams:
    def test_valid_defaults(self):
        p = CLIParams(input_path="in.tsv", output_dir="out/")
        assert p.dpi == 300
        assert p.color == "Blues"
        assert p.sample_name == "SAMPLE"
        assert p.multi is False
        assert p.group is False
        assert p.overwrite is False

    def test_valid_all_fields(self):
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

    def test_dpi_too_low(self):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(input_path="in.tsv", output_dir="out/", dpi=10)
        assert "dpi" in str(exc_info.value)

    def test_dpi_too_high(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", dpi=700)

    def test_dpi_boundary_low(self):
        p = CLIParams(input_path="in.tsv", output_dir="out/", dpi=72)
        assert p.dpi == 72

    def test_dpi_boundary_high(self):
        p = CLIParams(input_path="in.tsv", output_dir="out/", dpi=600)
        assert p.dpi == 600

    def test_invalid_color(self):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(input_path="in.tsv", output_dir="out/", color="Rainbow")
        assert "color" in str(exc_info.value)

    @pytest.mark.parametrize("color", ["Blues", "Greens", "Reds", "Purples", "Greys", "Oranges"])
    def test_all_valid_colors(self, color):
        p = CLIParams(input_path="in.tsv", output_dir="out/", color=color)
        assert p.color == color

    def test_sample_name_with_slash(self):
        with pytest.raises(ValidationError) as exc_info:
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="bad/name")
        assert "sample_name" in str(exc_info.value)

    def test_sample_name_with_backslash(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="bad\\name")

    def test_sample_name_with_asterisk(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="bad*name")

    def test_sample_name_with_colon(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="bad:name")

    def test_sample_name_valid_special_chars(self):
        p = CLIParams(input_path="in.tsv", output_dir="out/", sample_name="My-Sample_2024")
        assert p.sample_name == "My-Sample_2024"

    def test_sample_name_too_long(self):
        with pytest.raises(ValidationError):
            CLIParams(input_path="in.tsv", output_dir="out/", sample_name="x" * 65)


class TestWebParams:
    def test_valid_defaults(self):
        p = WebParams()
        assert p.dpi == 300
        assert p.color == "Blues"
        assert p.sample_name == "SAMPLE"
        assert p.group is False

    def test_invalid_dpi(self):
        with pytest.raises(ValidationError):
            WebParams(dpi=50)

    def test_invalid_color(self):
        with pytest.raises(ValidationError):
            WebParams(color="Viridis")

    def test_sample_name_unsafe_chars(self):
        with pytest.raises(ValidationError) as exc_info:
            WebParams(sample_name="hack/path")
        assert "sample_name" in str(exc_info.value)

    def test_sample_name_with_question_mark(self):
        with pytest.raises(ValidationError):
            WebParams(sample_name="bad?name")

    def test_sample_name_with_pipe(self):
        with pytest.raises(ValidationError):
            WebParams(sample_name="bad|name")

    def test_group_flag(self):
        p = WebParams(group=True)
        assert p.group is True


class TestJobStatus:
    def test_valid_pending(self):
        js = JobStatus(job_id="abc", status="pending")
        assert js.job_id == "abc"
        assert js.message == ""

    def test_valid_error_with_message(self):
        js = JobStatus(job_id="abc", status="error", message="Something went wrong")
        assert js.message == "Something went wrong"

    @pytest.mark.parametrize("status", ["pending", "running", "done", "error"])
    def test_all_valid_statuses(self, status):
        js = JobStatus(job_id="x", status=status)
        assert js.status == status

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            JobStatus(job_id="x", status="unknown")
