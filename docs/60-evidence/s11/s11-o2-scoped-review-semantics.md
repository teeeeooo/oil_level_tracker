# S11 O2 scoped review semantics — local implementation evidence

Date: 2026-09-18. Repository: `oil_level_tracker`, branch `main`, implementation
base `7462ef7`. This record covers offline annotation/evaluation tooling only.
Private Windows labels and images were not accessed or modified here. Field
status remains `FIELD FAIL`; no image classifier or new detector revision is
claimed.

## Implemented boundary

The existing `s11_interface_shadow_evaluation.py` owns label validation, explicit
v1 interpretation, reviewable witness geometry, freeze versions and metric
semantics. Its existing `s11_review_records.py` companion owns migration and
scoped human reply transactions. The companion's relative-locator helper was
moved into the evaluator and reused by receipts, migration, combine and freeze,
including the different-Windows-drive fallback. No duplicate label system or
new GUI was introduced. No production source file changed.

- `prepare` emits labels v2. Existing packets/witnesses and prediction format stay
  v1. Existing v1 labels and frozen sets remain readable; v1 record replies retain
  their original field semantics.
- `migrate` locks source/destination, requires an expected source hash and a new
  destination, preserves v1 judgments as `legacy_annotation`, retains prior reply
  history and original attribution, archives the original logical JSON, and
  writes v2 atomically. Original label files, receipts, packets, replies, history
  directories and frozen results are not overwritten. Migration is separately
  attributed and does not increment the human-reply revision count.
- Identity is independent of exact path agreement. Multiple artifact tags and
  free-text descriptions are permitted without adding identity votes. Missing
  subtype does not force uncertain identity. Legacy localization_mismatch stays
  positive identity with its original qualification retained.
- Path replies require the enclosing candidate ID/hash and exact witness
  X/Y/geometry basis. Native paths are not synthesized from scalar candidates.
  Partial updates preserve unmentioned geometry, identity and scene provenance.
  Missing path judgments stay unreviewed. Explicitly reusing a prior direct human
  judgment is possible with its basis/note; no script parses notes into truth.
- Status shows identity and separate native/candidate-center review coverage.
  Neither qualitative near-interface labels nor whole-candidate identity creates
  a reviewed contour or a numeric localization certificate.
- Reports use `s11-o2-shadow-report-v2` with the input label schema named. The old
  localized-frame metric is replaced by identity-support recall. All versus
  supported proposal path counts are separate. Numeric localization reports all
  versus supported interface proposals, eligible/matched coverage, per-sector
  errors and interval width/coverage. No contour means not_measured/null rather
  than zero error; full-path PASS remains null without an accepted tolerance and
  coverage policy. Visible empty-candidate frames and unverified support remain
  in their respective denominators.
- Existing v1 reports are not edited. Combining mixed label versions requires
  explicit migration first; combined sets retain source label hashes/locators.
  Source review trees remain the history owner.

## Verification

Focused command:

```text
.venv/bin/python -m pytest tests/unit/test_interface_shadow_evaluation.py tests/unit/test_s11_review_records.py tests/unit/test_s11_review_semantics.py tests/integration/test_debug_trace_bundle_output.py -q
```

Result: **91 passed**. Controls include all legacy label mappings, exact witness
joins, partial-path/whole-candidate separation, absent-contour and exact-X metrics,
overlapping artifact descriptions, no-model results, source and frozen-file
preservation, failed migration/retry, existing-output/stale-revision rejection,
scoped attribution, and migrated data-tree relocation. Real bundle writer/indexed
reader fixtures exercise prepare, receipt reuse, record/freeze/evaluate and
unchanged trace bytes. CLI migration/save/freeze/evaluation runs from a foreign
working directory with non-ASCII paths and no inherited stdin. Different-drive
locator fallback is simulated; these checks are local macOS tests, not a Windows
execution claim.

Canonical groups ran in separate pytest processes:

- `.venv/bin/python -m pytest -m 'not qt_app' -q` — **1,631 passed**, 254 deselected.
- `.venv/bin/python -m pytest -m qt_app -q` — **254 passed**, 1,631 deselected.

Detector governance against base `7462ef7`, `git diff --check`, and local file-link
checks for all changed Markdown documents passed. Main reviewed the changed
persistence/evaluation entry paths and their reuse boundaries. No production
`src/` files changed; no full-video replay or target-Windows run was performed.

The changed contract retains the existing
[validation owner](../../30-validation/s11-interface-observability-witness-validation.md).
No public-video rerun is required for this offline-only change; production
extraction/execution did not change. Existing O1 equality evidence is retained.
No operating point, private contour, new classifier result or field PASS was
inferred from these tests.

## Windows continuation

Use the updated [local procedure](../../40-operations/s11-o2-local-shadow-evaluation.md),
starting with “기존 review-001 / review-002 재개 — 먼저 한 번만 변환”. Replace only the
code checkout. Migrate each existing review to `labels-v2.json` beside the old
file; compare status and keep the same bundle-link. Existing R22-3 bundles do not
need rerunning. Already explicit human path judgments can be recorded after
exact correspondence checks; incomplete per-path scope is not filled from
candidate identity or reference-coordinate differences. Resume bounded annotation
only after the saved prior judgments are confirmed unchanged locally.

The transferred review-001 and review-002 counts are checkpoint assertions for
that local confirmation, not private constants in tool control flow. Their actual
Windows conversion remains to be performed. Classification remains NOT_EVALUATED
until a separately developed shadow classifier supplies predictions.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: offline review/evaluation semantics — a whole-candidate interface judgment previously implied localized frame support despite absent contour or partially off-interface path points. This does not identify or repair a production detector stage.
- Logic-map impact: NONE — offline label migration and evaluator metrics do not change the mapped R22-3 detector, resolver, trace publication or selected same-frame observations.
- Failure-registry impact: NONE — the change strengthens existing provenance/coordinate interpretation controls without claiming a new field cause or field repair.
