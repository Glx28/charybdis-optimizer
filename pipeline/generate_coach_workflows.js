const { readBuild, readJson } = require("./lib/io");
const fs = require("fs");
const path = require("path");

const SIBLING_COACH = process.env.COACH_PATH || path.resolve(__dirname, "..", "..", "charybdis-coach");
const WORKFLOW_DIR = path.join(SIBLING_COACH, "workflows");

const ICON_MAP = {
  teams: "chat",
  browser: "globe",
  vscode: "code",
  mfiles: "vault",
  mfiles_admin: "vault",
  windows: "desktop",
  outlook: "mail",
  excel: "table",
  explorer: "folder",
  terminal: "console",
  word: "doc",
  powerpoint: "slides",
  discord: "chat",
};

const DEFAULT_TAGS = {
  teams: ["communication", "meetings", "chat", "microsoft"],
  browser: ["chrome", "edge", "firefox", "web"],
  vscode: ["editor", "ide", "programming"],
  mfiles: ["dms", "documents", "vault"],
  mfiles_admin: ["dms", "admin", "vault"],
  windows: ["os", "system", "desktop", "window management"],
  outlook: ["email", "calendar", "microsoft", "office"],
  excel: ["spreadsheet", "office", "microsoft"],
  explorer: ["windows", "files", "folders"],
  terminal: ["powershell", "cmd", "cli", "development"],
  word: ["document", "writing", "office", "microsoft"],
  powerpoint: ["presentation", "slides", "office", "microsoft"],
  discord: ["communication", "voice", "chat"],
};

function buildScoreLookup(scores) {
  const lookup = {};
  for (const app of scores.apps) {
    for (const sc of app.shortcuts) {
      const key = `${app.id}|${sc.keys}|${sc.action}`;
      lookup[key] = sc;
    }
  }
  return lookup;
}

function formatCharybdis(match) {
  if (!match || !match.coord) return null;
  const [x, y] = match.coord.split(":");
  return `L${match.layer} (x${x},y${y})`;
}

function generate() {
  let scores;
  try {
    scores = readBuild("app_shortcut_scores.json");
  } catch {
    console.error("ERROR: build/app_shortcut_scores.json not found. Run the pipeline first:");
    console.error("  node pipeline/run_pipeline.js");
    process.exit(1);
  }

  const corpusIndex = readJson("app-keybindings/index.json");
  const scoreLookup = buildScoreLookup(scores);

  let existingIndex;
  try {
    existingIndex = JSON.parse(fs.readFileSync(path.join(WORKFLOW_DIR, "index.json"), "utf-8"));
  } catch {
    existingIndex = { version: "1.0", description: "Workflow guide index", apps: [] };
  }
  const existingTags = {};
  for (const entry of existingIndex.apps) {
    existingTags[entry.id] = entry.tags;
  }

  const newIndexApps = [];
  let totalGenerated = 0;
  let totalMapped = 0;

  for (const appEntry of corpusIndex.apps) {
    const corpus = readJson(`app-keybindings/${appEntry.file}`);
    const coachCategories = [];

    for (const cat of corpus.categories) {
      const coachShortcuts = [];
      for (const sc of cat.shortcuts) {
        const entry = { keys: sc.keys, action: sc.action };
        const scoreKey = `${corpus.id}|${sc.keys}|${sc.action}`;
        const scored = scoreLookup[scoreKey];
        if (scored && scored.mapped && scored.best_match) {
          const charybdis = formatCharybdis(scored.best_match);
          if (charybdis) {
            entry.charybdis = charybdis;
            totalMapped++;
          }
        }
        coachShortcuts.push(entry);
      }
      coachCategories.push({ name: cat.name, shortcuts: coachShortcuts });
    }

    const coachWorkflow = {
      id: corpus.id,
      name: corpus.name,
      icon: ICON_MAP[corpus.id] || "app",
      categories: coachCategories,
    };

    const outPath = path.join(WORKFLOW_DIR, `${corpus.id}.json`);
    fs.writeFileSync(outPath, JSON.stringify(coachWorkflow, null, 2) + "\n", "utf-8");
    totalGenerated++;

    const shortcutCount = coachCategories.reduce((sum, c) => sum + c.shortcuts.length, 0);
    const mappedCount = coachCategories.reduce(
      (sum, c) => sum + c.shortcuts.filter((s) => s.charybdis).length,
      0
    );
    console.log(`  ${corpus.id}: ${shortcutCount} shortcuts (${mappedCount} mapped) → ${corpus.id}.json`);

    newIndexApps.push({
      id: corpus.id,
      name: corpus.name,
      icon: ICON_MAP[corpus.id] || "app",
      file: `${corpus.id}.json`,
      tags: existingTags[corpus.id] || DEFAULT_TAGS[corpus.id] || [corpus.id],
    });
  }

  const newIndex = {
    version: "2.0",
    description: "Workflow guide index — auto-generated from app-keybindings corpus by generate_coach_workflows.js",
    apps: newIndexApps,
  };
  fs.writeFileSync(path.join(WORKFLOW_DIR, "index.json"), JSON.stringify(newIndex, null, 2) + "\n", "utf-8");

  console.log(`\nGenerated ${totalGenerated} workflow files, ${totalMapped} total mapped shortcuts.`);
}

console.log("Generating coach workflows from corpus + pipeline scores...\n");
generate();
