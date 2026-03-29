// ==========================================================================
// File / folder upload — drop zones and file input handlers
// ==========================================================================

const ANNOTATION_EXTS = [".annotations", ".tsv", ".txt"];
const isAnnot = name => ANNOTATION_EXTS.some(ext => name.endsWith(ext));

// ---- Single sample ----
const dropZoneSingle  = document.getElementById("drop-zone-single");
const fileInputSingle = document.getElementById("file-input-single");
let selectedFileSingle = null;

dropZoneSingle.addEventListener("click", () => fileInputSingle.click());
dropZoneSingle.addEventListener("dragover", e => {
  e.preventDefault(); dropZoneSingle.classList.add("over");
});
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

// ---- Multi sample (folder) ----
const dropZoneMulti  = document.getElementById("drop-zone-multi");
const fileInputMulti = document.getElementById("file-input-multi");
let selectedFilesMulti = null;

async function readDir(dir, files) {
  const reader = dir.createReader();
  let batch;
  do {
    batch = await new Promise((res, rej) => reader.readEntries(res, rej));
    for (const entry of batch) {
      if (entry.isDirectory) await readDir(entry, files);
      else if (entry.isFile && isAnnot(entry.name))
        files.push(await new Promise((res, rej) => entry.file(res, rej)));
    }
  } while (batch.length > 0);
}

dropZoneMulti.addEventListener("click", () => fileInputMulti.click());
dropZoneMulti.addEventListener("dragover", e => {
  e.preventDefault(); dropZoneMulti.classList.add("over");
});
dropZoneMulti.addEventListener("dragleave", () => dropZoneMulti.classList.remove("over"));
dropZoneMulti.addEventListener("drop", async e => {
  e.preventDefault(); dropZoneMulti.classList.remove("over");
  const files = [];
  for (const item of Array.from(e.dataTransfer.items || [])) {
    const entry = item.webkitGetAsEntry?.();
    if (!entry) continue;
    if (entry.isDirectory) await readDir(entry, files);
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
