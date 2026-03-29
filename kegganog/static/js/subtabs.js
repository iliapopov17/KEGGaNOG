// ==========================================================================
// Sub-tabs — build, activate, inject right-panel parameters
// ==========================================================================

const SINGLE_TABS = [
  { id: "heatmap", label: "Heatmap" },
  { id: "barplot", label: "Barplot" },
];
const MULTI_TABS = [
  { id: "heatmap",     label: "Heatmap" },
  { id: "radarplot",   label: "Radarplot" },
  { id: "corrnet",     label: "Corr. Network" },
  { id: "stackedbar",  label: "Stacked Bar" },
  { id: "streamgraph", label: "Streamgraph" },
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
  document.querySelectorAll(".subtab-panel").forEach(p => p.classList.remove("active"));
  const panel = document.getElementById(`stab-${id}`);
  if (panel) panel.classList.add("active");
  document.querySelectorAll(".subtab-btn").forEach(b => b.classList.remove("active"));
  const btn = document.getElementById(`subtab-btn-${id}`);
  if (btn) btn.classList.add("active");
  updateRightPanel(id);
}

function updateRightPanel(tabId) {
  const container = document.getElementById("right-content");
  const tpl = document.getElementById(`tpl-${tabId}-params`);

  if (!tpl) {
    container.innerHTML = '<p style="font-size:12px;color:var(--text-3);">No parameters for this plot.</p>';
    return;
  }

  if (tabId === "heatmap" && currentMode === "single") {
    container.innerHTML = `
      <div style="font-size:12px;color:var(--text-3);line-height:1.7;">
        <p>The single-sample heatmap is generated directly by the analysis pipeline.</p>
        <p style="margin-top:8px;">To change color scheme, DPI, or grouping — adjust the settings in the <strong>left panel</strong> and click <strong>Run analysis</strong> again. It takes only a few seconds.</p>
        <p style="margin-top:8px;">For richer customization, use the <strong>Barplot</strong> tab.</p>
      </div>`;
    return;
  }

  container.innerHTML = "";
  container.appendChild(tpl.content.cloneNode(true));

  if (tabId === "heatmap" && currentMode === "multi") buildSampleListInRight();
  if (tabId === "radarplot") { buildPathwayList(currentPathways); buildRadarColorInputs(); buildSampleListInRight(); }
  if (tabId === "stackedbar")  { document.getElementById("tpl-sbar-inner").innerHTML = multiBarParamsHTML("sbar");  buildSampleListInRight(); }
  if (tabId === "streamgraph") { document.getElementById("tpl-sg-inner").innerHTML  = multiBarParamsHTML("sg", true); buildSampleListInRight(); }
}
