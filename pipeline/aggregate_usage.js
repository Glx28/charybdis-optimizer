const fs = require("fs");
const path = require("path");
const { writeBuild, BUILD, SIBLING_TOOLS } = require("./lib/io");

const USAGE_LOG = path.join(SIBLING_TOOLS, "runtime", "shortcut_usage.jsonl");
const EVENTS_LOG = path.join(SIBLING_TOOLS, "runtime", "charybdis_events.jsonl");
const SCORES_PATH = path.join(BUILD, "app_shortcut_scores.json");

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
  const mouseClicks = {};
  const mouseByLayer = {};
  const scrollEvents = {};
  const scrollByLayer = {};
  let scrollTotal = 0;
  const layerSessions = {};
  const holdHeavy = {};
  const modifierTaps = {};
  const appFocusTime = {};
  const chainBuffer = [];  // ring buffer for 3-event chain detection
  const chains = {};
  const shortcutEventLog = [];  // flat log for workflow detection
  let earliest = null, latest = null;

  for (const line of lines) {
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }

    const ts = entry.ts;
    const eventType = entry.type || "shortcut";
    const app = entry.app || "unknown";
    const layer = String(entry.layer || "0");

    if (!earliest || ts < earliest) earliest = ts;
    if (!latest || ts > latest) latest = ts;

    if (eventType === "mouse") {
      const btn = entry.button || "MB1";
      const cnt = entry.count || 1;
      if (!mouseClicks[btn]) mouseClicks[btn] = { count: 0, apps: {}, with_modifier: {} };
      mouseClicks[btn].count += cnt;
      mouseClicks[btn].apps[app] = (mouseClicks[btn].apps[app] || 0) + cnt;
      if (entry.modifier) {
        mouseClicks[btn].with_modifier[entry.modifier] = (mouseClicks[btn].with_modifier[entry.modifier] || 0) + cnt;
      }
      if (!mouseByLayer[btn]) mouseByLayer[btn] = {};
      mouseByLayer[btn][layer] = (mouseByLayer[btn][layer] || 0) + cnt;
      if (!byApp[app]) byApp[app] = { total: 0, shortcuts: {}, mouse_clicks: 0, scroll_total: 0 };
      byApp[app].mouse_clicks = (byApp[app].mouse_clicks || 0) + cnt;
      continue;
    }

    if (eventType === "scroll") {
      const dir = entry.direction || "down";
      const ticks = entry.ticks || 1;
      const exe = app.toLowerCase();
      if (!scrollEvents[exe]) scrollEvents[exe] = { up: 0, down: 0, left: 0, right: 0 };
      scrollEvents[exe][dir] = (scrollEvents[exe][dir] || 0) + ticks;
      scrollTotal += ticks;
      scrollByLayer[layer] = (scrollByLayer[layer] || 0) + ticks;
      if (!byApp[app]) byApp[app] = { total: 0, shortcuts: {}, mouse_clicks: 0, scroll_total: 0 };
      byApp[app].scroll_total = (byApp[app].scroll_total || 0) + ticks;
      continue;
    }

    if (eventType === "layer_session") {
      const sl = String(entry.layer || "0");
      if (!layerSessions[sl]) layerSessions[sl] = { count: 0, total_duration_ms: 0, total_keys: 0, key_freq: {} };
      layerSessions[sl].count++;
      layerSessions[sl].total_duration_ms += entry.duration_ms || 0;
      const kp = entry.keys_pressed || [];
      layerSessions[sl].total_keys += kp.length;
      for (const k of kp) {
        layerSessions[sl].key_freq[k] = (layerSessions[sl].key_freq[k] || 0) + 1;
      }
      continue;
    }

    if (eventType === "app_focus") {
      const prevApp = entry.prev_app || "";
      const dur = entry.prev_duration_ms || 0;
      if (prevApp) {
        appFocusTime[prevApp] = (appFocusTime[prevApp] || 0) + dur;
      }
      continue;
    }

    if (eventType === "modifier_tap") {
      const key = entry.key || "unknown";
      modifierTaps[key] = (modifierTaps[key] || 0) + 1;
      continue;
    }

    if (eventType === "typing_counter") {
      const tkeys = entry.keys || "unknown";
      const tcount = entry.count || 1;
      if (!shortcuts[tkeys]) shortcuts[tkeys] = { count: 0, apps: {}, by_layer: {} };
      shortcuts[tkeys].count += tcount;
      shortcuts[tkeys].apps[app] = (shortcuts[tkeys].apps[app] || 0) + tcount;
      shortcuts[tkeys].by_layer[layer] = (shortcuts[tkeys].by_layer[layer] || 0) + tcount;
      if (!byApp[app]) byApp[app] = { total: 0, shortcuts: {}, mouse_clicks: 0, scroll_total: 0 };
      byApp[app].total += tcount;
      byApp[app].shortcuts[tkeys] = (byApp[app].shortcuts[tkeys] || 0) + tcount;
      continue;
    }

    // shortcut, functional, layer_key — all handled as key events
    const rawKeys = entry.keys;
    if (!rawKeys) continue;
    const keys = normalizeKeys(rawKeys);
    const repeatCount = entry.repeat_count || 1;

    if (!shortcuts[keys]) shortcuts[keys] = { count: 0, apps: {}, by_layer: {} };
    shortcuts[keys].count += repeatCount;
    shortcuts[keys].apps[app] = (shortcuts[keys].apps[app] || 0) + repeatCount;
    shortcuts[keys].by_layer[layer] = (shortcuts[keys].by_layer[layer] || 0) + repeatCount;

    if (!byApp[app]) byApp[app] = { total: 0, shortcuts: {}, mouse_clicks: 0, scroll_total: 0 };
    byApp[app].total += repeatCount;
    byApp[app].shortcuts[keys] = (byApp[app].shortcuts[keys] || 0) + repeatCount;

    byLayer[layer] = (byLayer[layer] || 0) + repeatCount;

    if (entry.prev && entry.gap_ms) {
      const seqKey = `${normalizeKeys(entry.prev)} -> ${keys}`;
      if (!sequences[seqKey]) sequences[seqKey] = { count: 0, total_gap_ms: 0 };
      sequences[seqKey].count++;
      sequences[seqKey].total_gap_ms += entry.gap_ms;
    }

    if (entry.held_ms && entry.held_ms >= 500) {
      if (!holdHeavy[keys]) holdHeavy[keys] = { count: 0, total_hold_ms: 0 };
      holdHeavy[keys].count++;
      holdHeavy[keys].total_hold_ms += entry.held_ms;
    }

    // Chain detection: variable-length sliding windows (2, 3, 4, 5 events)
    const evt = { keys, ts, app, layer };
    shortcutEventLog.push(evt);
    chainBuffer.push(evt);
    if (chainBuffer.length > 5) chainBuffer.shift();
    for (let winSize = 2; winSize <= chainBuffer.length; winSize++) {
      const win = chainBuffer.slice(chainBuffer.length - winSize);
      const spanMs = new Date(win[winSize - 1].ts) - new Date(win[0].ts);
      if (spanMs > 10000) continue;
      const sameApp = win.every(e => e.app === win[0].app);
      if (!sameApp) continue;
      const chainKey = win.map(e => e.keys).join(" -> ");
      if (!chains[chainKey]) chains[chainKey] = { count: 0, total_ms: 0 };
      chains[chainKey].count++;
      chains[chainKey].total_ms += spanMs;
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

  // Finalize layer sessions
  for (const [, ls] of Object.entries(layerSessions)) {
    ls.avg_duration_ms = Math.round(ls.total_duration_ms / Math.max(ls.count, 1));
    delete ls.total_duration_ms;
    ls.avg_keys_per_session = Math.round((ls.total_keys / Math.max(ls.count, 1)) * 10) / 10;
    ls.common_keys = Object.entries(ls.key_freq).sort((a, b) => b[1] - a[1]).slice(0, 10).map(e => e[0]);
    delete ls.key_freq;
  }

  // Layer switch activations: how many times each layer was activated
  const layerSwitchActivations = {};
  for (const [layerNum, ls] of Object.entries(layerSessions)) {
    layerSwitchActivations[layerNum] = ls.count;
  }

  // Finalize hold-heavy keys
  for (const [, h] of Object.entries(holdHeavy)) {
    h.avg_hold_ms = Math.round(h.total_hold_ms / Math.max(h.count, 1));
    delete h.total_hold_ms;
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

  // Merge app_focus time into appTime (more accurate when available)
  for (const [exe, ms] of Object.entries(appFocusTime)) {
    const key = exe.toLowerCase();
    const sec = Math.round(ms / 1000);
    if (sec > 0) appTime[key] = (appTime[key] || 0) + sec;
  }

  // ── Finalize chains ──
  for (const [, c] of Object.entries(chains)) {
    c.avg_total_ms = Math.round(c.total_ms / Math.max(c.count, 1));
    delete c.total_ms;
  }

  // ── Workflow detection: repeated subsequences of 3-5 shortcuts ──
  const workflows = {};
  for (let winSize = 3; winSize <= 5; winSize++) {
    for (let i = 0; i <= shortcutEventLog.length - winSize; i++) {
      const window = shortcutEventLog.slice(i, i + winSize);
      const spanMs = new Date(window[winSize - 1].ts) - new Date(window[0].ts);
      if (spanMs > 15000) continue;
      const apps = new Set(window.map(e => e.app));
      if (apps.size > 1) continue;
      const wfKey = window.map(e => e.keys).join(" -> ");
      if (!workflows[wfKey]) workflows[wfKey] = { count: 0, apps: {} };
      workflows[wfKey].count++;
      const app = window[0].app;
      workflows[wfKey].apps[app] = (workflows[wfKey].apps[app] || 0) + 1;
    }
  }
  // Filter: only keep workflows with count >= 3
  for (const key of Object.keys(workflows)) {
    if (workflows[key].count < 3) delete workflows[key];
  }

  // ── Blind spot analysis ──
  // Cross-reference: apps the user spends time in vs shortcuts they actually use
  const blindSpots = analyzeBlindSpots(shortcuts, appTime, periodDays);

  // Build by_layer_shortcut: {keys -> {layer -> count}} for layer-aware fitness
  const byLayerShortcut = {};
  for (const [keys, data] of Object.entries(shortcuts)) {
    if (data.by_layer && Object.keys(data.by_layer).length > 0) {
      byLayerShortcut[keys] = data.by_layer;
    }
  }

  const output = {
    timestamp: new Date().toISOString(),
    total_events: lines.length,
    period_days: periodDays,
    shortcuts,
    sequences,
    by_app: byApp,
    by_layer: byLayer,
    by_layer_shortcut: byLayerShortcut,
    chains,
    workflows,
    app_time_seconds: appTime,
    blind_spots: blindSpots,
    mouse_clicks: mouseClicks,
    mouse_by_layer: mouseByLayer,
    scroll_events: scrollEvents,
    scroll_total: scrollTotal,
    scroll_by_layer: scrollByLayer,
    layer_sessions: layerSessions,
    layer_switch_activations: layerSwitchActivations,
    hold_heavy: holdHeavy,
    modifier_taps: modifierTaps,
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
  // With the expanded logger, most shortcuts are now actually captured.
  // Only assume keys that Windows intercepts before AHK can see them.
  const ASSUMED_USED = new Set([
    "Ctrl+Alt+Delete",
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
