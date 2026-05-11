// ==========================================================================
// Global application state
// ==========================================================================
let currentJobId    = null;
let currentMode     = null;   // "single" | "multi"
let currentSamples  = [];
let currentPathways = [];
let activeSubtab    = "heatmap";

/** Normalize FastAPI / Starlette JSON error payloads for display. */
function formatFastApiDetail(payload) {
  if (!payload || payload.detail === undefined || payload.detail === null) {
    return "Request failed.";
  }
  const x = payload.detail;
  if (typeof x === "string") return x;
  if (Array.isArray(x)) {
    return x
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item.msg === "string") return item.msg;
        try {
          return JSON.stringify(item);
        } catch {
          return String(item);
        }
      })
      .join("; ");
  }
  return String(x);
}
