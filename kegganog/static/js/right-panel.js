// ==========================================================================
// Right panel — sample order, pathway selection, radar colors, param HTML
// ==========================================================================

// ---- Sample list (drag-and-drop) ----
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

// ---- Pathway checkboxes (radarplot) ----
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
  if (cnt) {
    cnt.textContent = `${sel} selected (max 4)`;
    cnt.style.color = sel > 4 ? "var(--red)" : "var(--text-3)";
  }
  document.querySelectorAll("#pathway-list input").forEach(cb => {
    if (!cb.checked) cb.disabled = sel >= 4;
  });
}

function getSelectedPathways() {
  return Array.from(document.querySelectorAll("#pathway-list input:checked")).map(cb => cb.value);
}

// ---- Radar color pickers (per pathway, 4 fixed slots) ----
function buildRadarColorInputs() {
  const container = document.getElementById("radar-color-inputs");
  if (!container) return;
  container.innerHTML = "";
  for (let i = 0; i < 4; i++) {
    const row = document.createElement("div");
    row.className = "radar-color-row";
    row.innerHTML = `<input type="color" id="rp-color-${i}" value="#000000"><span>Pathway ${i + 1}</span>`;
    container.appendChild(row);
  }
}

function getRadarColors() {
  return [0, 1, 2, 3].map(i => document.getElementById(`rp-color-${i}`)?.value || "#000000");
}

// ---- Stacked bar / streamgraph parameter HTML builder ----
function multiBarParamsHTML(p, isStream = false) {
  return `
  <details class="right-spoiler" open>
    <summary>Sample order <span style="font-weight:400;font-size:10px;color:var(--text-3);margin-left:4px;">drag to reorder</span></summary>
    <div class="right-spoiler-body">
      <ul class="sample-list" id="sample-list"></ul>
    </div>
  </details>
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
        <div class="param-cell"><label>Grid style</label><select id="${p}-grid-ls">
          <option value="--" selected>Dashed</option><option value="-">Solid</option>
          <option value="-.">Dash-dot</option><option value=":">Dotted</option>
        </select></div>
        <div class="param-cell"><label>Grid alpha</label><input type="number" id="${p}-grid-alpha" value="0.7" min="0" max="1" step="0.05"></div>
        <div class="param-cell" style="justify-content:flex-end;padding-top:8px;">
          <div class="check-row"><input type="checkbox" id="${p}-legend" checked><label for="${p}-legend">Show legend</label></div>
        </div>
        <div class="param-cell"><label>Legend loc</label><select id="${p}-legend-loc">
          <option value="upper left" selected>Upper left</option><option value="upper right">Upper right</option>
          <option value="lower left">Lower left</option><option value="lower right">Lower right</option>
        </select></div>
        <div class="param-cell"><label>Legend X (bbox)</label><input type="number" id="${p}-legend-bx" value="1.05" step="0.05"></div>
        <div class="param-cell"><label>Legend Y (bbox)</label><input type="number" id="${p}-legend-by" value="1.0" step="0.05"></div>
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
        <div class="param-cell"><label>X label weight</label><select id="${p}-xlw">
          <option value="normal" selected>Normal</option><option value="bold">Bold</option>
        </select></div>
        <div class="param-cell"><label>Y label weight</label><select id="${p}-ylw">
          <option value="normal" selected>Normal</option><option value="bold">Bold</option>
        </select></div>
        <div class="param-cell"><label>X rotation</label><input type="number" id="${p}-xrot" value="0" step="5"></div>
        <div class="param-cell"><label>X alignment</label><select id="${p}-xha">
          <option value="center" selected>Center</option><option value="right">Right</option><option value="left">Left</option>
        </select></div>
      </div>
    </div>
  </details>
  <details class="right-spoiler">
    <summary>Typography</summary>
    <div class="right-spoiler-body">
      <div class="params-grid-2">
        <div class="param-cell"><label>Title size</label><input type="number" id="${p}-tfs" value="16" step="0.5"></div>
        <div class="param-cell"><label>Title color</label><input type="text" id="${p}-tc" value="black"></div>
        <div class="param-cell"><label>Title weight</label><select id="${p}-tw">
          <option value="normal" selected>Normal</option><option value="bold">Bold</option>
        </select></div>
        <div class="param-cell"><label>Title style</label><select id="${p}-ts">
          <option value="normal" selected>Normal</option><option value="italic">Italic</option>
        </select></div>
        <div class="param-cell"><label>X tick size</label><input type="number" id="${p}-xtfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>Y tick size</label><input type="number" id="${p}-ytfs" value="12" step="0.5"></div>
        <div class="param-cell"><label>X tick color</label><input type="text" id="${p}-xtc" value="black"></div>
        <div class="param-cell"><label>Y tick color</label><input type="text" id="${p}-ytc" value="black"></div>
        <div class="param-cell"><label>X tick weight</label><select id="${p}-xtw">
          <option value="normal" selected>Normal</option><option value="bold">Bold</option>
        </select></div>
        <div class="param-cell"><label>Y tick weight</label><select id="${p}-ytw">
          <option value="normal" selected>Normal</option><option value="bold">Bold</option>
        </select></div>
        <div class="param-cell"><label>Legend size</label><input type="number" id="${p}-lgfs" value="9" step="0.5"></div>
      </div>
    </div>
  </details>`;
}
