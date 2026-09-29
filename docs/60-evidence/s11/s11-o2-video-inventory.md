# S11 O2 video inventory — transferred Windows report

Recorded: 2026-09-29. Source: user-transferred final inventory and explicit user
scope decisions. Private media, metadata and filesystem were not independently
read here. This is source-availability evidence, not new physical truth or field
qualification. The [work plan](../../00-project/work-plan.md) owns sequencing;
the [O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) and
[witness validation](../../30-validation/s11-interface-observability-witness-validation.md)
own the currently enforced split and acceptance contracts.

## Available sources and current scope

| Report alias | Reported relationship | Recorded exposure | Current O2 scope |
|---|---|---|---|
| SPL#1 | Existing Heating cold-start source, recording-A for current reviews | Six runs R20 through R22-3; reviews 001–003; nine canonical segments within 480–780 s | Included |
| SPL#2 | Separate Cooling on/off recording, user confirms not a split/transform of SPL#1 | No run, review or repository reference found; full historical exposure unconfirmed | Deferred by user |
| SPL#3 | Separate Cooling cold-start recording, user confirms not a split/transform of SPL#1 | No run, review or repository reference found; full historical exposure unconfirmed | Deferred by user |

Do not start processing SPL#2 or SPL#3, assign them to partitions, or call them
certified untouched holdout. The user intends to consider them after sufficient
SPL#1 improvement. Distinct recordings in Cooling conditions would also test a
different operating mode, not only the same-domain repeatability of Heating.
The report does not establish independence between every pair beyond its stated
user confirmations or establish prior exposure from absent records alone.

SPL#1 duration is reported approximately 4,104.6 s. Its 480–780 s reviewed window
spans 300 s (about 7.3% of the video), not 300 seconds of exhaustive contour labels.
The user excludes 0–480 s as containing no target for this expansion. The user
confirms sufficient potential material after 780 s, a remaining duration of
approximately 3,324.6 s (81%). Exact episode boundaries, interface visibility,
conditions and useful positive/negative scenes there remain unreviewed. These
claims do not automatically certify every frame as previously unseen or useful.

## Source identity and canonical companion

Reported bundle-link source SHA prefix is `fb03d742...`, with 1920x1080 video,
approximately 23.976 fps and duration 4104.64 s. File size is reported
683,165,477 bytes; the receipt does not store that size. The user confirms the
same physical source file before and after earlier reviews.

The repository's canonical reviewed-truth companion currently has null source
fingerprint fields and status `operator_alias_confirmed_fingerprint_pending`.
Its Markdown owner likewise states that only alias and operator correspondence
are recorded. This is a metadata gap, not evidence that video bytes changed.
O2 bundle-link stores a video hash with `association_basis=human_attestation`:
the hash identifies bytes, while the historical review/bundle association still
depends on operator evidence. Dimensions/fps/duration alone are not unique
cryptographic identity. Copying today's hash does not retroactively prove the
exact bytes used in an old run without preserved evidence or attestation.

For eventual companion reconciliation, check the current file's complete hash
against the full local receipt, obtain size and exact available media metadata,
preserve the original companion, and record provenance of the operator mapping.
Update the Markdown identity statement together with the companion when that
canonical amendment is actually performed. Do not populate a SHA field from the
truncated prefix or invent a successful historical fingerprint verification.
No canonical source identity or reviewed segment was changed by this inventory.

V3 requires source identity in the experiment manifest; it does not require every
legacy companion field to be filled before any O2 work. The existing O2 source
receipt remains scoped evidence for linked reviews. Reconciliation should not
invalidate those labels or trigger detector reruns solely because the R6-era
companion is incomplete.

## Consequence for the next experiment

Current `validate_labels()` locks each recording_group to one partition and
rejects one run renamed into several groups. Previously reviewed cases must stay
regression. The operational procedure explicitly places all episodes, Glasses,
transforms and reruns of one recording in the same partition. Therefore the
present tool cannot combine SPL#1 regression checkpoints with later SPL#1
development/calibration/holdout episodes as a valid partitioned experiment.
The `episode_id` field alone does not grant that capability. Separate files or
invented recording groups are not valid workarounds.

Respect the user's single-recording scope. Next is a bounded design/tool contract
change for an explicitly identified **within-recording exploratory experiment**,
before asking Windows to assign or label new partitions. It must preserve one
source identity, reviewed regression labels, original receipts and frozen files;
declare non-overlapping episode ranges and temporal/physical dependencies before
fitting; keep neighboring frames and transforms with their parent episode; and
report reserved-episode results separately from independent-recording validation.
No arbitrary temporal guard duration or independent holdout claim is selected
from this inventory. The strict existing recording policy must remain the
default; any exploratory exception needs explicit schema/validation support,
tests and documented result limits rather than removal of the leakage check.

Implementation has not been performed. No split has been assigned, no new labels
have been collected, and no shadow operating point has been selected. Once this
experiment contract is concrete, a bounded review of the user-approved post-780 s
region can establish episode boundaries; it should not become an unrestricted
whole-video labeling request. SPL#2/3 remain deferred and FIELD FAIL remains.

## User clarification and sequencing correction, 2026-09-29

The user clarified that "sufficient material after 780 s" means more episodes of
the interface rising and falling, not evidence of a new phenomenon. Unexamined
scenes within 480–780 s may serve the same purpose. The earlier suggestion to
implement an episode-partition exception first is superseded as a next action,
not implemented or promoted into an authoritative split rule.

The agreed priority is the first concrete shadow discrimination experiment using
existing evidence: define inputs, separate identity/location outputs, a combined
feature hypothesis and automatic error evaluation, then implement it locally
before another Windows run. Do not substitute additional dataset inventories or
manual tables for that experiment. Additional scene selection should answer a
named evidence gap rather than follow an arbitrary 780 s boundary. Existing V3
calibration requirements and strict partition checks are unchanged; exploratory
scores do not constitute calibrated classifier decisions or holdout success.
The [work plan](../../00-project/work-plan.md) records the initial implementation
brief and the scoring/model choices that still need to be made explicitly.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: potential experiment provenance leakage if episodes of one recording are renamed into independent groups; no new production detector defect is inferred.
- Logic-map impact: NONE — inventory and proposed experiment scope do not change runtime or existing partition validation.
- Failure-registry impact: NONE — existing provenance/validation boundaries are retained; no classifier or field repair is accepted.
