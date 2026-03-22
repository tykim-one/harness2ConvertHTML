# Direct HWP Next Step: Skill + Prompt

## Recommendation

### Right now: choose the extraction approach first
- **Workflow skill:** none required
- **Prompt role:** `dependency-expert`
- **Why:** the real blocker is not harness logic anymore; it is choosing a workable toolchain for legacy OLE `.hwp` extraction in the current environment.

### Immediately after toolchain choice
- **Workflow skill:** `$team`
- **Mode:** `team ralph`
- **Worker prompt:** `team-executor`
- **Why:** once the extraction path is chosen, implementation splits cleanly into oracle schema, extractor, and renderer/harness wiring lanes.

---

## 1) Prompt to use now: `dependency-expert`

```text
Evaluate the best practical toolchain for direct extraction from a legacy OLE `.hwp` file in this repository.

Context:
- Final target is direct HWP extraction.
- `today_major_economy/` is the oracle/reference bundle, not the intended long-term generation mechanism.
- Sample input file: `260121 일일 주요경제지표.hwp`
- The file is legacy OLE HWP (not HWPX/zip XML).
- Current pipeline/harness already exists and can evaluate generated output.
- Current implementation surface is Python-first (`scripts/*.py`).
- Current environment appears to lack direct HWP extraction tooling such as `hwp5txt`, `hwp5html`, `soffice`, and Python packages like `olefile`, `lxml`, `bs4`, `xmltodict`.

What I need from you:
1. Recommend the strongest practical path for extracting structure from this legacy HWP file.
2. Compare 2-3 viable approaches if they exist.
3. Tell me whether the right path is:
   - a Python library,
   - a CLI converter bridge,
   - LibreOffice/soffice conversion,
   - pyhwp/hwp5proc-style tooling,
   - or an intermediate conversion format.
4. Evaluate each option for:
   - ability to recover tables / paragraphs / text runs / styles,
   - fitness for editable HTML generation,
   - maintenance and ecosystem reality,
   - license and practicality,
   - setup cost in this environment.
5. End with one concrete recommendation for immediate implementation.

Output should be action-oriented for the next execution handoff.
```

---

## 2) Prompt to use next: `$team` + `team-executor`

### Launch command
```bash
omx team ralph 3:team-executor "Implement the chosen direct-HWP extraction approach for the sample 260121 일일 주요경제지표.hwp. Use today_major_economy/ as the oracle target and keep the harness as the judge. Build a true HWP -> IR -> editable HTML path for the sample, then measure structural coverage and runtime-contract compatibility against the oracle artifacts."
```

### Task prompt
```text
Implement the chosen direct-HWP extraction approach for the sample `260121 일일 주요경제지표.hwp`.

Ground truth:
- Final target is direct HWP extraction.
- `today_major_economy/` is the oracle/reference target.
- The harness must remain the evaluation loop.
- The current bootstrap reference-copy path must not remain the primary generation method.
- The extractor approach has already been selected and should now be implemented.

Mission:
Build the first real extraction-driven path for the sample document:
1. HWP -> extracted IR
2. IR -> editable HTML/CSS/payload
3. generated output -> validated by the existing harness

Required outcomes:
1. Add the extraction stage for the chosen HWP toolchain.
2. Define or finalize the minimum IR/schema required for this sample.
3. Adapt rendering so generated output comes from IR rather than reference-copy generation.
4. Preserve runtime contract verification and run artifact reporting.
5. Produce a fresh run with concrete structural-coverage evidence against the oracle, especially `extracted_fields.json`, semantic fields, table ids, and cell mappings.

Constraints:
- Keep scope to the single sample HWP.
- Do not widen into generic multi-format support yet.
- Do not regress the harness truthfulness already established.
- Preserve editability and binding structure.
- Keep diffs tight and reversible.
- You are not alone in the codebase; coordinate and do not revert other lanes.

Suggested lane split:
- Lane 1: oracle schema + IR contract
- Lane 2: HWP extraction into IR using the selected toolchain
- Lane 3: IR-driven renderer + harness integration + coverage reporting

Definition of done:
- The sample HWP is directly parsed by the selected extraction path.
- The primary generation path is HWP -> IR -> output, not reference-copy reuse.
- A fresh run is produced.
- Runtime contract verification still works or remaining gaps are explicitly reported.
- Oracle coverage/mismatch is reported concretely.
```

---

## Simple cheat sheet
- **Need to choose the HWP extraction method first?** → `dependency-expert`
- **Need to implement after the method is chosen?** → `$team` + `team-executor`
