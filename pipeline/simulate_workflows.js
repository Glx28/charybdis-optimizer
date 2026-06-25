const fs = require("fs");
const path = require("path");
const { readBuild, writeBuild } = require("./lib/io");
const { effort, hand, LAYER_CONTEXTS } = require("./lib/constants");

function loadWorkflowDefs() {
  const dir = path.join(__dirname, "workflows");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")));
}

function findContext(layerStack) {
  for (const ctx of LAYER_CONTEXTS) {
    if (ctx.stack.length === layerStack.length && ctx.stack.every((l, i) => l === layerStack[i])) return ctx;
  }
  return null;
}

function simulateWorkflow(workflow, resolved, ergScores) {
  const steps = [];
  let totalEffort = 0;
  let layerTransitions = 0;
  let conflicts = [];
  let currentStack = [0];
  let thumbBusy = null;

  for (const step of workflow.steps) {
    if (step.action === "hold_layer") {
      const [hx, hy] = (step.key || "0:0").split(":").map(Number);
      const holdEffort = effort(hx, hy);
      thumbBusy = hand(hx);
      currentStack = [step.layer, ...currentStack.filter((l) => l !== step.layer)];
      layerTransitions++;
      steps.push({ desc: step.desc, effort: holdEffort, conflicts: [], position: step.key, layer: step.layer });
      totalEffort += holdEffort;
      continue;
    }

    if (step.action === "release_layer") {
      thumbBusy = null;
      currentStack = currentStack.length > 1 ? currentStack.slice(1) : [0];
      steps.push({ desc: step.desc, effort: 0, conflicts: [] });
      continue;
    }

    if (step.action === "press") {
      const [px, py] = (step.key || "0:0").split(":").map(Number);
      const keyEffort = effort(px, py);
      const keyHand = hand(px);
      const stepConflicts = [];

      if (thumbBusy && keyHand === thumbBusy && py >= 4) {
        stepConflicts.push(`${keyHand} thumb busy holding layer — can't press thumb key ${step.key}`);
      }

      const ctxName = findContextName(currentStack);
      const ctxResolved = resolved.contexts[ctxName];
      if (ctxResolved) {
        const binding = ctxResolved.resolved[step.key];
        if (!binding) {
          stepConflicts.push(`Key ${step.key} has no binding in context ${ctxName}`);
        } else if (binding.blocked) {
          stepConflicts.push(`Key ${step.key} blocked by None in context ${ctxName}`);
        }
      }

      if (stepConflicts.length) conflicts.push(...stepConflicts.map((c) => ({ step: step.desc, issue: c })));

      steps.push({
        desc: step.desc, position: step.key, layer: step.layer,
        effort: keyEffort, conflicts: stepConflicts,
        resolved_context: ctxName,
      });
      totalEffort += keyEffort;
    }
  }

  return {
    id: workflow.id,
    name: workflow.name,
    weight: workflow.weight || 1.0,
    frequency: workflow.frequency || "medium",
    total_effort: totalEffort,
    layer_transitions: layerTransitions,
    steps,
    conflicts,
    weighted_score: totalEffort * (workflow.weight || 1.0),
    pass: conflicts.length === 0,
  };
}

function findContextName(stack) {
  for (const ctx of LAYER_CONTEXTS) {
    if (ctx.stack.length === stack.length && ctx.stack.every((l, i) => l === stack[i])) return ctx.name;
  }
  return `custom_${stack.join("_")}`;
}

function run(config) {
  const errors = [], warnings = [];
  const resolved = readBuild("resolved_layout.json");
  const ergScores = readBuild("ergonomic_scores.json");
  const workflows = loadWorkflowDefs();

  if (workflows.length === 0) {
    warnings.push("No workflow definitions found in scripts/keymap-optimizer/workflows/");
    const output = { timestamp: new Date().toISOString(), results: [], rankings: [] };
    writeBuild("workflow_results.json", output);
    return { success: true, output, errors, warnings };
  }

  const results = workflows.map((wf) => simulateWorkflow(wf, resolved, ergScores));
  const rankings = results
    .sort((a, b) => b.weighted_score - a.weighted_score)
    .map((r) => ({ id: r.id, effort: r.total_effort, weight: r.weight, weighted_score: r.weighted_score, pass: r.pass }));

  const totalWeightedEffort = results.reduce((sum, r) => sum + r.weighted_score, 0);
  const failedWorkflows = results.filter((r) => !r.pass);

  if (failedWorkflows.length) {
    warnings.push(`${failedWorkflows.length} workflow(s) have conflicts`);
  }

  const output = {
    timestamp: new Date().toISOString(),
    summary: {
      total_workflows: results.length,
      passed: results.filter((r) => r.pass).length,
      failed: failedWorkflows.length,
      total_weighted_effort: totalWeightedEffort,
    },
    results,
    rankings,
  };

  writeBuild("workflow_results.json", output);
  return { success: true, output, errors, warnings };
}

module.exports = { run };

if (require.main === module) {
  const result = run({});
  const s = result.output.summary;
  console.log(`Workflows: ${s.passed}/${s.total_workflows} passed, total weighted effort: ${s.total_weighted_effort.toFixed(1)}`);
  for (const r of result.output.results) {
    const status = r.pass ? "✓" : "✗";
    console.log(`  ${status} ${r.name} — effort=${r.total_effort}, weight=${r.weight}, conflicts=${r.conflicts.length}`);
    if (r.conflicts.length) {
      for (const c of r.conflicts) console.log(`    ⚠ ${c.step}: ${c.issue}`);
    }
  }
}
