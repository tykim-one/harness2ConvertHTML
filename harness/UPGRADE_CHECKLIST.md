# Upgrade Checklist

Use this after every direct HWP run.

## Extraction quality
- [ ] `extract_hwp_xml.json` exists
- [ ] warning count reviewed
- [ ] extracted XML size looks plausible
- [ ] extraction stderr log inspected when warning count increases

## IR quality
- [ ] `extracted_hwp_ir.json` exists
- [ ] paragraph/table counts reviewed
- [ ] oracle coverage reviewed
- [ ] unmatched labels reviewed

## Main path quality
- [ ] main generated HTML is IR-driven
- [ ] main payload/state exist
- [ ] runtime contract passes
- [ ] unresolved mappings reviewed
- [ ] fallback field count reviewed

## Scaffolding debt
- [ ] remaining reference scaffolding reviewed
- [ ] next reduction target selected

## Fidelity readiness
- [ ] capture status checked
- [ ] review status checked
- [ ] next visual-fidelity task recorded when captures exist

## Upgrade handoff
- [ ] `review/upgrade_targets.json` reviewed
- [ ] next highest-priority target chosen
- [ ] changes and evidence appended to run history
