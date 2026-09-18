# S11 O2 durable local review records

Date: 2026-09-18. Review base: `d7c1ebe1a86584682838634678a798eeca7d0884`.
Scope: offline record management and the existing evaluator's draft validation.
No `src/` file, detector version, trace format, authority or selector changes.
Existing R22-3 bundles are inputs; no detector rerun is needed for this workflow.
Current gate remains owned by [work-plan](../../00-project/work-plan.md).

## Ownership and implementation

The existing [O2 CLI](../../../tests/diagnostics/s11_interface_shadow_evaluation.py)
now routes four additional commands to the bounded
[record-management companion](../../../tests/diagnostics/s11_review_records.py).
Discovery covered existing O2 packet/freeze code, product truth identity/repository,
bundle/index readers and repository-wide atomic-write/record-management searches.
The companion reuses the production reader, SHA-256 helpers and public atomic text
writer. The product `.oiltruth` schema does not own O2 candidate labels or packets;
no parallel reader, GUI or production truth format was introduced.

- `link-bundle`: validates exact indexed record/witness equality, records hashes
  of manifest/recipe/session/trace/index, and a human-attested source-video digest.
  A conservative scene identity stores video bytes, frame, source dimensions and
  Glass geometry. The selected video's original association is not retroactively
  proven by calculating its digest.
- `relink`: checks those identities before changing relative/absolute transport
  locators, keeping the previous receipt snapshot and locator history.
- `status`: validates packets/drafts, reports pending/unreviewed/held judgments
  and content revision. Optional receipt checks report locator existence but do
  not pretend to rehash live media on every question.
- `record`: serializes one human reply under an exclusive writer lock and expected
  label hash, validates the complete draft, archives old JSON and atomically
  replaces live labels. Scene attribution is distinct from candidate corrections;
  existing v1 attribution is preserved without inventing a past timestamp.

Freeze remains strict. Existing frozen snapshots and old packet/label formats
remain readable. Subsequent draft edits cannot change an old frozen label set.
The [procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) specifies
external data storage, one-frame pilot then small batches, agent questions and
human replies, interruption recovery and preservation of original review folders.

## Verification

- Full local suite: **1,851 passed** in 167.55 seconds, including the Qt-marked
  tests. The invocation used `-m 'not qt'`; the repository marker is `qt_app`,
  so this selected the entire collected suite, not just non-Qt tests.
- After adding the explicit link/relink CLI round trip and preserving legacy v1
  scene attribution on candidate-only edits, final focused tests: **55 passed**.
  This includes 34 existing evaluator cases and 21 durable-record cases.
- Controls cover real writer/store/indexed-reader linkage; exact record mismatch
  despite a recomputed packet hash; moved data trees; non-repo/non-ASCII CLI entry;
  Windows cross-drive fallback; stale edits; overlapping writers; invalid labels;
  interrupted destination writes and retry; unchanged frozen snapshots; and wrong
  video/changed trace rejection. Source/video association in fixtures is explicit.
- No runtime source changed. Existing O1 behavior-equality evidence was not
  invalidated, so the four detector replays were not repeated.
- Governance and `git diff --check` passed. Main reviewed the change directly;
  no independent-agent audit or Windows field acceptance is claimed.

## Limits

No target Windows run, private frame classification, physical source association,
real shadow model or O2 discrimination PASS was performed here. Synthetic media
bytes in record tests exercise identity only, not video decoding or physical truth.
Different encodings/geometry do not automatically inherit labels. No command maps
candidate labels across executions; scene keys preserve evidence for later explicit
correspondence. Receipts and history are local integrity/audit aids, not signatures,
proof of an untouched holdout, or backups against loss of the work-PC disk.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: no new detector failure inferred; the bounded risk addressed is offline loss or misassociation of reviewed source/record/candidate provenance.
- Logic-map impact: NONE — offline record storage does not change any mapped detector, publication or UI execution path.
- Failure-registry impact: NONE — storage controls preserve existing provenance contracts and do not claim a physical field repair.
