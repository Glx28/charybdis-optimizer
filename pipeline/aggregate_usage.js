const fs = require("fs");
const path = require("path");
const { writeBuild, ROOT } = require("./lib/io");

const USAGE_LOG = path.join(ROOT, "runtime", "shortcut_usage.jsonl");
const EVENTS_LOG = path.join(ROOT, "runtime", "charybdis_events.jsonl");
const SCORES_PATH = path.join(ROOT, "scripts", "keymap-optimizer", "build", "app_shortcut_scores.json");

/**
 * Normalize AHK key notation to human-readable format matching app_shortcut_scores.json.
 * AHK: ^l, ^+p, #{Space}, !{F4}  =>  Ctrl+L, Ctrl+Shift+P, Win+Space, Alt+F4
 */
function normalizeKeys(ahk) {
  let mods = [];
  let i = 0;
  while (i < ahk.length) {
    if (ahk[i] === "^") { mods.push("Ctrl"); i++; }
    else if (ahk[i] === "!") { mods.push("Alt"); i++; }
    else if (ahk[i] === "#") { mods.push("Win"); i++; }
    else if (ahk[i] === "+") { mods.push("Shift"); i++; }
    else break;
  }
  let rest = ahk.slice(i);
  // Strip AHK braces: {Space} => Space, {F4} => F4, {Enter} => Enter
  const braceMatch = rest.match(/^\{(.+)\}$/);
  if (braceMatch) rest = braceMatch[1];
  // Capitalize single letters, title-case known keys
  if (rest.length === 1) rest = rest.toUpperCase();
  else if (/^f\d+$/i.test(rest)) rest = rest.toUpperCase();
  else rest = rest.charAt(0).toUpperCase() + rest.slice(1);
  // Special AHK names to standard
  const nameMap = { "``": "`", "Escape": "Esc", "Delete": "Del", "Backspace": "Backspace" };
  if (nameMap[rest]) rest = nameMap[rest];
  return [...mods, rest].join("+");
}

function run(config) {
  const errors = [], warnings = [];

  if (!fs.existsSync(USAGE_LOG)) {
    const empty = {
      timestamp: new Date().toISOString(),
      total_events: 0, period_days: 0,
      shortcuts: {}, sequences: {}, by_app: {}, by_layer: {},
      note: "No usage data yet. Start charybdis_helpers.ahk to begin collecting.",
    };
    writeBuild("usage_stats.json", empty);
    return { success: true, output: { summary: "No usage data (shortcut_usage.jsonl not found)" }, errors, warnings };
  }

  let raw = fs.readFileSync(USAGE_LOG, "utf-8");
  if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
  const lines = raw.split(/\r?\n/).filter(Boolean);
  const shortcuts = {};
  const sequences = {};
  const byApp = {};
  const byLayer = {};
  let earliest = null, latest = null;

  for (const line of lines) {
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }

    const ts = entry.ts;
    const rawKeys = entry.keys;
    const app = entry.app || "unknown";
    const layer = String(entry.layer || "0");

    if (!rawKeys) continue;
    const keys = normalizeKeys(rawKeys);

    if (!earliest || ts < earliest) earliest = ts;
    if (!latest || ts > latest) latest = ts;

    if (!shortcuts[keys]) shortcuts[keys] = { count: 0, apps: {} };
    shortcuts[keys].count++;
    shortcuts[keys].apps[app] = (shortcuts[keys].apps[app] || 0) + 1;

    if (!byApp[app]) byApp[app] = { total: 0, shortcuts: {} };
    byApp[app].total++;
    byApp[app].shortcuts[keys] = (byApp[app].shortcuts[keys] || 0) + 1;

    byLayer[layer] = (byLayer[layer] || 0) + 1;

    if (entry.prev && entry.gap_ms) {
      const seqKey = `${normalizeKeys(entry.prev)} -> ${keys}`;
      if (!sequences[seqKey]) sequences[seqKey] = { count: 0, total_gap_ms: 0 };
      sequences[seqKey].count++;
      sequences[seqKey].total_gap_ms += entry.gap_ms;
    }
  }

  for (const [, seq] of Object.entries(sequences)) {
    seq.avg_gap_ms = Math.round(seq.total_gap_ms / seq.count);
    delete seq.total_gap_ms;
  }

  let periodDays = 0;
  if (earliest && latest) {
    periodDays = Math.max(1, Math.round((new Date(latest) - new Date(earliest)) / 86400000));
  }

  for (const [, s] of Object.entries(shortcuts)) {
    s.per_day = Math.round((s.count / Math.max(periodDays, 1)) * 10) / 10;
  }

  for (const [, a] of Object.entries(byApp)) {
    a.top = Object.entries(a.shortcuts).sort((x, y) => y[1] - x[1]).slice(0, 10).map(e => e[0]);
    delete a.shortcuts;
  }

  // ── App time tracking from charybdis_events.jsonl ──
  const appTime = {};  // exe -> seconds in foreground
  const appEvents = parseEvents();
  for (let i = 0; i < appEvents.length - 1; i++) {
    const cur = appEvents[i];
    const next = appEvents[i + 1];
    const exe = extractExe(cur.activeApp || "");
    if (!exe) continue;
    const dt = (new Date(next.updatedAt) - new Date(cur.updatedAt)) / 1000;
    if (dt > 0 && dt < 300) { // cap at 5 min per event gap (idle filter)
      appTime[exe] = (appTime[exe] || 0) + dt;
    }
  }

  // ── Blind spot analysis ──
  // Cross-reference: apps the user spends time in vs shortcuts they actually use
  const blindSpots = analyzeBlindSpots(shortcuts, appTime, periodDays);

  const output = {
    timestamp: new Date().toISOString(),
    total_events: lines.length,
    period_days: periodDays,
    shortcuts,
    sequences,
    by_app: byApp,
    by_layer: byLayer,
    app_time_seconds: appTime,
    blind_spots: blindSpots,
  };

  writeBuild("usage_stats.json", output);

  const nBlind = blindSpots.length;
  return {
    success: true,
    output: { summary: `${lines.length} events, ${Object.keys(shortcuts).length} unique shortcuts, ${periodDays} days, ${nBlind} blind spots` },
    errors, warnings,
  };
}

function readFileBomSafe(filepath) {
  if (!fs.existsSync(filepath)) return null;
  let raw = fs.readFileSync(filepath, "utf-8");
  if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
  return raw;
}

function parseEvents() {
  const raw = readFileBomSafe(EVENTS_LOG);
  if (!raw) return [];
  return raw.split(/\r?\n/).filter(Boolean).map(line => {
    try { return JSON.parse(line); } catch { return null; }
  }).filter(Boolean);
}

function extractExe(activeAppStr) {
  // "msedge.exe - ZMK Studio..." => "msedge.exe"
  // "explorer.exe - " => "explorer.exe"
  const match = activeAppStr.match(/^(\S+\.exe)\b/i);
  if (match) return match[1].toLowerCase();
  // Non-exe entries like "Charybdis beacon listener" => skip
  return null;
}

// Map exe names to app names used in app_shortcut_scores.json
const EXE_TO_APP = {
  "msedge.exe": "Browser (Chrome/Edge)",
  "chrome.exe": "Browser (Chrome/Edge)",
  "code.exe": "Visual Studio Code",
  "explorer.exe": "File Explorer",
  "windowsterminal.exe": "Windows Terminal / PowerShell",
  "powershell.exe": "Windows Terminal / PowerShell",
  "pwsh.exe": "Windows Terminal / PowerShell",
  "excel.exe": "Microsoft Excel",
  "winword.exe": "Microsoft Word",
  "powerpnt.exe": "Microsoft PowerPoint",
  "outlook.exe": "Microsoft Outlook",
  "teams.exe": "Microsoft Teams",
  "ms-teams.exe": "Microsoft Teams",
  "discord.exe": "Discord",
  "taskmgr.exe": null, // no shortcut corpus
  "searchhost.exe": null,
};

function analyzeBlindSpots(usedShortcuts, appTime, periodDays) {
  // Load the shortcut corpus
  let scores;
  try { scores = JSON.parse(fs.readFileSync(SCORES_PATH, "utf-8")); } catch { return []; }

  // Shortcuts that are almost certainly used via direct keyboard (not AHK-routed)
  // and should not be flagged as blind spots just because they're not in the log
  // These shortcuts go directly from keyboard to OS/app — they never pass through
  // AHK's SendSafe, so absence from the log does NOT mean the user doesn't use them.
  const ASSUMED_USED = new Set([
    // Universal clipboard/edit
    "Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z", "Ctrl+A", "Ctrl+S",
    "Ctrl+Y", "Ctrl+Shift+Z",
    // Navigation keys
    "Enter", "Tab", "Escape", "Space", "Backspace", "Delete",
    "Up", "Down", "Left", "Right",
    "Ctrl+Left", "Ctrl+Right", "Ctrl+Up", "Ctrl+Down",
    "Shift+Tab", "Ctrl+Enter",
    // OS-level
    "Alt+Tab", "Alt+F4", "Win+D", "Win+E", "Win+L",
    // Browser basics (direct keyboard, not AHK-routed)
    "Ctrl+T", "Ctrl+W", "Ctrl+Tab", "Ctrl+Shift+Tab",
    "Ctrl+F", "Ctrl+R", "Ctrl+N", "Ctrl+Shift+T",
    "Alt+Left", "Alt+Right",
    // Common function keys
    "F1", "F2", "F3", "F4", "F5", "F11", "F12",
    // Common VS Code (direct keyboard)
    "Ctrl+P", "Ctrl+Shift+P", "Ctrl+`", "Ctrl+B",
  ]);
  // Single bare keys that aren't real "shortcuts" (Vimium-style, game keys)
  const BARE_KEY_RE = /^[a-zA-Z0-9]$/;

  // Build set of shortcuts the user has actually used (normalized keys)
  const usedKeys = new Set(Object.keys(usedShortcuts));

  // Build per-app used shortcuts (from the shortcut log app field)
  const usedByApp = {};
  for (const [keys, info] of Object.entries(usedShortcuts)) {
    for (const appExe of Object.keys(info.apps || {})) {
      const exe = appExe.toLowerCase();
      if (!usedByApp[exe]) usedByApp[exe] = new Set();
      usedByApp[exe].add(keys);
    }
  }

  const blindSpots = [];

  for (const app of scores.apps) {
    const appName = app.name;

    // Find which exe(s) map to this app
    const matchingExes = Object.entries(EXE_TO_APP)
      .filter(([, name]) => name === appName)
      .map(([exe]) => exe);

    // Calculate time spent in this app
    let timeInApp = 0;
    for (const exe of matchingExes) {
      timeInApp += appTime[exe] || 0;
    }

    // Collect shortcuts used in this specific app
    const appUsedKeys = new Set();
    for (const exe of matchingExes) {
      for (const k of (usedByApp[exe] || [])) appUsedKeys.add(k);
    }

    for (const shortcut of app.shortcuts) {
      const keys = shortcut.keys;
      const importance = shortcut.importance || 0;
      if (importance < 3.0) continue; // only flag important ones

      const isUsed = usedKeys.has(keys) || appUsedKeys.has(keys);
      if (isUsed) continue;

      // Skip shortcuts that are almost certainly used (direct keyboard, not AHK-routed)
      if (ASSUMED_USED.has(keys)) continue;
      // Skip bare single-character keys (Vimium-style, not real shortcuts)
      if (BARE_KEY_RE.test(keys)) continue;

      // Blind spot scoring:
      // - Higher importance = bigger blind spot
      // - More time in the app = more surprising the user doesn't use it
      // - Shortcuts with universal keys (Ctrl+C etc) may be used but not logged
      //   via AHK (only SendSafe-routed shortcuts are logged)
      const timeWeight = timeInApp > 0 ? Math.min(3.0, Math.log(1 + timeInApp / 60)) : 0.5;
      const score = importance * timeWeight;

      if (score < 2.0) continue; // filter noise

      blindSpots.push({
        app: appName,
        keys,
        action: shortcut.action || "",
        importance,
        time_in_app_min: Math.round(timeInApp / 60),
        blind_spot_score: Math.round(score * 10) / 10,
        reason: timeInApp > 300
          ? `User spent ${Math.round(timeInApp/60)}min in ${appName} but never used ${keys} (${shortcut.action})`
          : `High-importance shortcut not observed in usage data`,
      });
    }
  }

  // Sort by blind spot score descending
  blindSpots.sort((a, b) => b.blind_spot_score - a.blind_spot_score);
  return blindSpots;
}

module.exports = { run, normalizeKeys };

if (require.main === module) {
  const result = run({});
  console.log("Usage aggregation:", result.output.summary);
}
