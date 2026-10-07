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
artifacts, regenerate goldens or modify original recipes/truth. The adopted second-audit worktree was subsequently removed after its three
changed test files were verified identical to main. See the preservation record
below for the separately archived continued-experiment worktrees.

## Temporary-source preservation and cleanup — 2026-10-07

The user authorized preserving needed temporary material before cleanup. Local
preservation destinations are relative to the repository root:

| Original temporary source | Durable local destination | Verified scope |
|---|---|---|
| `/tmp/s11-audit-20261007-vaUpfB` | `sample/output/s11-first-audit-20261007-001` | 169 files, including full first-audit results omitted from its transfer ZIP |
| `/tmp/s11-second-audit-20261007-jtt0irop` | `sample/output/s11-second-audit-20261007-001` | Existing 203 files unchanged; five packaging/transfer files additionally preserved, 208 total |
| `/tmp/s11-continued-20261007-q8i5j175` | `sample/output/s11-continued-20261007-001` | 2,552 files/links, including three unadopted experiment snapshots |

All 2,929 entries were compared with SHA-256 or exact symlink targets before
removal and verified again afterward. Four loose support scripts/path records
were separately copied and hash-checked. Regenerable `__pycache__` entries and
obsolete worktree `.git` pointers are excluded from the experiment snapshots.
Original evidence contents and embedded execution paths are unchanged; translate
source prefixes using the preservation receipt instead of rewriting originals.

The local [preservation receipt](../../../sample/output/s11-temp-cleanup-20261007-001/preservation.json)
has SHA-256 `8a349564648c1aeb6b0a34d7e788568d1ed7a448bc7b8c802d90f38c4218ca5c`.
Its [recovery guide](../../../sample/output/s11-temp-cleanup-20261007-001/README.md)
and `recovery/<worktree-name>/` records retain each base HEAD, binary tracked
patch, status and untracked file list. Each patch was applied to its base in an
isolated Git index; every modified blob and untracked file matched its snapshot.
The snapshots are not live worktrees, and none of these experiments is adopted
into main. These preserved files are ignored local evidence, not included by
Git push; a fresh clone must obtain them separately.

The three continued worktrees were removed through Git after verification, then
the three temporary audit/experiment roots were deleted. Stale `/tmp` pytest
outputs, preserved loose support files and the five hash-matched original chat
attachments were also removed. Remaining tool references were read-only file
descriptors, with no writable handles or working directories under the removed
roots; existing POSIX descriptor reads remain valid. No process was stopped.

The separate sibling audit worktree and predictor-managed validation worktree
remain in place with their unadopted changes. Detector code, input videos,
recipes, truth, accepted results and field disposition are unchanged.

## Third audit and worktree preservation — 2026-10-07

The subsequent user request authorizes preserving worktrees and audit material,
reconciling the checkout with Git, verified temporary cleanup, commit and push.
This checkpoint starts at clean `main@a48124c9e9479864c988f6054935d48f8cc4897d`;
an origin fetch confirmed the same remote main before edits. It preserves the
third prototype without adopting its source into main.

### Supplied and native evidence

The [third audit](../../70-reference/s11-audit-2026-10-07/s11-third-audit-report-context-work-spec-2026-10-07.md),
[delivery JSON](../../70-reference/s11-audit-2026-10-07/s11-third-audit-execution-summary-2026-10-07.json)
and [code/evidence ZIP](../../70-reference/s11-audit-2026-10-07/s11-third-audit-code-and-evidence-2026-10-07.zip)
are byte-preserved in Git. The five reattached first/second audit files exactly
matched the previously imported originals. The updated
[import manifest](../../70-reference/s11-audit-2026-10-07/import-manifest.json)
pins all supplied files, recovery ZIPs and preservation records.

The third ZIP's fourteen payload hashes and twelve original corpus pins match.
The saved four-video baseline/prototype tracking CSVs match in every column
except `run_id`, across 299 rows per mode. Parsing the saved JUnit selections
confirms 2,343 distinct passing cases: 2,077 initial non-Qt, 254 Qt and twelve
recovered corpus cases, with no remaining skipped cases or failures. These are
checks of stored execution evidence, not newly executed tests or detector runs.
They do not close the historical Qt stall or establish field acceptance.

Full native third-audit evidence remains at
`sample/output/s11-third-audit-context-20261007-001`: 239 files, including nine
application/report bundles, raw crops, logs and receipts. Its
[file manifest](../../70-reference/s11-audit-2026-10-07/third-audit-native-evidence-manifest.json)
pins the files without changing original execution paths. Full bundles/media
remain ignored local evidence and are not distributed by Git push.

### Worktree recovery and cleanup

The [preservation receipt](../../70-reference/s11-audit-2026-10-07/third-audit-preservation-receipt.json)
locates complete local snapshots under
`sample/output/s11-preservation-20261007-002`. All non-cache files and symlink
targets were compared with their source; regenerable `__pycache__`,
`.pytest_cache` and obsolete worktree `.git` pointers were excluded.

| Worktree | Base | Preserved entries | Disposition |
|---|---|---:|---|
| `/private/tmp/s11-third-context-a48124c` | `a48124c` | 774 | Removed through Git after preservation and no-open-file check |
| sibling `oil_level_tracker-s11-audit-20261007` | `9f41d2f` | 763 | Preserved; live checkout retained as separate unadopted work |
| runtime-managed `validation-60a5b641bc01a37b31e60420` | `9f41d2f` | 1,306 | Preserved; managed checkout retained as separate unadopted work |

Each recovery ZIP contains its base HEAD, binary tracked patch, status, full
snapshot inventory, and untracked source/test/design files:

- [Third report recovery](../../70-reference/s11-audit-2026-10-07/third-report-worktree-recovery.zip)
- [Sibling audit recovery](../../70-reference/s11-audit-2026-10-07/sibling-audit-worktree-recovery.zip)
- [Managed validation recovery](../../70-reference/s11-audit-2026-10-07/managed-validation-worktree-recovery.zip)

For recovery, create a new detached worktree at the recorded base HEAD, unpack
the selected ZIP separately, apply `tracked.patch` there, then copy the contents
of `untracked/` into the same relative paths. Never apply a different experiment's
patch to current main as an implicit adoption. Original videos and full generated
outputs must be obtained from the local snapshot/evidence paths when required;
the source recovery ZIPs are not copies of all native artifacts.

Every tracked blob reconstructed through an isolated Git index matched its
snapshot, and all untracked files matched the original snapshot inventory.
The supplied report patch additionally reconstructed all six modified/new files
in the temporary third worktree exactly. The three recovered experiments remain
unadopted. No existing worktree was reset or rebased onto main.

Eight hash-matched attachment copies and their two empty temporary directories
were removed after repository preservation. The third native evidence and all
earlier preserved evidence were retained. The two other live worktrees retain
their original changes and HEADs; their older bases are intentional experiment
identities, not a reason to overwrite them.

The Work Plan now routes report repair and interval context review before the
bounded detector continuation. Two-second display gaps, scene captures,
domain-event compatibility and Review consistency still require their own
implementation/acceptance. A0B stays adopted, A0Q stays open, O2 stays unpromoted
and FIELD FAIL is unchanged.

Post-cleanup verification passed for all seventeen reference payload hashes,
2,843 snapshot entries, 239 native evidence files and twelve original corpus
pins. The retained worktree HEADs, tracked patches and status match their
preservation records. All 435 local links/anchors in the five updated navigation
and checkpoint documents resolve. Detector governance passes against `a48124c`;
runtime source, tests, recipes and truth are unchanged. This documentation and
preservation scope does not require another canonical detector replay.
Authored changes pass whitespace checks. The byte-preserved third-audit Markdown
retains six original two-space hard breaks reported by unrestricted Git
whitespace checking; its original hash remains unchanged.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `TRACE-PUBLICATION`, `OIL-PROJECTION`, `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: A0B repairs the test comparison contract, not a runtime stage. The supplied third audit identifies report namespace/wording/gap defects at RESULT-PRESENTATION; this preservation checkpoint does not adopt their repair. The earlier audit locates Y854 loss at authority/boundary advantage; Y821 physical identity and private-Windows first loss remain unresolved.
- Logic-map impact: NONE — only tests, external reference preservation and handoff routing change; runtime owners are unchanged.
- Failure-registry impact: NONE — existing provenance and no-shortcut guards remain; rejected experiments and field failure are not promoted.
