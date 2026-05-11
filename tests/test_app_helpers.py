"""Tests for app.py helper functions and additional routes."""

from __future__ import annotations

import asyncio
import io
import zipfile
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from kegganog.app import (
    _normalize_job_id,
    _safe_client_filename,
    app,
)
from kegganog.schemas import WebParams


def _minimal_png_bytes() -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(1, 1))
    fig.savefig(buf, format="png", dpi=72)
    plt.close(fig)
    return buf.getvalue()


def _make_done_job(workdir: Path) -> dict:
    png_bytes = _minimal_png_bytes()
    png_path = workdir / "preview.png"
    png_path.write_bytes(png_bytes)

    tsv_path = workdir / "pathways.tsv"
    tsv_path.write_text("Function\tSAMPLE\nglycoly\t0.5\n", encoding="utf-8")

    zip_path = workdir / "results.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("heatmap.png", png_bytes)

    return {
        "status": "done",
        "path": str(zip_path),
        "png_path": str(png_path),
        "tsv_path": str(tsv_path),
        "samples": ["SAMPLE"],
        "pathways": ["glycolysis"],
        "message": "",
    }


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# _normalize_job_id
# ---------------------------------------------------------------------------


class TestNormalizeJobId:
    def test_valid_uuid(self):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        assert _normalize_job_id(uid) == uid

    def test_invalid_string(self):
        assert _normalize_job_id("not-a-uuid") is None

    def test_empty_string(self):
        assert _normalize_job_id("") is None

    def test_uuid_without_dashes(self):
        uid = "550e8400e29b41d4a716446655440000"
        normalized = _normalize_job_id(uid)
        assert normalized == "550e8400-e29b-41d4-a716-446655440000"


# ---------------------------------------------------------------------------
# _safe_client_filename
# ---------------------------------------------------------------------------


class TestSafeClientFilename:
    def test_normal_filename(self):
        assert _safe_client_filename("sample.emapper.annotations") == "sample.emapper.annotations"

    def test_none_returns_default(self):
        assert _safe_client_filename(None) == "sample.annotations"

    def test_empty_string_returns_default(self):
        assert _safe_client_filename("") == "sample.annotations"

    def test_path_traversal_stripped(self):
        result = _safe_client_filename("../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result
        assert result == "passwd"

    def test_dot_only_returns_default(self):
        assert _safe_client_filename(".") == "sample.annotations"

    def test_dotdot_returns_default(self):
        assert _safe_client_filename("..") == "sample.annotations"

    def test_whitespace_stripped(self):
        result = _safe_client_filename("  sample.tsv  ")
        assert result == "sample.tsv"


# ---------------------------------------------------------------------------
# Status route — invalid UUID
# ---------------------------------------------------------------------------


def test_status_invalid_uuid_returns_404(client):
    r = client.get("/status/not-a-uuid")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Preview route
# ---------------------------------------------------------------------------


def test_preview_not_found(client):
    r = client.get("/preview/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_preview_invalid_uuid(client):
    r = client.get("/preview/invalid-uuid")
    assert r.status_code == 404


def test_preview_job_not_done(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running", "path": None, "png_path": None, "message": "", "tsv_path": None, "samples": [], "pathways": []}
    with TestClient(app) as c:
        r = c.get(f"/preview/{job_id}")
    assert r.status_code == 400
    del _jobs[job_id]


# ---------------------------------------------------------------------------
# Download route
# ---------------------------------------------------------------------------


def test_download_not_found(client):
    r = client.get("/download/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_download_invalid_uuid(client):
    r = client.get("/download/not-a-uuid")
    assert r.status_code == 404


def test_download_job_not_done(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "path": None, "png_path": None, "message": "", "tsv_path": None, "samples": [], "pathways": []}
    with TestClient(app) as c:
        r = c.get(f"/download/{job_id}")
    assert r.status_code == 400
    del _jobs[job_id]


# ---------------------------------------------------------------------------
# /samples route
# ---------------------------------------------------------------------------


def test_samples_not_found(client):
    r = client.get("/samples/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_samples_invalid_uuid(client):
    r = client.get("/samples/not-a-uuid")
    assert r.status_code == 404


def test_samples_job_not_done(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running", "path": None, "png_path": None, "message": "", "tsv_path": None, "samples": ["S1"], "pathways": []}
    with TestClient(app) as c:
        r = c.get(f"/samples/{job_id}")
    assert r.status_code == 400
    del _jobs[job_id]


def test_samples_done_returns_list(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    job = _make_done_job(tmp_path)
    job["samples"] = ["Sample1", "Sample2"]
    _jobs[job_id] = job
    with TestClient(app) as c:
        r = c.get(f"/samples/{job_id}")
    assert r.status_code == 200
    assert r.json()["samples"] == ["Sample1", "Sample2"]
    del _jobs[job_id]


# ---------------------------------------------------------------------------
# /pathways route
# ---------------------------------------------------------------------------


def test_pathways_not_found(client):
    r = client.get("/pathways/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_pathways_invalid_uuid(client):
    r = client.get("/pathways/not-a-uuid")
    assert r.status_code == 404


def test_pathways_job_not_done(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "path": None, "png_path": None, "message": "", "tsv_path": None, "samples": [], "pathways": ["p1"]}
    with TestClient(app) as c:
        r = c.get(f"/pathways/{job_id}")
    assert r.status_code == 400
    del _jobs[job_id]


def test_pathways_done_returns_list(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    job = _make_done_job(tmp_path)
    job["pathways"] = ["glycolysis", "TCA Cycle"]
    _jobs[job_id] = job
    with TestClient(app) as c:
        r = c.get(f"/pathways/{job_id}")
    assert r.status_code == 200
    assert "glycolysis" in r.json()["pathways"]
    del _jobs[job_id]


# ---------------------------------------------------------------------------
# /viz route
# ---------------------------------------------------------------------------


def test_viz_invalid_plot_type(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = _make_done_job(tmp_path)
    with TestClient(app) as c:
        r = c.post(f"/viz/{job_id}", data={"plot_type": "invalid_type"})
    assert r.status_code == 422
    del _jobs[job_id]


def test_viz_invalid_uuid(client):
    r = client.post("/viz/not-a-uuid", data={"plot_type": "barplot"})
    assert r.status_code == 404


def test_viz_not_found(client):
    r = client.post("/viz/00000000-0000-0000-0000-000000000000", data={"plot_type": "barplot"})
    assert r.status_code == 404


def test_viz_job_not_done(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running", "path": None, "png_path": None, "message": "", "tsv_path": None, "samples": [], "pathways": []}
    with TestClient(app) as c:
        r = c.post(f"/viz/{job_id}", data={"plot_type": "barplot"})
    assert r.status_code == 400
    del _jobs[job_id]


def test_viz_no_tsv_path(tmp_path):
    from kegganog.app import _jobs
    import uuid
    job_id = str(uuid.uuid4())
    job = _make_done_job(tmp_path)
    job["tsv_path"] = None
    _jobs[job_id] = job
    with TestClient(app) as c:
        r = c.post(f"/viz/{job_id}", data={"plot_type": "barplot"})
    assert r.status_code == 400
    del _jobs[job_id]


@pytest.mark.asyncio
async def test_viz_barplot_with_real_tsv(tmp_path):
    """Test /viz/{job_id} with barplot using a real TSV fixture."""
    from kegganog.app import _jobs, _blocking_viz
    import uuid
    from pathlib import Path

    fixtures = Path(__file__).parent / "fixtures"
    tsv_path = fixtures / "simple_decoder.tsv"

    job_id = str(uuid.uuid4())
    png_path = tmp_path / "preview.png"
    zip_path = tmp_path / "results.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("dummy.txt", "x")

    _jobs[job_id] = {
        "status": "done",
        "path": str(zip_path),
        "png_path": str(png_path),
        "tsv_path": str(tsv_path),
        "samples": ["TEST"],
        "pathways": ["a1", "a2"],
        "message": "",
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(f"/viz/{job_id}", data={"plot_type": "barplot"})

    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("image/png")
    del _jobs[job_id]


# ---------------------------------------------------------------------------
# Upload size limit
# ---------------------------------------------------------------------------


def test_run_upload_too_large(client):
    from kegganog.app import MAX_UPLOAD_BYTES_SINGLE

    oversized = b"x" * (MAX_UPLOAD_BYTES_SINGLE + 1)
    r = client.post(
        "/run",
        files={"file": ("big.tsv", oversized, "text/tab-separated-values")},
        data={"dpi": 300},
    )
    assert r.status_code == 413


# ---------------------------------------------------------------------------
# run-multi: too many files
# ---------------------------------------------------------------------------


def test_run_multi_too_many_files(client):
    from kegganog.app import MAX_MULTI_UPLOAD_FILES
    files = [
        ("files", (f"f{i}.tsv", b"x", "text/tab-separated-values"))
        for i in range(MAX_MULTI_UPLOAD_FILES + 1)
    ]
    r = client.post("/run-multi", files=files, data={})
    assert r.status_code == 413
