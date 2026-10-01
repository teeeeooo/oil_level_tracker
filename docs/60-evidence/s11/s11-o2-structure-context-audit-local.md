# S11 O2 recorded structure-context audit — local preparation

Date: 2026-10-01. Base: `89acfb0` plus local uncommitted uncertainty/context
reconciliation work. This record covers the optional audit implementation and
local validation, not private Windows results. FIELD FAIL is unchanged.

## Question and discovery

The human cannot conclusively separate BASE idx0/idx20 even with approximately
+/-5 s of movement and interface formation. That qualification is retained in
[context evidence](s11-o2-identity-context-windows-review-001.md); labels, historical
ordering and denominators remain pinned. It does not settle the separate idx11
structure-negative failure. No further rationale question or repeat clip was
requested.

Bounded source discovery found existing owners rather than a need for another
scorer:

| Owner | Finding | Boundary |
|---|---|---|
| `oil_candidate_evidence.py::OilCandidateEvidence.from_candidate` | Raw feature/penalty artifact, static, optics, texture and boundary context already feeds production evidence | Calling the typed view again would supply defaults and recompute composites; audit raw values instead |
| `artifact_calibration.py::apply_artifact_templates` and `artifact_match_score` | Registered recipe artifact templates can already record `calibrated_artifact_match` and rejection reasons | Matching geometry is not independently verified physical identity; do not rerun or tune this gate |
| `jsonl_debug_trace_writer.py` | Raw candidates serialize features/penalties with original input indices, although the list is sorted by score | Join exact indices/provenance, never list positions |
| `s11_interface_shadow_evaluation.py::extract_frame` | Verifies original candidate identity but projects O1 witness rather than all raw features/penalties | Current packet-band tables do not establish absence of original context |
| `oil_interface_witness.py` | `vessel_fitting_geometry_unavailable` is emitted as a constant reason | It does not prove recipe artifact templates absent |
| `JsonRecipeRepository` / `InspectionRecipe` | Recipe snapshots contain per-Glass geometry/template registration; deserialization supplies defaults | Raw snapshot presence is needed to distinguish absent/null/empty inventory |
| Existing target-audit helper and runner | Already own indexed original-bundle joins, reference reproduction and immutable-input receipts | Extend these owners with one optional projection, no new runner |

## Implemented boundary

`--target-audit --structure-context --bundle` projects a fixed field inventory from
raw candidate features and penalties separately, preserving missing/null/present
and raw zero. It checks original candidate inventory and source/kind/Y/rejected
provenance, exact recipe Glass identity and duplicate template IDs. It records
raw template metadata/geometry, ellipse/exclusions, reject reason and feature
score without re-evaluating production evidence or artifact matches.

The distinct schema is `s11-o2-structure-context-audit-v1`, with artifact spec
`recorded-structure-context-v1`. Original fixed-score inputs/scores/evaluation
must reproduce exactly. Ordinary target-audit behavior remains available without
the flag. Report scope is all supplied regression reviews; no hand-picked candidate
exclusion or uncertain-label replacement is implemented.

A generated summary includes all projected present values (zero included),
missing/null counts and template geometry. Detailed states remain in JSON.
Sequence witness absence does not imply raw context absence. Template existence,
recorded match, rejection or same-frame correlated measurements are not a new
identity decision, independent truth or classifier accuracy result.

## Verification

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_structure_context.py \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_review_semantics.py
```

**159 passed in 5.89 s**. Includes 23 new projection controls: original-index joins,
missing/null/zero, invalid numeric types, wrong/duplicate identities, raw template
inventory, flag dependencies, real indexed-bundle CLI from an external cwd with a
Unicode/spaced output path, unchanged v1 reference, preserved source bytes, output
hashes/COMPLETE, no overwrite and failed input-mutation receipts. The real bundle
is generated from a synthetic raster; private Windows inputs were not loaded.

Governance checker against `89acfb0` including worktree and `git diff --check`
passed. Local tests do not prove private template availability or efficacy.

## Next evidence boundary

The [operation](../../40-operations/s11-o2-local-shadow-evaluation.md#recorded-structure-context-audit--원래-번들만)
requests one read-only run on the original R22-3 bundle with rev3/14/4 labels and
original v1 reference. No video is required. Return generated summary, exact code
identity, reference reproduction, COMPLETE/output hashes and 12 preserved input
hashes. Do not register templates, edit labels, pick thresholds or rerun detection
when a field is missing. The new local source must be transferred before execution;
the historical base commit alone does not contain this option.

Use that result to determine whether a recorded distinguishing observable exists
or the evidence is absent. This is preparation for choosing an identity hypothesis,
not another score promoted on the same small sample. The current work plan alone
owns the next transition.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: a distinct structure-negative ordering failure remains, but private raw context/registered-template availability and its causal role are not yet verified. Absence from O1 projection does not prove absence from the original trace.
- Logic-map impact: NONE — this is a read-only diagnostics projection; production owners, gates, scores and publication are unchanged.
- Failure-registry impact: NONE — no new field result, general identity discriminator or repair is established.
