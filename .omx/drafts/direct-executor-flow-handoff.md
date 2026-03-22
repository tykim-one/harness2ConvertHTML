# Direct Executor Flow Handoff

## Recommended mode
- **No workflow skill required**
- **Role prompt:** `executor`
- **Why:** `$team` is currently unstable from this agent context, but the local environment is now ready for a single strong executor to keep moving.

## Current grounded starting point
- `pyhwp` / `hwp5proc` is installed in `.venv-pyhwp`
- `hwp5proc xml '260121 일일 주요경제지표.hwp'` succeeds locally
- `today_major_economy/` remains the oracle/reference target
- current harness baseline remains usable as the judge
- final target is **HWP -> IR -> editable HTML**, not reference-copy reuse

## What the executor should do next
1. Add a repo-managed extraction wrapper around `hwp5proc xml`.
2. Save the extracted XML as a stable intermediate artifact for the sample.
3. Define the first sample IR/schema.
4. Transform pyhwp XML into that IR.
5. Wire a first renderer entrypoint from IR toward generated HTML.
6. Hook the new path into the existing run pipeline so the harness can judge it.

## Recommended exact prompt for `executor`
```text
Implement the first direct executor path for the sample `260121 일일 주요경제지표.hwp` using the already-installed pyhwp/hwp5proc environment.

Ground truth:
- Final target is direct HWP extraction.
- The primary generation path must become HWP -> IR -> editable HTML, not reference-copy reuse.
- `today_major_economy/` is the oracle/reference target.
- The harness must remain the evaluation loop.
- `.venv-pyhwp` already exists and `hwp5proc xml '260121 일일 주요경제지표.hwp'` works locally.

Mission:
Build the first real single-executor slice that moves the repository from raw HWP extraction toward final editable HTML generation.

Required outcomes:
1. Add a stable extraction wrapper that runs pyhwp/hwp5proc from the pipeline.
2. Save the extracted XML as a repo-managed intermediate artifact for the sample.
3. Define the first IR/schema for this sample.
4. Transform pyhwp XML/model output into that IR.
5. Add the first renderer entrypoint that reads IR and begins generating HTML artifacts.
6. Wire the new path into the current run/harness pipeline without regressing runtime verification and reporting.
7. Report structural coverage against the oracle, especially `extracted_fields.json`, semantic fields, table ids, and cell mappings.

Suggested concrete file targets (adjust minimally if the codebase suggests a better nearby fit):
- `scripts/extract_hwp_xml.py`
- `scripts/transform_hwp_xml_to_ir.py`
- `scripts/render_ir_to_html.py`
- sample-managed intermediate artifacts under `harness/samples/260121-major-economy/` or run-managed metadata/artifact paths under `harness/artifacts/.../metadata/`
- small changes to `scripts/run_sample.py` only as needed to wire the new path in

Constraints:
- Keep scope to the sample HWP only.
- Do not widen into generic multi-format support yet.
- Do not regress harness truthfulness.
- Preserve editability and binding structure.
- Keep diffs tight and reversible.
- If full HTML generation cannot be completed in one pass, the minimum acceptable midpoint is:
  - repo-managed extraction artifact
  - first IR/schema
  - renderer entrypoint stub wired into the pipeline
  - explicit evidence of what still blocks final IR-driven HTML generation

Definition of done:
- The pipeline directly parses the sample HWP.
- A repo-managed extraction artifact exists.
- A first IR exists.
- The repository contains an IR-to-HTML generation entrypoint.
- A fresh run or verification artifact shows the new extraction-driven path is wired into the pipeline.
- Remaining gaps, if any, are concrete and evidence-backed.
```

## Acceptance checklist for the executor
- [ ] HWP XML extraction is produced by repo code, not just by an ad-hoc shell command
- [ ] Extracted XML is saved in a repeatable repo-managed location
- [ ] First IR/schema is checked in or emitted deterministically
- [ ] Renderer entrypoint exists
- [ ] Existing harness/run reporting still works
- [ ] Final report cites exact files changed and exact commands run

## Practical command shape
If switching to an executor implementation context, use the prompt above as the task body.
