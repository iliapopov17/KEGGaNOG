// ==========================================================================
// Analysis — submit job, poll status, show/hide results
// ==========================================================================

async function submitJob() {
  const mode = currentMode || "single";
  if (mode === "single" && !selectedFileSingle) {
    alert("Please select an annotation file."); return;
  }
  if (mode === "multi" && (!selectedFilesMulti || !selectedFilesMulti.length)) {
    alert("Please select annotation files."); return;
  }

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
    if (!r.ok) {
      showStatus("error", d.detail ? d.detail.join("; ") : "Submission failed.");
      btn.disabled = false; return;
    }
    jobId = d.job_id;
  } catch {
    showStatus("error", "Could not reach the server.");
    btn.disabled = false; return;
  }

  pollStatus(jobId, btn, mode);
}

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
    } catch {
      clearInterval(iv); btn.disabled = false;
      showStatus("error", "Lost connection.");
    }
  }, 2000);
}

async function showResults(jobId, mode) {
  currentJobId = jobId; currentMode = mode;
  const ts = Date.now();

  if (mode === "single") {
    document.getElementById("heatmap-single-result").classList.remove("hidden");
    document.getElementById("heatmap-multi-result").classList.add("hidden");
    document.getElementById("result-img-single").src = `/preview/${jobId}?t=${ts}`;
  } else {
    document.getElementById("heatmap-single-result").classList.add("hidden");
    document.getElementById("heatmap-multi-result").classList.remove("hidden");
    document.getElementById("heatmap-spoiler").removeAttribute("open");
    document.getElementById("result-img-multi").src = `/preview/${jobId}?t=${ts}`;
  }
  if (mode === "single") {
    document.getElementById("heatmap-rerender").classList.add("hidden");
  } else {
    document.getElementById("heatmap-rerender").classList.remove("hidden");
  }

  const dlZip = document.getElementById("dl-heatmap-zip");
  dlZip.href = `/download/${jobId}?t=${ts}`;
  dlZip.setAttribute("download", `kegganog_${jobId.slice(0, 8)}.zip`);

  buildSubtabs(mode);

  if (mode === "multi") {
    await loadSamples(jobId);
    await loadPathways(jobId);
  }

  document.getElementById("center-placeholder").classList.add("hidden");
  document.getElementById("center-results").classList.remove("hidden");
  activateSubtab("heatmap");
}

function hideResults() {
  currentJobId = null;
  document.getElementById("center-placeholder").classList.remove("hidden");
  document.getElementById("center-results").classList.add("hidden");
  document.getElementById("right-content").innerHTML =
    '<p style="font-size:12px;color:var(--text-3);">Run an analysis to see plot parameters here.</p>';
}
