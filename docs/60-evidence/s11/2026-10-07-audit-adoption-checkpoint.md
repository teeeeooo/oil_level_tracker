# S11 audit adoption checkpoint — 2026-10-07

This record owns the checkout integration evidence and handoff, not the live
milestone state. [Work Plan](../../00-project/work-plan.md) remains the current
owner. Scope: import the supplied audits, adopt their A0B test repair, validate,
and prepare the user-authorized commit/push checkpoint. A1–A4 implementation and
A0Q repair are subsequent work; no detector improvement is claimed here.

## Identity and adopted change

- Starting branch: clean `main`; local HEAD and remote main both
  `9f41d2f8a517da21f570f57ed1b4e2009a9d48db`.
- Adopted test source commit: `fa2d6d536140fdb08c8b8c68ef369ce89dd49e35`.
- Applied exactly the supplied `a0b-test-contract.patch`: three tests,
  102 insertions / 9 deletions. All `src/` files and historical fingerprint
  constants are unchanged.
- The legacy characterization view excludes only named trace additions.
  Its fixture-specific reason translation first checks all 44 current leaves,
  frame order and candidate cardinality, then maps the 20 known reason deltas.
  Thirteen new guards reject unexpected reasons/structure and preserve all
  other leaves and input objects. Five text I/O calls now declare UTF-8.
- The rejected paired scorer remains archived in the supplied ZIP. It is not
  installed in `src/`, imported by runtime, or collected by canonical tests.

## Preserved inputs and evidence

The [import manifest](../../70-reference/s11-audit-2026-10-07/import-manifest.json)
identifies all five supplied files plus selected native evidence by SHA-256.
Original Markdown, JSON and ZIP bytes are preserved. They are reference sources,
not a second plan; their audit-time “not applied to main” prose is historical.

- [First audit](../../70-reference/s11-audit-2026-10-07/s11-audit-and-detector-work-spec-2026-10-07.md)
  and its execution summary establish the baseline defects.
- [Second audit](../../70-reference/s11-audit-2026-10-07/s11-second-audit-and-detector-work-spec-2026-10-07.md)
  and delivery summary supply the tested A0B patch and rejected experiment.
- [Code/evidence ZIP](../../70-reference/s11-audit-2026-10-07/s11-second-audit-code-and-evidence-2026-10-07.zip)
  contains 14 manifest-pinned payloads, all verified before applying the patch.
- Full native `final_receipt.json` and `execution-summary.json` hashes match
  the second audit. All 75 native receipt artifacts and 12 original corpus
  video/recipe/truth pins were verified locally.
- Full native artifacts remain at
  `sample/output/s11-second-audit-20261007-001` (ignored, Mac-local).
  The original `/tmp/s11-second-audit-20261007-jtt0irop` prefix in copied evidence
  identifies the execution; resolve that prefix to the durable directory.
  Do not rewrite receipt bytes or original media paths.
- The initial Qt native stack and focused retry summary are included in the
  tracked reference packet. A fresh clone receives these and the curated ZIP,
  but not full PNGs, replay bundles or media. Obtain the preserved local evidence
  when needed; do not infer its presence from a successful Git pull.

## Adoption verification

Fresh verification at the adopted commit completed successfully:

| Selection | Result |
|---|---|
| Focused three changed files plus test-authoring policy | 58 passed, 3.50 s |
| Canonical non-Qt | 2,072 passed, 170.10 s |
| Canonical Qt | 254 passed, 9.19 s; no timeout in this run |
| Canonical union | 2,326 distinct cases, zero overlap |
| Compared with first-audit JUnit node set | 2,313 retained, 13 new guards, zero removals |

The [verification receipt](2026-10-07-a0b-adoption-verification.json) records exact
source/test Git tree identities, commands, run timings and log/JUnit hashes.
The original audit's longer timings belong to that run and are not replaced.
No performance improvement claim follows from the elapsed-time difference.

Canonical execution is serial, in fresh processes with
`PYTHONDONTWRITEBYTECODE=1`, `QT_QPA_PLATFORM=offscreen`,
`-p no:cacheprovider`, `-vv`, `-o faulthandler_timeout=30` and JUnit output.
An external process-group timeout is fixed at 2400 seconds for non-Qt and
240 seconds for Qt. Timeout is a failed/incomplete run, never a PASS.

The full adoption logs and JUnit live in
`sample/output/s11-a0b-adoption-20261007-001`; the tracked verification receipt
pins their hashes and exact commands. Later handoff-document changes do not
change the tested source tree. Final governance/link/whitespace checks cover
those documentation changes separately. Passing Qt in this run does not repair
the previously observed intermittent stall.

Governance passes against the original audit base; 420 local links/anchors in
the changed owner/checkpoint documents resolve. Source-tree comparison and all
historical fingerprint constants are unchanged. Whitespace checking passes for
authored changes. The two byte-preserved source Markdown files retain ten
original Markdown hard-break lines flagged by unrestricted `git diff --check`;
they are intentionally not rewritten, and their hashes still match the inputs.

## Resume instructions and boundaries

1. Start at the Work Plan, then second audit §8 A1. Reuse the existing
   `phase_candidate_assembler.py` frame-local sidecar and
   `oil_interface_witness`/diagnostic adapters. Search current callers first.
2. Close exactly three measurement gaps: actual upper/lower/common-X support
   and censoring; signed center/partner source-Y pair semantics; proposal,
   transition and final scalar coordinates with score dependency lineage.
3. Keep these diagnostics out of `PhaseDetection.debug_metrics`,
   `OilCandidateEvidenceIndex` and resolver authority inputs. Preserve candidate
   count/order/source/Y/score/flags, raw/completed returns, Foam, events, CSV,
   reports and prior diagnostic fields. Prove schema/binding/availability,
   malformed-input and output-safety controls, four-video equality and bounded
   time/RSS/trace resources before A2.
4. Treat A0Q separately through `ui/controllers/preflight_controller.py` and
   `tests/unit/test_preflight_controller.py`: retain the native stall, use fixed
   timeout and bounded retries, establish a causal lifecycle repair and its
   completion/failure/cancel/generation/close regression before closing it.
5. A2 requires adopted A0B plus verified A1. The tested paired scorer is rejected:
   it leaves frame420 Y821 unresolved; Sample3's 29→27 Oil count hides seven
   additions and nine withdrawals. Preserve those losses and collisions.
   A3 Foam local-front support has its own owner and controls. A4 reuses W3 and
   target binding; exposed development/regression clips are not holdout.

At this checkpoint: S11 ACTIVE, W4 OPEN, O2 not promoted, FIELD FAIL retained.
No independent holdout, private Windows replay, new physical/scalar labels,
production scorer, or field qualification was performed. Previous passive
review/binding and appearance experiments stay closed at their recorded scopes.

For test-only rollback, revert `fa2d6d5`; do not reset the checkout, erase audit
artifacts, regenerate goldens or modify original recipes/truth. Existing detached
audit worktrees are retained; their cleanup is not required for this checkpoint.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `TRACE-PUBLICATION`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: this adoption repairs the test comparison contract, not a runtime stage. The supplied audit locates Y854 loss at authority/boundary advantage; Y821 physical identity and private-Windows first loss remain unresolved.
- Logic-map impact: NONE — only tests, external reference preservation and handoff routing change; runtime owners are unchanged.
- Failure-registry impact: NONE — existing provenance and no-shortcut guards remain; rejected experiments and field failure are not promoted.
