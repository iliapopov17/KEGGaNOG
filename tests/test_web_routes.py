"""HTTP-level characterization for the FastAPI surface (no full decoder run)."""

from __future__ import annotations

import asyncio
import io
import zipfile
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from kegganog.app import app
from kegganog.schemas import WebParams


def _minimal_png_bytes() -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.plot([0, 1], [0, 1], color="blue")
    fig.savefig(buf, format="png", dpi=72)
    plt.close(fig)
    return buf.getvalue()


def _fake_blocking_result(workdir: Path) -> dict:
    png_bytes = _minimal_png_bytes()
    png_path = workdir / "preview.png"
    png_path.write_bytes(png_bytes)

    tsv_path = workdir / "pathways.tsv"
    tsv_path.write_text("X\tSAMPLE\na\t1.0\n", encoding="utf-8")

    zip_path = workdir / "results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("heatmap_figure.png", png_bytes)
        zf.writestr("sample_pathways.tsv", tsv_path.read_text(encoding="utf-8"))

    return {
        "path": str(zip_path),
        "png_path": str(png_path),
        "tsv_path": str(tsv_path),
        "samples": ["SAMPLE"],
        "pathways": ["a"],
    }


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_index_returns_html(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    body = r.text
    assert "KEGGaNOG" in body or "kegganog" in body.lower()


def test_run_validation_error(client: TestClient) -> None:
    r = client.post(
        "/run",
        files={"file": ("test.tsv", b"x", "text/tab-separated-values")},
        data={"dpi": 10},
    )
    assert r.status_code == 422


def test_status_not_found(client: TestClient) -> None:
    r = client.get("/status/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_run_completes_with_mocked_pipeline(tmp_path: Path) -> None:
    """Async ASGI client so asyncio.create_task background jobs can finish."""

    def fake_blocking(file_bytes: bytes, params: WebParams) -> dict:
        return _fake_blocking_result(tmp_path)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Keep patch active until the background task finishes (runs after POST returns).
        with patch("kegganog.app._blocking_analysis", fake_blocking):
            r = await ac.post(
                "/run",
                files={"file": ("in.tsv", b"dummy", "text/tab-separated-values")},
                data={
                    "dpi": 300,
                    "color": "Blues",
                    "sample_name": "SAMPLE",
                    "group": "false",
                },
            )
            assert r.status_code == 200, r.text
            job_id = r.json()["job_id"]

            status_payload = None
            for _ in range(100):
                await asyncio.sleep(0.05)
                s = await ac.get(f"/status/{job_id}")
                status_payload = s.json()
                if status_payload.get("status") in ("done", "error"):
                    break
            assert status_payload is not None, job_id
            assert status_payload["status"] == "done", status_payload

            prev = await ac.get(f"/preview/{job_id}")
            assert prev.status_code == 200
            assert prev.headers.get("content-type", "").startswith("image/png")

            dl = await ac.get(f"/download/{job_id}")
            assert dl.status_code == 200
            assert "zip" in dl.headers.get("content-type", "").lower()


def test_run_multi_rejects_empty_files(client: TestClient) -> None:
    r = client.post("/run-multi", files=[], data={})
    assert r.status_code == 422
