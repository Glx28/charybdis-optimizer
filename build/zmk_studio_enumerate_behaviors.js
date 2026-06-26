/*
  ZMK Studio — Deep enumerate all behaviors and their controls.
  Click any key first, then paste this in console.

  For each behavior:
  1. Selects it in the behavior dropdown
  2. Records what selects, inputs, checkboxes appear
  3. For behaviors with a parameter select, clicks each option
     to see if sub-controls appear (e.g. Bluetooth "Select Profile" → number input)
  4. Resets back to original state

  Does NOT save — read-only inspection.
*/
(async function enumerateBehaviors() {
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const clean = (s) => String(s || "").trim();
  const qa = (sel, root) => [...(root || document).querySelectorAll(sel)];

  function visibleSelects() {
    return qa("select").filter(s => s.offsetParent !== null);
  }

  function isBehaviorSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "Key Press")
      && [...s.options].some(o => clean(o.textContent) === "Transparent");
  }

  function isZoomSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "Auto")
      && [...s.options].some(o => clean(o.textContent) === "100%");
  }

  function isDefaultTransformSelect(s) {
    return [...s.options].some(o => clean(o.textContent) === "default_transform")
      && s.options.length <= 3;
  }

  function snapshotSelects(behaviorSel) {
    return visibleSelects()
      .filter(s => s !== behaviorSel && !isBehaviorSelect(s) && !isZoomSelect(s) && !isDefaultTransformSelect(s))
      .map(s => {
        const label = s.closest("div")?.querySelector("label")?.textContent || "";
        return {
          label: clean(label),
          selectedIndex: s.selectedIndex,
          selectedText: clean(s.options[s.selectedIndex]?.textContent),
          options: [...s.options].map(o => ({ value: o.value, text: clean(o.textContent) }))
        };
      });
  }

  function snapshotInputs() {
    return qa("input").filter(i => i.offsetParent !== null).map(i => {
      if (i.type === "checkbox") return null;
      return {
        type: i.type,
        role: i.getAttribute("role") || "",
        label: clean(
          i.getAttribute("aria-label")
          || (i.getAttribute("aria-labelledby") ? document.getElementById(i.getAttribute("aria-labelledby"))?.textContent : "")
          || i.closest("div")?.querySelector("label")?.textContent
          || ""
        ),
        value: i.value || "",
        min: i.min || undefined,
        max: i.max || undefined
      };
    }).filter(Boolean);
  }

  function snapshotCheckboxes() {
    return qa("input[type=checkbox]").filter(c => c.offsetParent !== null).map(c => {
      const label = c.closest("label")?.textContent || c.parentElement?.textContent || "";
      return { label: clean(label), value: c.value, checked: c.checked };
    });
  }

  // Find behavior select
  const behaviorSelect = visibleSelects().find(isBehaviorSelect);
  if (!behaviorSelect) {
    console.error("No behavior select found. Click a key in ZMK Studio first.");
    return;
  }

  const originalValue = behaviorSelect.value;
  const behaviors = [...behaviorSelect.options].map(o => ({
    value: o.value,
    name: clean(o.textContent)
  }));

  console.log("Found " + behaviors.length + " behaviors. Deep-enumerating each...\n");
  const results = {};

  for (const beh of behaviors) {
    // Select behavior by clicking the option directly (avoids nativeSetValue RPC errors)
    behaviorSelect.value = beh.value;
    behaviorSelect.dispatchEvent(new Event("change", { bubbles: true }));
    await sleep(800);

    const paramSelects = snapshotSelects(behaviorSelect);
    const inputs = snapshotInputs();
    const checkboxes = snapshotCheckboxes();

    const entry = {
      dropdownValue: beh.value,
      parameterSelects: paramSelects,
      inputs: inputs,
      checkboxes: checkboxes.length > 0 ? checkboxes : [],
    };

    // For behaviors with a parameter select, explore each option to find sub-controls
    if (paramSelects.length > 0) {
      const mainParamSelect = visibleSelects().find(s =>
        s !== behaviorSelect && !isBehaviorSelect(s) && !isZoomSelect(s) && !isDefaultTransformSelect(s)
      );

      if (mainParamSelect) {
        const subControls = {};
        const originalParamValue = mainParamSelect.value;

        for (const opt of [...mainParamSelect.options]) {
          mainParamSelect.value = opt.value;
          mainParamSelect.dispatchEvent(new Event("change", { bubbles: true }));
          await sleep(500);

          // Check what new controls appeared after selecting this option
          const subSelects = snapshotSelects(behaviorSelect)
            .filter(s => {
              // Only include selects that weren't the main param select
              const isMainParam = s.options.length === paramSelects[0]?.options.length
                && s.options.every((o, i) => o.text === paramSelects[0]?.options[i]?.text);
              return !isMainParam;
            });
          const subInputs = snapshotInputs();
          const subCheckboxes = snapshotCheckboxes();

          // Only record if there are sub-controls beyond what we already captured
          const hasExtra = subSelects.length > 0
            || subInputs.length > inputs.length
            || subCheckboxes.length > checkboxes.length;

          if (hasExtra) {
            subControls[clean(opt.textContent)] = {
              extraSelects: subSelects,
              extraInputs: subInputs.filter(si =>
                !inputs.some(i => i.type === si.type && i.role === si.role && i.label === si.label)
              ),
              extraCheckboxes: subCheckboxes.length > checkboxes.length
                ? subCheckboxes.filter(sc =>
                    !checkboxes.some(c => c.label === sc.label)
                  )
                : []
            };
          }
        }

        // Reset param select
        mainParamSelect.value = originalParamValue;
        mainParamSelect.dispatchEvent(new Event("change", { bubbles: true }));
        await sleep(300);

        if (Object.keys(subControls).length > 0) {
          entry.subControlsByOption = subControls;
        }
      }
    }

    results[beh.name] = entry;

    // Summary line
    const parts = [];
    if (paramSelects.length > 0) parts.push(paramSelects.length + " param select(s): [" + paramSelects.map(s => s.options.map(o => o.text).join(", ")).join("] [") + "]");
    if (inputs.length > 0) parts.push(inputs.length + " input(s)");
    if (checkboxes.length > 0) parts.push(checkboxes.length + " checkbox(es)");
    if (entry.subControlsByOption) parts.push("sub-controls on: " + Object.keys(entry.subControlsByOption).join(", "));
    if (parts.length === 0) parts.push("no parameters");
    console.log("  " + beh.name + ": " + parts.join(" | "));
  }

  // Reset to original behavior
  behaviorSelect.value = originalValue;
  behaviorSelect.dispatchEvent(new Event("change", { bubbles: true }));
  await sleep(300);

  console.log("\n=== FULL RESULTS ===");
  console.log(JSON.stringify(results, null, 2));

  try {
    await navigator.clipboard.writeText(JSON.stringify(results, null, 2));
    console.log("Copied to clipboard.");
  } catch (e) {
    console.log("Could not copy — grab from JSON above.");
  }

  return results;
})();
