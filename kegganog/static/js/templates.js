// ==========================================================================
// Parameter templates — injected into <body> on load,
// cloned into the right panel when a sub-tab is activated.
// ==========================================================================

(function registerTemplates() {
  const defs = {

    // ------------------------------------------------------------------
    // Heatmap: sample order drag list + color/DPI/group settings
    // ------------------------------------------------------------------
    "tpl-heatmap-params": `
      <div id="rp-heatmap">
        <details class="right-spoiler" open>
          <summary>Sample order <span style="font-weight:400;font-size:10px;color:var(--text-3);margin-left:4px;">drag to reorder</span></summary>
          <div class="right-spoiler-body">
            <ul class="sample-list" id="sample-list"></ul>
          </div>
        </details>
        <details class="right-spoiler" open>
          <summary>Heatmap settings</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell">
                <label>Color scheme</label>
                <select id="hm-color">
                  <option value="Blues" selected>Blues</option>
                  <option value="Greens">Greens</option>
                  <option value="Reds">Reds</option>
                  <option value="Purples">Purples</option>
                  <option value="Greys">Greys</option>
                  <option value="Oranges">Oranges</option>
                </select>
              </div>
              <div class="param-cell">
                <label>DPI</label>
                <input type="number" id="hm-dpi" value="300" min="72" max="600">
              </div>
              <div class="param-cell full">
                <div class="check-row">
                  <input type="checkbox" id="hm-group">
                  <label for="hm-group">Group by functional category</label>
                </div>
              </div>
            </div>
          </div>
        </details>
      </div>`,

    // ------------------------------------------------------------------
    // Barplot
    // ------------------------------------------------------------------
    "tpl-barplot-params": `
      <div>
        <details class="right-spoiler" open>
          <summary>Main</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Colormap</label><input type="text" id="bp-cmap" value="Greens" placeholder="Greens, viridis…"></div>
              <div class="param-cell"><label>Sort order</label><select id="bp-sort"><option value="descending" selected>Descending</option><option value="ascending">Ascending</option></select></div>
              <div class="param-cell"><label>Cmap range min</label><input type="number" id="bp-cmap-min" value="8"></div>
              <div class="param-cell"><label>Cmap range max</label><input type="number" id="bp-cmap-max" value="30"></div>
              <div class="param-cell"><label>Title</label><input type="text" id="bp-title" placeholder="optional"></div>
              <div class="param-cell"><label>Background</label><input type="text" id="bp-bg" value="white"></div>
              <div class="param-cell"><label>Fig width</label><input type="number" id="bp-fw" value="8"></div>
              <div class="param-cell"><label>Fig height</label><input type="number" id="bp-fh" value="12"></div>
              <div class="param-cell"><label>DPI</label><input type="number" id="bp-dpi" value="300" min="72" max="600"></div>
              <div class="param-cell" style="justify-content:flex-end;padding-top:18px;">
                <div class="check-row"><input type="checkbox" id="bp-grid" checked><label for="bp-grid">Grid</label></div>
              </div>
              <div class="param-cell"><label>Grid style</label><select id="bp-grid-ls"><option value="--" selected>Dashed</option><option value="-">Solid</option><option value="-.">Dash-dot</option><option value=":">Dotted</option></select></div>
              <div class="param-cell"><label>Grid alpha</label><input type="number" id="bp-grid-alpha" value="0.7" min="0" max="1" step="0.05"></div>
            </div>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Axis labels</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>X label</label><input type="text" id="bp-xlabel" value="Pathway completeness"></div>
              <div class="param-cell"><label>Y label</label><input type="text" id="bp-ylabel" value="Pathway"></div>
              <div class="param-cell"><label>X label size</label><input type="number" id="bp-xlfs" value="14" step="0.5"></div>
              <div class="param-cell"><label>Y label size</label><input type="number" id="bp-ylfs" value="14" step="0.5"></div>
              <div class="param-cell"><label>X label color</label><input type="text" id="bp-xlc" value="black"></div>
              <div class="param-cell"><label>Y label color</label><input type="text" id="bp-ylc" value="black"></div>
              <div class="param-cell"><label>X label weight</label><select id="bp-xlw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Y label weight</label><select id="bp-ylw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>X label style</label><select id="bp-xls"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
              <div class="param-cell"><label>Y label style</label><select id="bp-yls"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
            </div>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Typography</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Title size</label><input type="number" id="bp-tfs" value="16" step="0.5"></div>
              <div class="param-cell"><label>Title color</label><input type="text" id="bp-tc" value="black"></div>
              <div class="param-cell"><label>Title weight</label><select id="bp-tw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Title style</label><select id="bp-ts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
              <div class="param-cell"><label>X tick size</label><input type="number" id="bp-xtfs" value="12" step="0.5"></div>
              <div class="param-cell"><label>Y tick size</label><input type="number" id="bp-ytfs" value="12" step="0.5"></div>
              <div class="param-cell"><label>X tick color</label><input type="text" id="bp-xtc" value="black"></div>
              <div class="param-cell"><label>Y tick color</label><input type="text" id="bp-ytc" value="black"></div>
              <div class="param-cell"><label>X tick weight</label><select id="bp-xtw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Y tick weight</label><select id="bp-ytw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>X tick style</label><select id="bp-xts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
              <div class="param-cell"><label>Y tick style</label><select id="bp-yts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
            </div>
          </div>
        </details>
      </div>`,

    // ------------------------------------------------------------------
    // Radarplot
    // ------------------------------------------------------------------
    "tpl-radarplot-params": `
      <div>
        <details class="right-spoiler" open>
          <summary>Sample order <span style="font-weight:400;font-size:10px;color:var(--text-3);margin-left:4px;">drag to reorder</span></summary>
          <div class="right-spoiler-body">
            <ul class="sample-list" id="sample-list"></ul>
          </div>
        </details>
        <details class="right-spoiler" open>
          <summary>Pathway selection (1–4)</summary>
          <div class="right-spoiler-body">
            <input class="pathway-search" type="text" id="pathway-search" placeholder="Search pathways…" oninput="filterPathways()">
            <div class="pathway-list" id="pathway-list"></div>
            <div class="pathway-count" id="pathway-count">0 selected</div>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Pathway colors</summary>
          <div class="right-spoiler-body">
            <div class="radar-colors" id="radar-color-inputs"></div>
            <p style="font-size:11px;color:var(--text-3);margin-top:4px;">Colors map to pathways in selection order. All black = matplotlib defaults.</p>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Main</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Title</label><input type="text" id="rp-title" placeholder="optional"></div>
              <div class="param-cell"><label>Background</label><input type="text" id="rp-bg" value="white"></div>
              <div class="param-cell"><label>Fig width</label><input type="number" id="rp-fw" value="8"></div>
              <div class="param-cell"><label>Fig height</label><input type="number" id="rp-fh" value="8"></div>
              <div class="param-cell"><label>DPI</label><input type="number" id="rp-dpi" value="300" min="72" max="600"></div>
              <div class="param-cell"><label>Fill alpha</label><input type="number" id="rp-fill-alpha" value="0.25" min="0" max="1" step="0.05"></div>
              <div class="param-cell"><label>Line width</label><input type="number" id="rp-lw" value="2.0" step="0.5"></div>
              <div class="param-cell"><label>Line style</label><select id="rp-ls"><option value="solid" selected>Solid</option><option value="dashed">Dashed</option><option value="dotted">Dotted</option><option value="dashdot">Dashdot</option></select></div>
              <div class="param-cell"><label>Label pad</label><input type="number" id="rp-lpad" value="1.05" step="0.05"></div>
              <div class="param-cell"><label>Label bg</label><input type="text" id="rp-lbg" placeholder="none"></div>
              <div class="param-cell full"><div class="check-row"><input type="checkbox" id="rp-legend" checked><label for="rp-legend">Show legend</label></div></div>
              <div class="param-cell"><label>Legend loc</label><select id="rp-legend-loc"><option value="upper right" selected>Upper right</option><option value="upper left">Upper left</option><option value="lower right">Lower right</option><option value="lower left">Lower left</option></select></div>
              <div class="param-cell"><label>Legend X (bbox)</label><input type="number" id="rp-legend-bx" value="1.3" step="0.05"></div>
              <div class="param-cell"><label>Legend Y (bbox)</label><input type="number" id="rp-legend-by" value="1.1" step="0.05"></div>
            </div>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Typography</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Title size</label><input type="number" id="rp-tfs" value="14" step="0.5"></div>
              <div class="param-cell"><label>Title color</label><input type="text" id="rp-tc" value="black"></div>
              <div class="param-cell"><label>Title weight</label><select id="rp-tw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Title style</label><select id="rp-ts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
              <div class="param-cell"><label>Label size</label><input type="number" id="rp-lfs" value="10" step="0.5"></div>
              <div class="param-cell"><label>Label color</label><input type="text" id="rp-lc" value="black"></div>
              <div class="param-cell"><label>Label weight</label><select id="rp-lw-font"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Y-tick size</label><input type="number" id="rp-ytfs" value="8" step="0.5"></div>
              <div class="param-cell"><label>Y-tick color</label><input type="text" id="rp-ytc" value="black"></div>
              <div class="param-cell"><label>Y-tick weight</label><select id="rp-ytw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
            </div>
          </div>
        </details>
      </div>`,

    // ------------------------------------------------------------------
    // Correlation network
    // ------------------------------------------------------------------
    "tpl-corrnet-params": `
      <div>
        <details class="right-spoiler" open>
          <summary>Main</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Threshold</label><input type="number" id="cn-threshold" value="0.5" min="0" max="1" step="0.05"></div>
              <div class="param-cell"><label>Node size</label><input type="number" id="cn-node-size" value="700" step="50"></div>
              <div class="param-cell"><label>Node color</label><input type="text" id="cn-node-color" value="#A3D5FF"></div>
              <div class="param-cell"><label>Node edge color</label><input type="text" id="cn-node-ec" value="#03045E"></div>
              <div class="param-cell"><label>Node edge width</label><input type="number" id="cn-node-lw" value="1.5" step="0.5"></div>
              <div class="param-cell"><label>Edge colormap</label><input type="text" id="cn-edge-cmap" value="coolwarm"></div>
              <div class="param-cell"><label>Colorbar size</label><input type="number" id="cn-cbar" value="0.5" step="0.05"></div>
              <div class="param-cell"><label>Title</label><input type="text" id="cn-title" placeholder="optional"></div>
              <div class="param-cell"><label>Background</label><input type="text" id="cn-bg" value="white"></div>
              <div class="param-cell"><label>Fig width</label><input type="number" id="cn-fw" value="12"></div>
              <div class="param-cell"><label>Fig height</label><input type="number" id="cn-fh" value="6"></div>
              <div class="param-cell"><label>DPI</label><input type="number" id="cn-dpi" value="300" min="72" max="600"></div>
            </div>
          </div>
        </details>
        <details class="right-spoiler">
          <summary>Typography</summary>
          <div class="right-spoiler-body">
            <div class="params-grid-2">
              <div class="param-cell"><label>Title size</label><input type="number" id="cn-tfs" value="16" step="0.5"></div>
              <div class="param-cell"><label>Title color</label><input type="text" id="cn-tc" value="black"></div>
              <div class="param-cell"><label>Title weight</label><select id="cn-tw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
              <div class="param-cell"><label>Title style</label><select id="cn-ts"><option value="normal" selected>Normal</option><option value="italic">Italic</option></select></div>
              <div class="param-cell"><label>Label size</label><input type="number" id="cn-lfs" value="8" step="0.5"></div>
              <div class="param-cell"><label>Label color</label><input type="text" id="cn-lc" value="#03045E"></div>
              <div class="param-cell"><label>Label weight</label><select id="cn-lw"><option value="normal" selected>Normal</option><option value="bold">Bold</option></select></div>
            </div>
          </div>
        </details>
      </div>`,

    // ------------------------------------------------------------------
    // Stacked barplot / Streamgraph — inner HTML filled by right-panel.js
    // ------------------------------------------------------------------
    "tpl-stackedbar-params":  `<div id="tpl-sbar-inner"></div>`,
    "tpl-streamgraph-params": `<div id="tpl-sg-inner"></div>`,
  };

  Object.entries(defs).forEach(([id, html]) => {
    const tpl = document.createElement("template");
    tpl.id = id;
    tpl.innerHTML = html;
    document.body.appendChild(tpl);
  });
})();
