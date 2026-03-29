// ==========================================================================
// GitHub stars fetch
// ==========================================================================
fetch("https://api.github.com/repos/iliapopov17/KEGGaNOG")
  .then(r => r.json())
  .then(d => {
    if (d.stargazers_count !== undefined)
      document.getElementById("gh-stars").textContent = d.stargazers_count;
  })
  .catch(() => {});

// ==========================================================================
// Global state
// ==========================================================================
let currentJobId    = null;
let currentMode     = null;   // "single" | "multi"
let currentSamples  = [];
let currentPathways = [];
let activeSubtab    = "heatmap";

// ==========================================================================
// Mode switching
// ==========================================================================
function switchMode(mode) {
  currentMode = mode;
  document.getElementById("mode-single").classList.toggle("active", mode === "single");
  document.getElementById("mode-multi").classList.toggle("active",  mode === "multi");
  document.getElementById("left-single").classList.toggle("hidden", mode !== "single");
  document.getElementById("left-multi").classList.toggle("hidden",  mode !== "multi");
  document.getElementById("left-params-single").classList.toggle("hidden", mode !== "single");
  document.getElementById("left-params-multi").classList.toggle("hidden",  mode !== "multi");
  hideResults();
  hideStatus();
}

// ==========================================================================
// File selection — single
// ==========================================================================
const dropZoneSingle  = document.getElementById("drop-zone-single");
const fileInputSingle = document.getElementById("file-input-single");
let selectedFileSingle = null;

dropZoneSingle.addEventListener("click", () => fileInputSingle.click());
dropZoneSingle.addEventListener("dragover",  e => { e.preventDefault(); dropZoneSingle.classList.add("over"); });
dropZoneSingle.addEventListener("dragleave", () => dropZoneSingle.classList.remove("over"));
dropZoneSingle.addEventListener("drop", e => {
  e.preventDefault(); dropZoneSingle.classList.remove("over");
  if (e.dataTransfer.files[0]) setFileSingle(e.dataTransfer.files[0]);
});
fileInputSingle.addEventListener("change", () => {
  if (fileInputSingle.files[0]) setFileSingle(fileInputSingle.files[0]);
});
function setFileSingle(file) {
  selectedFileSingle = file;
  dropZoneSingle.innerHTML = `<span class="drop-zone-icon">✅</span>${file.name}`;
  dropZoneSingle.classList.add("has-file");
}

// ==========================================================================
// File selection — multi (folder)
// ==========================================================================
const dropZoneMulti  = document.getElementById("drop-zone-multi");
const fileInputMulti = document.getElementById("file-input-multi");
let selectedFilesMulti = null;

const ANNOTATION_EXTS = [".annotations", ".tsv", ".txt"];
const isAnnot = name => ANNOTATION_EXTS.some(ext => name.endsWith(ext));

dropZoneMulti.addEventListener("click", () => fileInputMulti.click());
dropZoneMulti.addEventListener("dragover",  e => { e.preventDefault(); dropZoneMulti.classList.add("over"); });
dropZoneMulti.addEventListener("dragleave", () => dropZoneMulti.classList.remove("over"));
dropZoneMulti.addEventListener("drop", async e => {
  e.preventDefault(); dropZoneMulti.classList.remove("over");
  const files = [];
  async function readDir(dir) {
    const reader = dir.createReader(); let batch;
    do {
      batch = await new Promise((res, rej) => reader.readEntries(res, rej));
      for (const entry of batch) {
        if (entry.isDirectory) await readDir(entry);
        else if (entry.isFile && isAnnot(entry.name)) {
          files.push(await new Promise((res, rej) => entry.file(res, rej)));
        }
      }
    } while (batch.length > 0);
  }
  for (const item of Array.from(e.dataTransfer.items || [])) {
    const entry = item.webkitGetAsEntry?.();
    if (!entry) continue;
    if (entry.isDirectory) await readDir(entry);
    else if (entry.isFile && isAnnot(entry.name))
      files.push(await new Promise((res, rej) => entry.file(res, rej)));
  }
  if (files.length) setFilesMulti(files);
});
fileInputMulti.addEventListener("change", () => {
  const files = Array.from(fileInputMulti.files).filter(f => isAnnot(f.name));
  if (files.length) setFilesMulti(files);
});
function setFilesMulti(files) {
  selectedFilesMulti = files;
  const txt = files.length === 1 ? files[0].name : `${files.length} annotation files found`;
  dropZoneMulti.innerHTML = `<span class="drop-zone-icon">✅</span>${txt}`;
  dropZoneMulti.classList.add("has-file");
}

// ==========================================================================
// Submit
// ==========================================================================
async function submitJob() {
  const mode = currentMode || "single";
  if (mode === "single" && !selectedFileSingle) { alert("Please select an annotation file."); return; }
  if (mode === "multi"  && (!selectedFilesMulti || !selectedFilesMulti.length)) { alert("Please select annotation files."); return; }

  const btn = document.getElementById("btn-run");
  btn.disabled = true;
  hideResults();
  showStatus("running", "Running analysis…");

  const form = new FormData();
  let url;

  if (mode === "single") {
    url = "/run";
    form.append("file",        selectedFileSingle);
    form.append("dpi",         document.getElementById("single-dpi").value);
    form.append("color",       document.getElementById("single-color").value);
    form.append("sample_name", document.getElementById("single-sample-name").value);
    form.append("group",       document.getElementById("single-group").checked);
  } else {
    url = "/run-multi";
    for (const f of selectedFilesMulti) form.append("files", f);
    form.append("dpi",   document.getElementById("multi-dpi").value);
    form.append("color", document.getElementById("multi-color").value);
    form.append("group", document.getElementById("multi-group").checked);
  }

  let jobId;
  try {
    const r = await fetch(url, { method: "POST", body: form });
    const d = await r.json();
    if (!r.ok) { showStatus("error", d.detail ? d.detail.join("; ") : "Submission failed."); btn.disabled = false; return; }
    jobId = d.job_id;
  } catch { showStatus("error", "Could not reach the server."); btn.disabled = false; return; }

  pollStatus(jobId, btn, mode);
}

// ==========================================================================
// Polling
// ==========================================================================
function pollStatus(jobId, btn, mode) {
  const iv = setInterval(async () => {
    try {
      const r = await fetch(`/status/${jobId}`);
      const d = await r.json();
      if (d.status === "done") {
        clearInterval(iv); btn.disabled = false;
        hideStatus(); await showResults(jobId, mode);
      } else if (d.status === "error") {
        clearInterval(iv); btn.disabled = false;
        showStatus("error", d.message || "Analysis failed.");
      }
    } catch { clearInterval(iv); btn.disabled = false; showStatus("error", "Lost connection."); }
  }, 2000);
}

// ==========================================================================
// Show results
// ==========================================================================
async function showResults(jobId, mode) {
  currentJobId = jobId; currentMode = mode;
  const ts = Date.now();

  // Heatmap image
  if (mode === "single") {
    document.getElementById("heatmap-single-result").classList.remove("hidden");
    document.getElementById("heatmap-multi-result").classList.add("hidden");
    document.getElementById("heatmap-rerender").classList.add("hidden");
    document.getElementById("result-img-single").src = `/preview/${jobId}?t=${ts}`;
  } else {
    document.getElementById("heatmap-single-result").classList.add("hidden");
    document.getElementById("heatmap-multi-result").classList.remove("hidden");
    document.getElementById("heatmap-rerender").classList.remove("hidden");
    document.getElementById("heatmap-spoiler").removeAttribute("open");
    document.getElementById("result-img-multi").src = `/preview/${jobId}?t=${ts}`;
  }

  // Download ZIP link
  const dlZip = document.getElementById("dl-heatmap-zip");
  dlZip.href = `/download/${jobId}?t=${ts}`;
  dlZip.setAttribute("download", `kegganog_${jobId.slice(0,8)}.zip`);

  // Build subtabs
  buildSubtabs(mode);

  // Load metadata for multi
  if (mode === "multi") {
    await loadSamples(jobId);
    await loadPathways(jobId);
  }

  // Show center
  document.getElementById("center-placeholder").classList.add("hidden");
  document.getElementById("center-results").classList.remove("hidden");

  // Activate heatmap subtab
  activateSubtab("heatmap");
}

function hideResults() {
  currentJobId = null;
  document.getElementById("center-placeholder").classList.remove("hidden");
  document.getElementById("center-results").classList.add("hidden");
  document.getElementById("right-content").innerHTML =
    '<p style="font-size:12px;color:var(--text-3);">Run an analysis to see plot parameters here.</p>';
}

// ==========================================================================
// Subtabs
// ==========================================================================
const SINGLE_TABS = [
  { id: "heatmap",   label: "Heatmap" },
  { id: "barplot",   label: "Barplot" },
];
const MULTI_TABS = [
  { id: "heatmap",    label: "Heatmap" },
  { id: "radarplot",  label: "Radarplot" },
  { id: "corrnet",    label: "Corr. Network" },
  { id: "stackedbar", label: "Stacked Bar" },
  { id: "streamgraph",label: "Streamgraph" },
];

function buildSubtabs(mode) {
  const bar  = document.getElementById("subtabs-bar");
  const tabs = mode === "single" ? SINGLE_TABS : MULTI_TABS;
  bar.innerHTML = "";
  tabs.forEach(t => {
    const btn = document.createElement("button");
    btn.className = "subtab-btn";
    btn.id = `subtab-btn-${t.id}`;
    btn.textContent = t.label;
    btn.onclick = () => activateSubtab(t.id);
    bar.appendChild(btn);
  });
}

function activateSubtab(id) {
  activeSubtab = id;
  // Toggle panels
  document.querySelectorAll(".subtab-panel").forEach(p => p.classList.remove("active"));
  const panel = document.getElementById(`stab-${id}`);
  if (panel) panel.classList.add("active");
  // Toggle buttons
  document.querySelectorAll(".subtab-btn").forEach(b => b.classList.remove("active"));
  const btn = document.getElementById(`subtab-btn-${id}`);
  if (btn) btn.classList.add("active");
  // Update right panel
  updateRightPanel(id);
}

// ==========================================================================
// Right panel — load params for active tab
// ==========================================================================
function updateRightPanel(tabId) {
  const container = document.getElementById("right-content");
  const tplId = `tpl-${tabId}-params`;
  const tpl = document.getElementById(tplId);

  if (!tpl) {
    container.innerHTML = '<p style="font-size:12px;color:var(--text-3);">No parameters for this plot.</p>';
    return;
  }

  container.innerHTML = "";
  container.appendChild(tpl.content.cloneNode(true));

  // Post-clone setup
  if (tabId === "heatmap" && currentMode === "multi") {
    buildSampleListInRight();
  }
  if (tabId === "radarplot") {
    buildPathwayList(currentPathways);
    buildRadarColorInputs();
  }
  if (tabId === "stackedbar") {
    document.getElementById("tpl-sbar-inner").innerHTML = multiBarParamsHTML("sbar");
  }
  if (tabId === "streamgraph") {
    document.getElementById("tpl-sg-inner").innerHTML = multiBarParamsHTML("sg", true);
  }
}

// ==========================================================================
// Sample list (drag-and-drop)
// ==========================================================================
async function loadSamples(jobId) {
  const r = await fetch(`/samples/${jobId}`);
  const d = await r.json();
  currentSamples = d.samples || [];
}

function buildSampleListInRight() {
  const ul = document.getElementById("sample-list");
  if (!ul) return;
  ul.innerHTML = "";
  currentSamples.forEach(name => {
    const li = document.createElement("li");
    li.dataset.sample = name; li.draggable = true;
    li.innerHTML = `<span class="drag-handle">⇅</span>${name}`;
    ul.appendChild(li);
  });
  initDragSort(ul);
}

function getSampleOrder() {
  return Array.from(document.querySelectorAll("#sample-list li")).map(li => li.dataset.sample);
}

function initDragSort(ul) {
  let dragged = null;
  ul.addEventListener("dragstart", e => {
    dragged = e.target.closest("li");
    setTimeout(() => dragged?.classList.add("dragging"), 0);
  });
  ul.addEventListener("dragend", () => { dragged?.classList.remove("dragging"); dragged = null; });
  ul.addEventListener("dragover", e => {
    e.preventDefault();
    const target = e.target.closest("li");
    if (!target || target === dragged) return;
    const after = e.clientY > target.getBoundingClientRect().top + target.getBoundingClientRect().height / 2;
    ul.insertBefore(dragged, after ? target.nextSibling : target);
  });
}

// ==========================================================================
// Pathway checkboxes (radarplot)
// ==========================================================================
async function loadPathways(jobId) {
  const r = await fetch(`/pathways/${jobId}`);
  const d = await r.json();
  currentPathways = d.pathways || [];
}

function buildPathwayList(pathways) {
  const container = document.getElementById("pathway-list");
  if (!container) return;
  container.innerHTML = "";
  pathways.forEach(pw => {
    const lbl = document.createElement("label");
    const cb  = document.createElement("input");
    cb.type = "checkbox"; cb.value = pw;
    cb.addEventListener("change", updatePathwayCount);
    lbl.appendChild(cb);
    lbl.appendChild(document.createTextNode(" " + pw));
    container.appendChild(lbl);
  });
  updatePathwayCount();
}

function filterPathways() {
  const q = document.getElementById("pathway-search")?.value.toLowerCase() || "";
  document.querySelectorAll("#pathway-list label").forEach(lbl => {
    lbl.style.display = lbl.textContent.toLowerCase().includes(q) ? "" : "none";
  });
}

function updatePathwayCount() {
  const sel = document.querySelectorAll("#pathway-list input:checked").length;
  const cnt = document.getElementById("pathway-count");
  if (cnt) { cnt.textContent = `${sel} selected (max 4)`; cnt.style.color = sel > 4 ? "var(--red)" : "var(--text-3)"; }
  document.querySelectorAll("#pathway-list input").forEach(cb => { if (!cb.checked) cb.disabled = sel >= 4; });
}

function getSelectedPathways() {
  return Array.from(document.querySelectorAll("#pathway-list input:checked")).map(cb => cb.value);
}

// ==========================================================================
// Radar color inputs
// ==========================================================================
function buildRadarColorInputs() {
  const container = document.getElementById("radar-color-inputs");
  if (!container) return;
  container.innerHTML = "";
  currentSamples.forEach(name => {
    const row = document.createElement("div");
    row.className = "radar-color-row";
    row.innerHTML = `<input type="color" id="rp-color-${CSS.escape(name)}" value="#000000"><span>${name}</span>`;
    container.appendChild(row);
  });
}

function getRadarColors() {
  return currentSamples.map(name => document.getElementById(`rp-color-${CSS.escape(name)}`)?.value || "#000000");
}

// ==========================================================================
// Multi bar params template builder (stacked bar & streamgraph)
// ==========================================================================
function multiBarParamsHTML(p, isStream = false) {
  return `
  <details class="right-spoiler" open>
    <summary>Main</summary>
    <div class="right-spoiler-body">
      <div class="params-grid-2">
        <div class="param-cell"><label>Colormap</label><input type="text" id="${p}-cmap" value="tab20"></div>
        <div class="param-cell"><label>Bar width</label><input type="number" id="${p}-bw" value="0.6" min="0.1" max="1" step="0.05"></div>
        ${isStream ? `
        <div class="param-cell"><label>Fill alpha</label><input type="number" id="${p}-fill-alpha" value="1.0" min="0" max="1" step="0.05"></div>
        <div class="param-cell"><label>Edge color</label><input type="text" id="${p}-ec" placeholder="none"></div>
        ` : `
        <div class="param-cell"><label>Edge color</label><input type="text" id="${p}-ec" value="black"></div>
        <div class="param-cell"><label>Edge width</label><input type="number" id="${p}-elw" value="0.3" step="0.1"></div>
        `}
        <div class="param-cell"><label>Title</label><input type="text" id="${p}-title" placeholder="optional"></div>
        <div class="param-cell"><label>Background</label><input type="text" id="${p}-bg" value="white"></div>
        <div class="param-cell"><label>Fig width</label><input type="number" id="${p}-fw" value="14"></div>
        <div class="param-cell"><label>Fig height</label><input type="number" id="${p}-fh" value="7"></div>
        <div class="param-cell"><label>DPI</label><input type="number" id="${p}-dpi" value="300" min="72" max="600"></div>
        <div class="param-cell" style="justify-content:flex-end;padding-top:18px;">
          <div class="check-row"><input type="checkbox" id="${p}-grid" checked><label for="${p}-grid">Grid</label></div>
        </div>
        <div class="param-cell"><label>Grid style</label><select id="${p}-grid-ls"><option value="--" selected>Dashed</option><option value="-">Solid</option><option value="-.">Dash-dot</option><option value=":">Dotted</option></select></div>
        <div class="param-cell"><label>Grid alpha</label><input type="number" id="${p}-grid-alpha" value="0.7" min="0" max="1" step="0.05"></div>
        <div class="param-cell" style="justify-content:flex-end;padding-top:8px;">
          <div class="check-row"><input type="checkbox" id="${p}-legend" checked><label for="${p}-legend">Show legend</label></div>
        </div>
        <div class="param-cell"><label>Legend loc</label><select id="${p}-legend-loc"><option value="upper left" selected>Upper left</option><option value="upper right">Upper right</option><option value="lower left">Lower left</option><option value="lower right">Lower right</option></select></div>
      </div>
    </div>
  </details>
  <details class="right-spoiler">
    <summary>Axis labels</summary>
    <div class="right-spoiler-body">
      <div class="params-grid-2">
        <div class="param-cell"><label>X label</label><input type="text" id="${p}-xlabel" value="Samples"></div>
        <div class="param-cell"><label>Y label</label><input type="text" id="${p}-ylabel" value="Total Completeness"></div>
        <div class="param-cell"><label>X label size</label><input type="number" id="${p}-xlfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>Y label size</label><input type="number" id="${p}-ylfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>X label color</label><input type="text" id="${p}-xlc" value="black"></div>
        <div class="param-cell"><label>Y label color</label><input type="text" id="${p}-ylc" value="black"></div>
        <div class="param-cell"><label>X label weight</label><select id="${p}-xlw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
        <div class="param-cell"><label>Y label weight</label><select id="${p}-ylw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
        <div class="param-cell"><label>X rotation</label><input type="number" id="${p}-xrot" value="0" step="5"></div>
        <div class="param-cell"><label>X alignment</label><select id="${p}-xha"><option value="center" selected>Center</option><option value="right">Right</option><option value="left">Left</option></select></div>
      </div>
    </div>
  </details>
  <details class="right-spoiler">
    <summary>Typography</summary>
    <div class="right-spoiler-body">
      <div class="params-grid-2">
        <div class="param-cell"><label>Title size</label><input type="number" id="${p}-tfs" value="16" step="0.5"></div>
        <div class="param-cell"><label>Title color</label><input type="text" id="${p}-tc" value="black"></div>
        <div class="param-cell"><label>Title weight</label><select id="${p}-tw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
        <div class="param-cell"><label>Title style</label><select id="${p}-ts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
        <div class="param-cell"><label>X tick size</label><input type="number" id="${p}-xtfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>Y tick size</label><input type="number" id="${p}-ytfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>X tick color</label><input type="text" id="${p}-xtc" value="black"></div>
        <div class="param-cell"><label>Y tick color</label><input type="text" id="${p}-ytc" value="black"></div>
        <div class="param-cell"><label>X tick weight</label><select id="${p}-xtw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
        <div class="param-cell"><label>Y tick weight</label><select id="${p}-ytw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
        <div class="param-cell"><label>Legend size</label><input type="number" id="${p}-lgfs" value="9" step="0.5"></div>
      </div>
    </div>
  </details>`;
}

// ==========================================================================
// Run visualization
// ==========================================================================
const v   = id => document.getElementById(id);
const val = id => v(id)?.value ?? "";
const chk = id => v(id)?.checked ?? false;
const num = (id, def) => parseFloat(v(id)?.value) || def;
const int_ = (id, def) => parseInt(v(id)?.value) || def;

async function runViz(plotType) {
  if (!currentJobId) return;

  const btn  = v(`btn-viz-${plotType}`) || v(`btn-rerender-heatmap`);
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
    form.append("dpi",           int_("cn-dpi", 300));
    form.append("figwidth",      int_("cn-fw", 12));
    form.append("figheight",     int_("cn-fh", 6));
    form.append("threshold",     num("cn-threshold", 0.5));
    form.append("node_size",     num("cn-node-size", 700));
    form.append("node_color",    val("cn-node-color"));
    form.append("node_edgecolors", val("cn-node-ec"));
    form.append("node_linewidths", num("cn-node-lw", 1.5));
    form.append("label_fontsize",num("cn-lfs", 8));
    form.append("label_color",   val("cn-lc"));
    form.append("label_weight",  val("cn-lw"));
    form.append("edge_cmap",     val("cn-edge-cmap"));
    form.append("cbar_size",     num("cn-cbar", 0.5));
    form.append("title",         val("cn-title"));
    form.append("title_fontsize",num("cn-tfs", 16));
    form.append("title_color",   val("cn-tc"));
    form.append("title_weight",  val("cn-tw"));
    form.append("title_style",   val("cn-ts"));
    form.append("background_color", val("cn-bg"));
    form.append("sample_order",  JSON.stringify(sampleOrder));

  } else if (plotType === "radarplot") {
    const pws = getSelectedPathways();
    if (pws.length < 1 || pws.length > 4) {
      if (stat) { stat.className = "viz-status error"; stat.textContent = "Select 1–4 pathways."; }
      if (btn) btn.disabled = false; return;
    }
    const colors = getRadarColors();
    form.append("dpi",             int_("rp-dpi", 300));
    form.append("figwidth",        int_("rp-fw", 8));
    form.append("figheight",       int_("rp-fh", 8));
    form.append("pathways_selected", JSON.stringify(pws));
    form.append("colors_selected",   colors.every(c => c === "#000000") ? "[]" : JSON.stringify(colors));
    form.append("sample_order",    JSON.stringify(sampleOrder));
    form.append("fill_alpha",      num("rp-fill-alpha", 0.25));
    form.append("line_width",      num("rp-lw", 2.0));
    form.append("line_style",      val("rp-ls"));
    form.append("label_background",val("rp-lbg"));
    form.append("label_pad",       num("rp-lpad", 1.05));
    form.append("show_legend",     chk("rp-legend"));
    form.append("legend_loc",      val("rp-legend-loc"));
    form.append("title",           val("rp-title"));
    form.append("title_fontsize",  num("rp-tfs", 14));
    form.append("title_color",     val("rp-tc"));
    form.append("title_weight",    val("rp-tw"));
    form.append("title_style",     val("rp-ts"));
    form.append("background_color",val("rp-bg"));
    form.append("label_fontsize",  num("rp-lfs", 10));
    form.append("label_color",     val("rp-lc"));
    form.append("label_weight",    val("rp-lw-font"));
    form.append("yticks_fontsize", num("rp-ytfs", 8));
    form.append("yticks_color",    val("rp-ytc"));
    form.append("yticks_weight",   val("rp-ytw"));

  } else {
    // stackedbar / streamgraph
    const p = plotType === "stackedbar" ? "sbar" : "sg";
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
    if (dl)   { dl.href = url; dl.setAttribute("download", `kegganog_${plotType}_${currentJobId.slice(0,8)}.png`); dl.classList.remove("hidden"); }
  } catch (e) {
    if (stat) { stat.className = "viz-status error"; stat.textContent = "Request failed: " + e.message; }
  }
  if (btn) btn.disabled = false;
}

// ==========================================================================
// Status helpers
// ==========================================================================
function showStatus(type, msg) {
  const bar = document.getElementById("status-bar");
  const txt = document.getElementById("status-text");
  const spn = document.getElementById("status-spinner");
  bar.className = `status-bar ${type}`;
  txt.textContent = msg;
  spn.style.display = type === "running" ? "block" : "none";
}
function hideStatus() { document.getElementById("status-bar").className = "status-bar"; }

// Init
switchMode("single");
