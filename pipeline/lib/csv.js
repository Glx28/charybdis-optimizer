const fs = require("fs");
const path = require("path");

function csvSplit(line) {
  const out = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"' && q && line[i + 1] === '"') { cur += '"'; i++; }
    else if (ch === '"') q = !q;
    else if (ch === "," && !q) { out.push(cur); cur = ""; }
    else cur += ch;
  }
  out.push(cur);
  return out;
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const headers = csvSplit(lines.shift());
  return lines.map((line) => {
    const values = csvSplit(line);
    const row = {};
    headers.forEach((h, i) => (row[h.trim()] = (values[i] || "").trim()));
    return row;
  });
}

function loadCsv(filePath) {
  return parseCsv(fs.readFileSync(filePath, "utf-8"));
}

module.exports = { csvSplit, parseCsv, loadCsv };
