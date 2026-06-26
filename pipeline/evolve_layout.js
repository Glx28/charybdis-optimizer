const { execSync } = require("child_process");
const { readBuild, writeBuild, BUILD } = require("./lib/io");
const path = require("path");

function run(config) {
  const errors = [], warnings = [];
  const evolveDir = path.join(__dirname, "..", "evolve");

  let pythonCmd = "python";
  try {
    execSync(`${pythonCmd} --version`, { stdio: "pipe", shell: true });
  } catch {
    try {
      pythonCmd = "python3";
      execSync(`${pythonCmd} --version`, { stdio: "pipe", shell: true });
    } catch {
      warnings.push("Python not available, skipping evolution. Install Python 3.12+.");
      return { success: true, output: { summary: "Skipped (no Python)", skipped: true }, errors, warnings };
    }
  }

  try {
    execSync(`${pythonCmd} -c "import deap; import numpy"`, { stdio: "pipe", shell: true });
  } catch {
    warnings.push("DEAP/numpy not installed. Run: pip install -r evolve/requirements.txt");
    return { success: true, output: { summary: "Skipped (missing deps)", skipped: true }, errors, warnings };
  }

  try {
    const script = path.join(evolveDir, "run_evolution.py");
    const stdout = execSync(`${pythonCmd} "${script}" "${BUILD}"`, {
      timeout: 1800000,
      stdio: ["pipe", "pipe", "pipe"],
      cwd: evolveDir,
      shell: true,
    });

    console.log(stdout.toString().split("\n").map(l => `    ${l}`).join("\n"));

    const evoResults = readBuild("evolution_results.json");

    try {
      const candidates = readBuild("candidates.json");
      for (const sol of (evoResults.pareto_front || []).slice(0, 5)) {
        candidates.candidates.push({
          id: sol.id,
          name: `Evolution: ${sol.id} (effort=${sol.fitness.effort}, adj=${sol.fitness.adjacency})`,
          description: `NSGA-II + QD optimized. ${sol.changes_from_current || 0} changes from current. Thumb util: ${(sol.behavior?.thumb_utilization * 100 || 0).toFixed(0)}%`,
          changes: sol.changes || [],
          scoring_breakdown: sol.scoring_breakdown,
          rationale: "Multi-objective evolutionary optimization with 12-factor fitness",
          estimated_coverage_change: `${sol.total_assignments || 0} assignments`,
          risk: "medium",
        });
      }
      if (evoResults.qd_solutions) {
        for (const sol of evoResults.qd_solutions.slice(0, 3)) {
          candidates.candidates.push({
            id: sol.id,
            name: `QD Niche: ${sol.id} (balance=${(sol.behavior?.app_balance || 0).toFixed(2)}, thumb=${(sol.behavior?.thumb_utilization || 0).toFixed(2)})`,
            description: `Quality-Diversity MAP-Elites solution for niche app_balance=${(sol.behavior?.app_balance || 0).toFixed(2)}, thumb_util=${(sol.behavior?.thumb_utilization || 0).toFixed(2)}`,
            changes: sol.changes || [],
            rationale: "Quality-Diversity: best layout for this behavioral niche",
            estimated_coverage_change: `${sol.total_assignments || 0} assignments`,
            risk: "medium",
          });
        }
      }
      writeBuild("candidates.json", candidates);
    } catch (e) {
      warnings.push("Could not merge evolution results into candidates: " + e.message);
    }

    const frontSize = (evoResults.pareto_front || []).length;
    const qdSize = (evoResults.qd_solutions || []).length;
    const summary = `${frontSize} Pareto solutions` + (qdSize ? `, ${qdSize} QD elites` : "");

    return { success: true, output: { summary }, errors, warnings };
  } catch (e) {
    const stderr = e.stderr ? e.stderr.toString().slice(-500) : "";
    errors.push(`Evolution failed: ${e.message}${stderr ? "\n" + stderr : ""}`);
    return { success: false, output: {}, errors, warnings };
  }
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  console.log("Evolution:", result.output.summary || "failed");
  if (result.errors.length) console.error("Errors:", result.errors);
}
