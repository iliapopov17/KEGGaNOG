import matplotlib

matplotlib.use("Agg")

import asyncio
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .schemas import JobStatus, WebParams
from .version import __version__

# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="KEGGaNOG",
    version=__version__,
    docs_url=None,
    redoc_url=None,
)

_static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# ---------------------------------------------------------------------------
# In-memory job store
#
# Keys are job UUIDs (strings).
# Values are dicts with keys:
#   status, path, png_path, message, tsv_path, samples, pathways
#
# tsv_path  — path to the merged_pathways.tsv (multi) or *_pathways.tsv (single)
# samples   — list of sample names (multi only), used for ordering UI
# pathways  — list of pathway names (multi only), used for radarplot UI
# ---------------------------------------------------------------------------

_jobs: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Route 1: serve the HTML interface
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    from .version import __version__
    html_file = Path(__file__).parent / "static" / "index.html"
    html = html_file.read_text(encoding="utf-8").replace("__VERSION__", __version__)
    return HTMLResponse(html)


# ---------------------------------------------------------------------------
# Route 2: single-sample analysis
# ---------------------------------------------------------------------------


@app.post("/run", response_model=JobStatus)
async def run_analysis(
    file: UploadFile,
    dpi: int = Form(default=300),
    color: str = Form(default="Blues"),
    sample_name: str = Form(default="SAMPLE"),
    group: bool = Form(default=False),
) -> JobStatus:
    try:
        params = WebParams(dpi=dpi, color=color, sample_name=sample_name, group=group)
    except ValidationError as e:
        messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return JSONResponse(status_code=422, content={"detail": messages})

    file_bytes = await file.read()
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending", "path": None, "png_path": None,
        "message": "", "tsv_path": None, "samples": [], "pathways": [],
    }
    asyncio.create_task(_run_job(job_id, file_bytes, params))
    return JobStatus(job_id=job_id, status="pending")


# ---------------------------------------------------------------------------
# Route 3: multi-sample analysis
# ---------------------------------------------------------------------------


@app.post("/run-multi", response_model=JobStatus)
async def run_analysis_multi(
    files: List[UploadFile],
    dpi: int = Form(default=300),
    color: str = Form(default="Blues"),
    group: bool = Form(default=False),
) -> JobStatus:
    if not files:
        return JSONResponse(
            status_code=422, content={"detail": ["files: at least one file required."]}
        )
    try:
        params = WebParams(dpi=dpi, color=color, sample_name="MULTI", group=group)
    except ValidationError as e:
        messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return JSONResponse(status_code=422, content={"detail": messages})

    named_files: list[tuple[str, bytes]] = []
    for f in files:
        named_files.append((f.filename or "sample.annotations", await f.read()))

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending", "path": None, "png_path": None,
        "message": "", "tsv_path": None, "samples": [], "pathways": [],
    }
    asyncio.create_task(_run_job_multi(job_id, named_files, params))
    return JobStatus(job_id=job_id, status="pending")


# ---------------------------------------------------------------------------
# Route 4: poll job status
# ---------------------------------------------------------------------------


@app.get("/status/{job_id}", response_model=None)
async def get_status(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(
            status_code=404, content={"detail": f"Job '{job_id}' not found."}
        )
    return JobStatus(job_id=job_id, status=job["status"], message=job["message"])


# ---------------------------------------------------------------------------
# Route 5: serve the PNG heatmap for in-browser preview
# ---------------------------------------------------------------------------


@app.get("/preview/{job_id}", response_model=None)
async def preview(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": "Job not found."})
    if job["status"] != "done":
        return JSONResponse(status_code=400, content={"detail": "Analysis not finished yet."})
    return FileResponse(path=job["png_path"], media_type="image/png")


# ---------------------------------------------------------------------------
# Route 6: download the full results ZIP
# ---------------------------------------------------------------------------


@app.get("/download/{job_id}", response_model=None)
async def download(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": "Job not found."})
    if job["status"] != "done":
        return JSONResponse(status_code=400, content={"detail": "Analysis not finished yet."})
    return FileResponse(
        path=job["path"],
        media_type="application/zip",
        filename=f"kegganog_{job_id[:8]}.zip",
    )


# ---------------------------------------------------------------------------
# Route 7: return sample list (multi jobs only)
# ---------------------------------------------------------------------------


@app.get("/samples/{job_id}", response_model=None)
async def get_samples(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": "Job not found."})
    if job["status"] != "done":
        return JSONResponse(status_code=400, content={"detail": "Analysis not finished yet."})
    return JSONResponse(content={"samples": job["samples"]})


# ---------------------------------------------------------------------------
# Route 8: return pathway list (multi jobs only, for radarplot)
# ---------------------------------------------------------------------------


@app.get("/pathways/{job_id}", response_model=None)
async def get_pathways(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": "Job not found."})
    if job["status"] != "done":
        return JSONResponse(status_code=400, content={"detail": "Analysis not finished yet."})
    return JSONResponse(content={"pathways": job["pathways"]})


# ---------------------------------------------------------------------------
# Route 9: run a visualization API on an existing job's data
# ---------------------------------------------------------------------------


@app.post("/viz/{job_id}", response_model=None)
async def run_viz(
    job_id: str,
    plot_type: str = Form(...),
    # ---- shared ----
    dpi: int = Form(default=300),
    figwidth: int = Form(default=0),
    figheight: int = Form(default=0),
    title: str = Form(default=""),
    title_fontsize: float = Form(default=16.0),
    title_color: str = Form(default="black"),
    title_weight: str = Form(default="normal"),
    title_style: str = Form(default="normal"),
    background_color: str = Form(default="white"),
    # ---- axis labels ----
    xlabel: str = Form(default=""),
    xlabel_fontsize: float = Form(default=14.0),
    xlabel_color: str = Form(default="black"),
    xlabel_weight: str = Form(default="normal"),
    xlabel_style: str = Form(default="normal"),
    ylabel: str = Form(default=""),
    ylabel_fontsize: float = Form(default=14.0),
    ylabel_color: str = Form(default="black"),
    ylabel_weight: str = Form(default="normal"),
    ylabel_style: str = Form(default="normal"),
    # ---- ticks ----
    xticks_fontsize: float = Form(default=12.0),
    xticks_color: str = Form(default="black"),
    xticks_weight: str = Form(default="normal"),
    xticks_style: str = Form(default="normal"),
    xticks_rotation: float = Form(default=0.0),
    xticks_ha: str = Form(default="center"),
    yticks_fontsize: float = Form(default=12.0),
    yticks_color: str = Form(default="black"),
    yticks_weight: str = Form(default="normal"),
    yticks_style: str = Form(default="normal"),
    # ---- grid ----
    grid: bool = Form(default=True),
    grid_linestyle: str = Form(default="--"),
    grid_alpha: float = Form(default=0.7),
    # ---- barplot-specific ----
    cmap: str = Form(default=""),
    cmap_range_min: int = Form(default=8),
    cmap_range_max: int = Form(default=30),
    sort_order: str = Form(default="descending"),
    # ---- boxplot-specific ----
    box_color: str = Form(default="blue"),
    showfliers: bool = Form(default=True),
    grid_color: str = Form(default="gray"),
    grid_linewidth: float = Form(default=0.5),
    # ---- corrnet-specific ----
    threshold: float = Form(default=0.5),
    node_size: float = Form(default=700.0),
    node_color: str = Form(default="#A3D5FF"),
    node_edgecolors: str = Form(default="#03045E"),
    node_linewidths: float = Form(default=1.5),
    label_fontsize: float = Form(default=8.0),
    label_color: str = Form(default="#03045E"),
    label_weight: str = Form(default="normal"),
    edge_cmap: str = Form(default="coolwarm"),
    cbar_size: float = Form(default=0.5),
    # ---- radarplot-specific ----
    pathways_selected: str = Form(default=""),   # JSON array string
    colors_selected: str = Form(default=""),     # JSON array string
    sample_order: str = Form(default=""),        # JSON array string
    fill_alpha: float = Form(default=0.25),
    line_width: float = Form(default=2.0),
    line_style: str = Form(default="solid"),
    label_background: str = Form(default=""),
    label_edgecolor: str = Form(default=""),
    label_pad: float = Form(default=1.05),
    show_legend: bool = Form(default=True),
    legend_loc: str = Form(default="upper right"),
    # ---- stackedbar / streamgraph ----
    bar_width: float = Form(default=0.6),
    edgecolor: str = Form(default="black"),
    edge_linewidth: float = Form(default=0.3),
    stream_fill_alpha: float = Form(default=1.0),
    legend_fontsize: float = Form(default=9.0),
    legend_bbox_x: float = Form(default=1.05),
    legend_bbox_y: float = Form(default=1.0),
    # ---- heatmap-specific ----
    heatmap_color: str = Form(default="Blues"),
    heatmap_group: bool = Form(default=False),
    heatmap_sample_name: str = Form(default=""),
    heatmap_dpi: int = Form(default=300),
):
    import json

    job = _jobs.get(job_id)
    if job is None:
        return JSONResponse(status_code=404, content={"detail": "Job not found."})
    if job["status"] != "done":
        return JSONResponse(status_code=400, content={"detail": "Analysis not finished yet."})
    if not job.get("tsv_path"):
        return JSONResponse(status_code=400, content={"detail": "No TSV data available for this job."})

    def _parse_json_list(s: str) -> list:
        s = s.strip()
        if not s:
            return []
        try:
            return json.loads(s)
        except Exception:
            return []

    figsize = (figwidth, figheight) if figwidth > 0 and figheight > 0 else None

    loop = asyncio.get_event_loop()
    try:
        png_path = await loop.run_in_executor(
            None, _blocking_viz,
            job["tsv_path"], plot_type, figsize, dpi,
            heatmap_color, heatmap_group, heatmap_sample_name, heatmap_dpi,
            title, title_fontsize, title_color, title_weight, title_style,
            background_color,
            xlabel, xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style,
            ylabel, ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style,
            xticks_fontsize, xticks_color, xticks_weight, xticks_style,
            xticks_rotation, xticks_ha,
            yticks_fontsize, yticks_color, yticks_weight, yticks_style,
            grid, grid_linestyle, grid_alpha,
            cmap, cmap_range_min, cmap_range_max, sort_order,
            box_color, showfliers, grid_color, grid_linewidth,
            threshold, node_size, node_color, node_edgecolors, node_linewidths,
            label_fontsize, label_color, label_weight, edge_cmap, cbar_size,
            _parse_json_list(pathways_selected),
            _parse_json_list(colors_selected),
            _parse_json_list(sample_order),
            fill_alpha, line_width, line_style,
            label_background or None, label_edgecolor or None, label_pad,
            show_legend, legend_loc,
            bar_width, edgecolor, edge_linewidth, stream_fill_alpha,
            legend_fontsize, (legend_bbox_x, legend_bbox_y),
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    return FileResponse(path=png_path, media_type="image/png")


# ---------------------------------------------------------------------------
# Background workers
# ---------------------------------------------------------------------------


async def _run_job(job_id: str, file_bytes: bytes, params: WebParams) -> None:
    _jobs[job_id]["status"] = "running"
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _blocking_analysis, file_bytes, params)
        _jobs[job_id].update({"status": "done", **result})
    except Exception as e:
        _jobs[job_id].update({"status": "error", "message": str(e)})


async def _run_job_multi(
    job_id: str, named_files: list[tuple[str, bytes]], params: WebParams
) -> None:
    _jobs[job_id]["status"] = "running"
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, _blocking_analysis_multi, named_files, params
        )
        _jobs[job_id].update({"status": "done", **result})
    except Exception as e:
        _jobs[job_id].update({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# Blocking analysis functions (run in worker threads)
# ---------------------------------------------------------------------------


def _pack_results(output_dir: Path) -> tuple[str, str]:
    png_files = list(output_dir.rglob("*.png"))
    if not png_files:
        raise FileNotFoundError(
            "KEGGaNOG finished but produced no PNG file. "
            "Check that the input file is a valid eggNOG-mapper annotation."
        )
    stable_png = Path(tempfile.mktemp(suffix=".png"))
    shutil.copy2(png_files[0], stable_png)

    stable_zip = Path(tempfile.mktemp(suffix=".zip"))
    with zipfile.ZipFile(stable_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for result_file in output_dir.rglob("*"):
            if result_file.is_file():
                zf.write(result_file, result_file.relative_to(output_dir))

    return str(stable_zip), str(stable_png)


def _blocking_analysis(file_bytes: bytes, params: WebParams) -> dict:
    from .processing import data_processing
    from .cheatmaps import simple_heatmap, grouped_heatmap

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        input_file = tmpdir / "input.annotations"
        input_file.write_bytes(file_bytes)

        output_dir = tmpdir / "output"
        output_dir.mkdir()
        temp_folder = output_dir / "temp_files"
        temp_folder.mkdir()

        parsed_file = data_processing.parse_emapper(str(input_file), str(temp_folder))
        kegg_decoder_file = data_processing.run_kegg_decoder(
            parsed_file, str(output_dir), params.sample_name
        )

        if params.group:
            grouped_heatmap.generate_grouped_heatmap(
                kegg_decoder_file, str(output_dir), params.dpi, params.color, params.sample_name
            )
        else:
            simple_heatmap.generate_heatmap(
                kegg_decoder_file, str(output_dir), params.dpi, params.color, params.sample_name
            )

        # Read TSV to extract pathway list for viz
        df = pd.read_csv(kegg_decoder_file, sep="\t", index_col=0)
        pathways = list(df.columns)

        # Copy TSV to a stable path for later viz calls
        stable_tsv = Path(tempfile.mktemp(suffix=".tsv"))
        shutil.copy2(kegg_decoder_file, stable_tsv)

        zip_path, png_path = _pack_results(output_dir)

    return {
        "path": zip_path,
        "png_path": png_path,
        "tsv_path": str(stable_tsv),
        "samples": [params.sample_name],
        "pathways": pathways,
    }


def _blocking_analysis_multi(
    named_files: list[tuple[str, bytes]], params: WebParams
) -> dict:
    from .processing import data_processing_multi
    from .cheatmaps import simple_heatmap_multi, grouped_heatmap_multi

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        output_dir = tmpdir / "output"
        output_dir.mkdir()
        temp_folder = output_dir / "temp_files"
        temp_folder.mkdir()

        for filename, file_bytes in named_files:
            file_prefix = filename.replace(".emapper.annotations", "")
            file_prefix = Path(file_prefix).stem if "." in file_prefix else file_prefix

            sample_folder = temp_folder / file_prefix
            sample_folder.mkdir(exist_ok=True)

            input_file = sample_folder / filename
            input_file.write_bytes(file_bytes)

            parsed_file = data_processing_multi.parse_emapper(
                str(input_file), str(sample_folder), file_prefix
            )
            data_processing_multi.run_kegg_decoder(
                parsed_file, str(sample_folder), file_prefix
            )

        merged_df = data_processing_multi.merge_outputs(str(output_dir))

        if params.group:
            grouped_heatmap_multi.generate_grouped_heatmap_multi(
                merged_df, str(output_dir), params.dpi, params.color
            )
        else:
            simple_heatmap_multi.generate_heatmap_multi(
                merged_df, str(output_dir), params.dpi, params.color
            )

        # Extract sample and pathway names for viz UI
        samples = [c for c in merged_df.columns if c != "Function"]
        pathways = list(merged_df["Function"].dropna().unique())

        # Save merged TSV to stable path for later viz calls
        stable_tsv = Path(tempfile.mktemp(suffix=".tsv"))
        merged_tsv = output_dir / "merged_pathways.tsv"
        shutil.copy2(merged_tsv, stable_tsv)

        zip_path, png_path = _pack_results(output_dir)

    return {
        "path": zip_path,
        "png_path": png_path,
        "tsv_path": str(stable_tsv),
        "samples": samples,
        "pathways": pathways,
    }


# ---------------------------------------------------------------------------
# Blocking visualization function (run in worker thread)
# ---------------------------------------------------------------------------


def _blocking_viz(
    tsv_path: str,
    plot_type: str,
    figsize,
    dpi: int,
    heatmap_color: str,
    heatmap_group: bool,
    heatmap_sample_name: str,
    heatmap_dpi: int,
    title, title_fontsize, title_color, title_weight, title_style,
    background_color,
    xlabel, xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style,
    ylabel, ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style,
    xticks_fontsize, xticks_color, xticks_weight, xticks_style,
    xticks_rotation, xticks_ha,
    yticks_fontsize, yticks_color, yticks_weight, yticks_style,
    grid, grid_linestyle, grid_alpha,
    cmap, cmap_range_min, cmap_range_max, sort_order,
    box_color, showfliers, grid_color, grid_linewidth,
    threshold, node_size, node_color, node_edgecolors, node_linewidths,
    label_fontsize, label_color, label_weight, edge_cmap_name, cbar_size,
    pathways_selected, colors_selected, sample_order,
    fill_alpha, line_width, line_style,
    label_background, label_edgecolor, label_pad,
    show_legend, legend_loc,
    bar_width, edgecolor, edge_linewidth, stream_fill_alpha,
    legend_fontsize, legend_bbox,
) -> str:
    import matplotlib.pyplot as plt
    from .kgnplot import barplot as bp, corrnet as cn, radarplot as rp
    from .kgnplot import stackedbar as sb, streamgraph as sg
    from .cheatmaps import (
        simple_heatmap, grouped_heatmap,
        simple_heatmap_multi, grouped_heatmap_multi,
    )

    df = pd.read_csv(tsv_path, sep="\t")

    # Apply sample ordering if provided (multi plots)
    if sample_order:
        ordered_cols = ["Function"] + [s for s in sample_order if s in df.columns]
        remaining = [c for c in df.columns if c not in ordered_cols]
        df = df[ordered_cols + remaining]

    title_val = title if title else None
    cmap_val = cmap if cmap else None

    out_path = Path(tempfile.mktemp(suffix=".png"))

    if plot_type == "barplot":
        fs = figsize or (8, 12)
        plot = bp.barplot(
            df,
            figsize=fs,
            cmap=cmap_val or "Greens",
            cmap_range=(cmap_range_min, cmap_range_max),
            title=title_val,
            title_fontsize=title_fontsize, title_color=title_color,
            title_weight=title_weight, title_style=title_style,
            xlabel=xlabel or "Pathway completeness",
            xlabel_fontsize=xlabel_fontsize, xlabel_color=xlabel_color,
            xlabel_weight=xlabel_weight, xlabel_style=xlabel_style,
            ylabel=ylabel or "Pathway",
            ylabel_fontsize=ylabel_fontsize, ylabel_color=ylabel_color,
            ylabel_weight=ylabel_weight, ylabel_style=ylabel_style,
            xticks_fontsize=xticks_fontsize, xticks_color=xticks_color,
            xticks_weight=xticks_weight, xticks_style=xticks_style,
            yticks_fontsize=yticks_fontsize, yticks_color=yticks_color,
            yticks_weight=yticks_weight, yticks_style=yticks_style,
            grid=grid, grid_linestyle=grid_linestyle, grid_alpha=grid_alpha,
            background_color=background_color,
            sort_order=sort_order,
        )

    elif plot_type == "corrnet":
        import matplotlib.cm as mcm
        fs = figsize or (12, 6)
        edge_cmap_obj = getattr(mcm, edge_cmap_name, plt.cm.coolwarm)
        plot = cn.correlation_network(
            df,
            figsize=fs,
            threshold=threshold,
            node_size=node_size,
            node_color=node_color,
            node_edgecolors=node_edgecolors,
            node_linewidths=node_linewidths,
            label_fontsize=label_fontsize, label_color=label_color,
            label_weight=label_weight,
            edge_cmap=edge_cmap_obj,
            cbar_size=cbar_size,
            title=title_val,
            title_fontsize=title_fontsize, title_color=title_color,
            title_weight=title_weight, title_style=title_style,
            background_color=background_color,
        )

    elif plot_type == "radarplot":
        fs = figsize or (8, 8)
        pwlist = pathways_selected if pathways_selected else None
        if not pwlist:
            raise ValueError("Please select 1–4 pathways for the radar plot.")
        clrs = colors_selected if colors_selected else None
        sord = sample_order if sample_order else None
        plot = rp.radarplot(
            df,
            pathways=pwlist,
            figsize=fs,
            colors=clrs,
            sample_order=sord,
            title=title_val,
            title_fontsize=title_fontsize, title_color=title_color,
            title_weight=title_weight, title_style=title_style,
            label_fontsize=label_fontsize, label_color=label_color,
            label_weight=label_weight, label_style=xticks_style,
            label_background=label_background,
            label_edgecolor=label_edgecolor,
            label_pad=label_pad,
            ytick_fontsize=yticks_fontsize, ytick_color=yticks_color,
            ytick_weight=yticks_weight,
            fill_alpha=fill_alpha, line_width=line_width, line_style=line_style,
            background_color=background_color,
            legend_loc=legend_loc, legend_bbox=legend_bbox,
            show_legend=show_legend,
        )

    elif plot_type == "stackedbar":
        fs = figsize or (14, 7)
        plot = sb.stacked_barplot(
            df,
            figsize=fs,
            cmap=cmap_val or "tab20",
            bar_width=bar_width,
            edgecolor=edgecolor,
            edge_linewidth=edge_linewidth,
            title=title_val,
            title_fontsize=title_fontsize, title_color=title_color,
            title_weight=title_weight, title_style=title_style,
            xlabel=xlabel or "Samples",
            xlabel_fontsize=xlabel_fontsize, xlabel_color=xlabel_color,
            xlabel_weight=xlabel_weight, xlabel_style=xlabel_style,
            ylabel=ylabel or "Total Completeness",
            ylabel_fontsize=ylabel_fontsize, ylabel_color=ylabel_color,
            ylabel_weight=ylabel_weight, ylabel_style=ylabel_style,
            xticks_rotation=xticks_rotation, xticks_ha=xticks_ha,
            xticks_fontsize=xticks_fontsize, xticks_color=xticks_color,
            xticks_weight=xticks_weight, xticks_style=xticks_style,
            background_color=background_color,
            grid=grid, grid_linestyle=grid_linestyle, grid_alpha=grid_alpha,
            legend_fontsize=legend_fontsize, legend_loc=legend_loc,
            legend_bbox=legend_bbox, show_legend=show_legend,
        )

    elif plot_type == "streamgraph":
        fs = figsize or (14, 7)
        plot = sg.streamgraph(
            df,
            figsize=fs,
            cmap=cmap_val or "tab20",
            bar_width=bar_width,
            fill_alpha=stream_fill_alpha,
            edgecolor=edgecolor or None,
            edge_linewidth=edge_linewidth,
            title=title_val,
            title_fontsize=title_fontsize, title_color=title_color,
            title_weight=title_weight, title_style=title_style,
            xlabel=xlabel or "Samples",
            xlabel_fontsize=xlabel_fontsize, xlabel_color=xlabel_color,
            xlabel_weight=xlabel_weight, xlabel_style=xlabel_style,
            ylabel=ylabel or "Total Completeness",
            ylabel_fontsize=ylabel_fontsize, ylabel_color=ylabel_color,
            ylabel_weight=ylabel_weight, ylabel_style=ylabel_style,
            xticks_rotation=xticks_rotation, xticks_ha=xticks_ha,
            xticks_fontsize=xticks_fontsize, xticks_color=xticks_color,
            xticks_weight=xticks_weight, xticks_style=xticks_style,
            background_color=background_color,
            grid=grid, grid_linestyle=grid_linestyle, grid_alpha=grid_alpha,
            legend_fontsize=legend_fontsize, legend_loc=legend_loc,
            legend_bbox=legend_bbox, show_legend=show_legend,
        )

    elif plot_type == "heatmap":
        # Re-render heatmap from existing TSV with (optionally) reordered samples.
        # Detect single vs multi by checking whether a "Function" column exists.
        is_multi = "Function" in df.columns
        try:
            with tempfile.TemporaryDirectory() as hm_tmp:
                hm_tmp = Path(hm_tmp)
                if is_multi:
                    if heatmap_group:
                        grouped_heatmap_multi.generate_grouped_heatmap_multi(
                            df, str(hm_tmp), heatmap_dpi, heatmap_color
                        )
                    else:
                        simple_heatmap_multi.generate_heatmap_multi(
                            df, str(hm_tmp), heatmap_dpi, heatmap_color
                        )
                else:
                    sample_name = heatmap_sample_name if heatmap_sample_name else "SAMPLE"
                    if heatmap_group:
                        grouped_heatmap.generate_grouped_heatmap(
                            tsv_path, str(hm_tmp), heatmap_dpi, heatmap_color, sample_name
                        )
                    else:
                        simple_heatmap.generate_heatmap(
                            tsv_path, str(hm_tmp), heatmap_dpi, heatmap_color, sample_name
                        )
                png_files = list(hm_tmp.rglob("*.png"))
                if not png_files:
                    raise FileNotFoundError("Heatmap generation produced no PNG.")
                shutil.copy2(png_files[0], out_path)
        finally:
            plt.close("all")
        return str(out_path)

    else:
        raise ValueError(f"Unknown plot_type: {plot_type!r}")

    plot.savefig(str(out_path), dpi=dpi)
    plt.close("all")
    return str(out_path)
