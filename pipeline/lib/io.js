const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const BUILD = path.join(ROOT, "build");
const SIBLING_ZMK = process.env.ZMK_CONFIG_PATH || path.resolve(ROOT, "..", "charybdis-zmk-config");
const SIBLING_TOOLS = process.env.TOOLS_PATH || path.resolve(ROOT, "..", "charybdis-tools");
const SIBLING_COACH = process.env.COACH_PATH || path.resolve(ROOT, "..", "charybdis-coach");

function ensureBuildDir() {
  if (!fs.existsSync(BUILD)) fs.mkdirSync(BUILD, { recursive: true });
}

function resolveSource(relPath) {
  const zmkPath = path.join(SIBLING_ZMK, relPath);
  if (fs.existsSync(zmkPath)) return zmkPath;
  return path.join(ROOT, relPath);
}

function readSource(relPath) {
  return fs.readFileSync(resolveSource(relPath), "utf-8");
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
  return fs.existsSync(resolveSource(relPath));
}

module.exports = { ROOT, BUILD, SIBLING_ZMK, SIBLING_TOOLS, SIBLING_COACH, readSource, readJson, readBuild, writeBuild, ensureBuildDir, sourceExists };
