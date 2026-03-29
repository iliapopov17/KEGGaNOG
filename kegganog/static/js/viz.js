// ==========================================================================
// Visualization — send parameters to /viz/{job_id}, display result image
// ==========================================================================

// Shorthand DOM accessors
const v    = id => document.getElementById(id);
const val  = id => v(id)?.value ?? "";
const chk  = id => v(id)?.checked ?? false;
const num  = (id, def) => parseFloat(v(id)?.value) || def;
const int_ = (id, def) => parseInt(v(id)?.value)   || def;

async function runViz(plotType) {
  if (!currentJobId) return;

  const btn  = v(`btn-viz-${plotType}`) || v("btn-rerender-heatmap");
  const img  = v(`viz-img-${plotType}`);
  const stat = v(`viz-status-${plotType}`);
  const dl   = v(`dl-${plotType}-png`) || v(`dl-${plotType}`);

  if (btn)  btn.disabled = true;
  if (img)  img.style.display = "none";
  if (dl)   dl.classList.add("hidden");
  if (stat) { stat.className = "viz-status running"; stat.textContent = "Generating plot…"; }

  const sampleOrder = getSampleOrder();
  const form = new FormData();
  form.append("plot_type", plotType);

  if (plotType === "heatmap") {
    form.append("heatmap_color",       val("hm-color") || val("single-color") || val("multi-color") || "Blues");
    form.append("heatmap_group",       chk("hm-group") || chk("single-group") || chk("multi-group") || false);
    form.append("heatmap_dpi",         int_("hm-dpi", 300));
    form.append("heatmap_sample_name", val("single-sample-name") || "SAMPLE");
    form.append("sample_order",        JSON.stringify(sampleOrder));

  } else if (plotType === "barplot") {
    form.append("dpi",            int_("bp-dpi", 300));
    form.append("figwidth",       int_("bp-fw", 8));
    form.append("figheight",      int_("bp-fh", 12));
    form.append("cmap",           val("bp-cmap"));
    form.append("cmap_range_min", int_("bp-cmap-min", 8));
    form.append("cmap_range_max", int_("bp-cmap-max", 30));
    form.append("sort_order",     val("bp-sort"));
    form.append("title",          val("bp-title"));
    form.append("title_fontsize", num("bp-tfs", 16));
    form.append("title_color",    val("bp-tc"));
    form.append("title_weight",   val("bp-tw"));
    form.append("title_style",    val("bp-ts"));
    form.append("background_color", val("bp-bg"));
    form.append("xlabel",         val("bp-xlabel"));
    form.append("xlabel_fontsize",num("bp-xlfs", 14));
    form.append("xlabel_color",   val("bp-xlc"));
    form.append("xlabel_weight",  val("bp-xlw"));
    form.append("xlabel_style",   val("bp-xls"));
    form.append("ylabel",         val("bp-ylabel"));
    form.append("ylabel_fontsize",num("bp-ylfs", 14));
    form.append("ylabel_color",   val("bp-ylc"));
    form.append("ylabel_weight",  val("bp-ylw"));
    form.append("ylabel_style",   val("bp-yls"));
    form.append("xticks_fontsize",num("bp-xtfs", 12));
    form.append("xticks_color",   val("bp-xtc"));
    form.append("xticks_weight",  val("bp-xtw"));
    form.append("xticks_style",   val("bp-xts"));
    form.append("yticks_fontsize",num("bp-ytfs", 12));
    form.append("yticks_color",   val("bp-ytc"));
    form.append("yticks_weight",  val("bp-ytw"));
    form.append("yticks_style",   val("bp-yts"));
    form.append("grid",           chk("bp-grid"));
    form.append("grid_linestyle", val("bp-grid-ls"));
    form.append("grid_alpha",     num("bp-grid-alpha", 0.7));

  } else if (plotType === "corrnet") {
    form.append("dpi",             int_("cn-dpi", 300));
    form.append("figwidth",        int_("cn-fw", 12));
    form.append("figheight",       int_("cn-fh", 6));
    form.append("threshold",       num("cn-threshold", 0.5));
    form.append("node_size",       num("cn-node-size", 700));
    form.append("node_color",      val("cn-node-color"));
    form.append("node_edgecolors", val("cn-node-ec"));
    form.append("node_linewidths", num("cn-node-lw", 1.5));
    form.append("label_fontsize",  num("cn-lfs", 8));
    form.append("label_color",     val("cn-lc"));
    form.append("label_weight",    val("cn-lw"));
    form.append("edge_cmap",       val("cn-edge-cmap"));
    form.append("cbar_size",       num("cn-cbar", 0.5));
    form.append("title",           val("cn-title"));
    form.append("title_fontsize",  num("cn-tfs", 16));
    form.append("title_color",     val("cn-tc"));
    form.append("title_weight",    val("cn-tw"));
    form.append("title_style",     val("cn-ts"));
    form.append("background_color",val("cn-bg"));
    form.append("sample_order",    JSON.stringify(sampleOrder));

  } else if (plotType === "radarplot") {
    const pws = getSelectedPathways();
    if (pws.length < 1 || pws.length > 4) {
      if (stat) { stat.className = "viz-status error"; stat.textContent = "Select 1–4 pathways."; }
      if (btn) btn.disabled = false; return;
    }
    const colors = getRadarColors();
    form.append("dpi",               int_("rp-dpi", 300));
    form.append("figwidth",          int_("rp-fw", 8));
    form.append("figheight",         int_("rp-fh", 8));
    form.append("pathways_selected", JSON.stringify(pws));
    form.append("colors_selected",   colors.every(c => c === "#000000") ? "[]" : JSON.stringify(colors));
    form.append("sample_order",      JSON.stringify(sampleOrder));
    form.append("fill_alpha",        num("rp-fill-alpha", 0.25));
    form.append("line_width",        num("rp-lw", 2.0));
    form.append("line_style",        val("rp-ls"));
    form.append("label_background",  val("rp-lbg"));
    form.append("label_pad",         num("rp-lpad", 1.05));
    form.append("show_legend",       chk("rp-legend"));
    form.append("legend_loc",        val("rp-legend-loc"));
    form.append("legend_bbox_x",     num("rp-legend-bx", 1.3));
    form.append("legend_bbox_y",     num("rp-legend-by", 1.1));
    form.append("title",             val("rp-title"));
    form.append("title_fontsize",    num("rp-tfs", 14));
    form.append("title_color",       val("rp-tc"));
    form.append("title_weight",      val("rp-tw"));
    form.append("title_style",       val("rp-ts"));
    form.append("background_color",  val("rp-bg"));
    form.append("label_fontsize",    num("rp-lfs", 10));
    form.append("label_color",       val("rp-lc"));
    form.append("label_weight",      val("rp-lw-font"));
    form.append("yticks_fontsize",   num("rp-ytfs", 8));
    form.append("yticks_color",      val("rp-ytc"));
    form.append("yticks_weight",     val("rp-ytw"));

  } else {
    // stackedbar / streamgraph
    const p      = plotType === "stackedbar" ? "sbar" : "sg";
    const stream = plotType === "streamgraph";
    form.append("dpi",            int_(`${p}-dpi`, 300));
    form.append("figwidth",       int_(`${p}-fw`, 14));
    form.append("figheight",      int_(`${p}-fh`, 7));
    form.append("cmap",           val(`${p}-cmap`));
    form.append("bar_width",      num(`${p}-bw`, 0.6));
    form.append("edgecolor",      val(`${p}-ec`));
    form.append("edge_linewidth", num(`${p}-elw`, 0.3));
    if (stream) form.append("stream_fill_alpha", num(`${p}-fill-alpha`, 1.0));
    form.append("title",          val(`${p}-title`));
    form.append("title_fontsize", num(`${p}-tfs`, 16));
    form.append("title_color",    val(`${p}-tc`));
    form.append("title_weight",   val(`${p}-tw`));
    form.append("title_style",    val(`${p}-ts`));
    form.append("background_color", val(`${p}-bg`));
    form.append("xlabel",         val(`${p}-xlabel`));
    form.append("xlabel_fontsize",num(`${p}-xlfs`, 12));
    form.append("xlabel_color",   val(`${p}-xlc`));
    form.append("xlabel_weight",  val(`${p}-xlw`));
    form.append("xlabel_style",   val(`${p}-xls`));
    form.append("ylabel",         val(`${p}-ylabel`));
    form.append("ylabel_fontsize",num(`${p}-ylfs`, 12));
    form.append("ylabel_color",   val(`${p}-ylc`));
    form.append("ylabel_weight",  val(`${p}-ylw`));
    form.append("ylabel_style",   val(`${p}-yls`));
    form.append("xticks_rotation",num(`${p}-xrot`, 0));
    form.append("xticks_ha",      val(`${p}-xha`));
    form.append("xticks_fontsize",num(`${p}-xtfs`, 12));
    form.append("xticks_color",   val(`${p}-xtc`));
    form.append("xticks_weight",  val(`${p}-xtw`));
    form.append("xticks_style",   val(`${p}-xts`));
    form.append("yticks_fontsize",num(`${p}-ytfs`, 12));
    form.append("yticks_color",   val(`${p}-ytc`));
    form.append("yticks_weight",  val(`${p}-ytw`));
    form.append("yticks_style",   val(`${p}-yts`));
    form.append("grid",           chk(`${p}-grid`));
    form.append("grid_linestyle", val(`${p}-grid-ls`));
    form.append("grid_alpha",     num(`${p}-grid-alpha`, 0.7));
    form.append("show_legend",    chk(`${p}-legend`));
    form.append("legend_loc",     val(`${p}-legend-loc`));
    form.append("legend_bbox_x",  num(`${p}-legend-bx`, 1.05));
    form.append("legend_bbox_y",  num(`${p}-legend-by`, 1.0));
    form.append("legend_fontsize",num(`${p}-lgfs`, 9));
    form.append("sample_order",   JSON.stringify(sampleOrder));
  }

  try {
    const r = await fetch(`/viz/${currentJobId}`, { method: "POST", body: form });
    if (!r.ok) {
      const d = await r.json();
      if (stat) { stat.className = "viz-status error"; stat.textContent = d.detail || "Failed."; }
      if (btn) btn.disabled = false; return;
    }
    const blob = await r.blob();
    const url  = URL.createObjectURL(blob);
    if (img)  { img.src = url; img.style.display = "block"; }
    if (stat) stat.className = "viz-status";
    if (dl)   {
      dl.href = url;
      dl.setAttribute("download", `kegganog_${plotType}_${currentJobId.slice(0, 8)}.png`);
      dl.classList.remove("hidden");
    }
  } catch (e) {
    if (stat) { stat.className = "viz-status error"; stat.textContent = "Request failed: " + e.message; }
  }
  if (btn) btn.disabled = false;
}
