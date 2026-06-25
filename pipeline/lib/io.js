const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const BUILD = path.join(__dirname, "..", "build");

function ensureBuildDir() {
  if (!fs.existsSync(BUILD)) fs.mkdirSync(BUILD, { recursive: true });
}

function readSource(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), "utf-8");
}

function readJson(relPath) {
  return JSON.parse(readSource(relPath));
}

function readBuild(name) {
  return JSON.parse(fs.readFileSync(path.join(BUILD, name), "utf-8"));
}

function writeBuild(name, obj) {
  ensureBuildDir();
  fs.writeFileSync(path.join(BUILD, name), JSON.stringify(obj, null, 2), "utf-8");
}

function sourceExists(relPath) {
  return fs.existsSync(path.join(ROOT, relPath));
}

module.exports = { ROOT, BUILD, readSource, readJson, readBuild, writeBuild, ensureBuildDir, sourceExists };
