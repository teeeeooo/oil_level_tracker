# S11 O2 W3 — first Windows target/context audit

Source: user-transferred report for code `038a3034bc4d8d681c47aa234616959fa80510a1`.
Private packets, trace and output files were not read in this checkout. Windows
execution, artifact receipts and measurements below are reported evidence; only
code/spec identities and serialization semantics were checked locally.

Current state: [work-plan](../../00-project/work-plan.md#s11-work-item-ledger).
Contracts: [W3 architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#w3-separated-shadow-targets)
and [validation](../../30-validation/s11-interface-observability-witness-validation.md#w3-separated-target-and-audit-controls).
The [local implementation evidence](s11-o2-w3-target-evaluation-local.md) is separate
from this Windows execution report.

## Identity and completion

| Item | Reported value |
|---|---|
| Code | `038a303`, ZIP without .git |
| Python/platform | 3.14.3 / Windows-11-10.0.26200-SP0 |
| Script SHA-256 | `35e2630c8ca24ff307f1ad51023ebf0042929047335db8b78cbf0d4ebbcc8157` |
| Audit artifact SHA-256 | `a559dc2b470480e6807c79a1113f03266748fe290452a686a7dab020cd97aa63` |
| Reference artifact SHA-256 | `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9` |
| Reference inputs/scores/evaluation equal | true |
| Receipt | `s11-o2-target-audit-v1`, COMPLETE |
| experiment.json SHA-256 | `ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f` |
| summary.md SHA-256 | `7f001e2dd45b955a2ba940e6742000d9f46888f0eea1897f72ebd3473906f0c1` |
| Output hashes | 2/2 checked equal on Windows |
| Input preservation | 12/12 before/after hashes equal |
| Output directory alias | `experiments/target-context-audit-001` |
| Status | EXPLORATORY_UNCALIBRATED; auto_acceptance=false; FIELD FAIL |
| Numeric localization | NOT_MEASURED |

Active labels were review-001 `labels-v2.json` revision 3, review-002
`labels-v2.json` revision 14, review-003 `labels.json` revision 4, all schema v2.
Packet links and the original indexed R22-3 bundle were reported verified; no
video was read or detector rerun. Script/artifact hashes match the local W3 record.
No complete logical label hashes were supplied in this report; do not substitute
output or raw-file hashes for them. This does not undo the reported exact reference
input comparison. Originals and frozen r10/r3 remain local, not current labels.

The pasted summary repeats the footer after each case, whereas the checked
renderer appends it once at the end. Treat the pasted material as a transferred
report, not a byte-identical copy whose SHA can be independently verified here.
No numeric error follows from that formatting difference, and no rerun is requested.

## D1 raw-file pin correction — 2026-10-08

During the later D1 handoff, the user reported that Windows stopped on the raw
file hash check and supplied the actual Windows `experiment.json` SHA-256 as
`ba5fe84b28473f7e387e363ef7d40877f559c80b1852755d997e1dd04171937f`.
The user suspects a transcription error in the Mac-side record. Both strings
are valid 64-digit hex; positions 6, 16 and 30 differ. The original transferred
value in the table above is retained as historical provenance.

The supplied correction is the current D1 execution pin. It is **user-reported
Windows evidence**, not an independent local hash measurement or proof of why
the earlier value differed. Before continuing, Windows must compute the hash
from the unchanged file and confirm this is the first target/context audit:
schema `s11-o2-target-audit-v1`, review-001/002/003 with 23/23/27 candidates and
the existing case/frame/Glass/packet identities. A different dataset/revision
or another mismatch requires a report, not changing the input or another pin.
This correction does not reverify the historical input-preservation claim,
change labels/results, complete D1 or establish detector efficacy.

## Recorded funnel facts

All three cases report RECORDED, with selected_candidate=None. Review-001 is
not_visible / filled_barrier; review-002 is visible / filled_barrier; review-003
is visible / filling. These are recorded phase states, not human scene truth.

| Review | not_selected | tracklet_not_admitted | UNKNOWN_BEFORE_RETAINED_REFS |
|---|---|---|---|
| 001 | 2,3,7,11,18,19,20 | 12,13,14,15,16,17,22 | 0,1,4,5,6,8,9,10,21 |
| 002 | 1,2,8,9,14,15,20 | 10,11,12,13,16,17,18,19,21 | 0,3,4,5,6,7,22 |
| 003 | 2,3,7,11,18,19,20,23,24,25 | 12,13,14,15,16,17,22,26 | 0,1,4,5,6,8,9,10,21 |

These disjoint sets account for all 23 / 23 / 27 candidates. Retained refs total
48, absent refs 25. No candidate is inferred to be false merely because it was
not selected or absent from retained refs.

Reviewed positives:

| Review / candidate | Identity | Recorded facts |
|---|---|---|
| 002 / 0 | interface | absent from retained refs; earlier loss unknown |
| 002 / 8,9 | interface | ANCHOR_ELIGIBLE / corroborated_material_path; tracklet, phase-row and publishable-row flags true; not selected |
| 002 / 10,12,16 | interface | CONTINUATION_ELIGIBLE / continuation; tracklet flag false and row flags false |
| 003 / 10 | interface | absent from retained refs; earlier loss unknown |
| 003 / 19 | interface | CONTINUATION_ELIGIBLE / continuation; all three admission flags true; not selected |

Reviewed negatives also reach admitted rows: all-negative 001 has seven such
unselected candidates; 002 / 20 is another. Conversely, 002 / 11 and 003 / 15
have false tracklet flags. Admission alone therefore does not certify identity.

### What these flags do not establish

Source review of `OilPathLifecycleOwner.resolve`, `OilResolutionProjectionOwner`
and `build_oil_decision_witness` confirms:

- phase_admitted and publishable are **row-membership sets** from constructed
  phase/layer nodes, copied onto each member; they are not independent per-member
  certificates or proof that every later lifecycle restriction was passed;
- the bounded selector also consumes allowed tracklet IDs and owner chains;
  publishability checks and spike suppression precede final projection;
- selected refers to the final projected node. None does not identify whether
  allowed-owner restriction, competition, ambiguity or a later check caused it;
- an absent retained ref was present in the O1 packet but may have been lost to
  authority, retention or other earlier processing. It is not proof of missing
  candidate generation or specifically top-k loss.

Thus BASE 8/9 identify a post-layer unresolved selection boundary, not a proven
selector bug or permission to relax phase gates. Accum 10 identifies a separate
pre-retention unknown. Snapshot evidence does not establish the first causal
failure in the entire video or the exact final CSV disposition.

## Context availability and limits

All values below are reported rounded band summaries. Bands/scales are correlated;
counts are availability counts, not independent examples or frame coverage.

| Review / candidate / basis | Truth | Material usable/total; median [min,max] | Static median [min,max] | Glare max |
|---|---|---|---|---|
| 001 / 10 / native | non_interface | 26/36; .0089 [.0022,.0327] | .0000 [.0000,.0185] | .0000 |
| 001 / 12 / native | non_interface | 36/36; .0036 [.0019,.0481] | .0000 [.0000,.0413] | .0000 |
| 002 / 0 / center | interface | 39/60; .0220 [.0007,.3548] | .0000 [.0000,.0228] | .0000 |
| 002 / 8 / native | interface | 45/48; .0220 [.0022,.3823] | .0000 [.0000,.0277] | .0000 |
| 002 / 9 / native | interface | 46/48; .0199 [.0025,.3685] | .0000 [.0000,.0304] | .0000 |
| 002 / 10 / native | interface | 36/36; .0198 [.0017,.3100] | .0000 [.0000,.0177] | .0000 |
| 002 / 12 / native | interface | 36/36; .0227 [.0024,.3789] | .0000 [.0000,.0413] | .0000 |
| 002 / 11 / native | non_interface | 26/36; .0946 [.0034,.2706] | .0000 [.0000,.2358] | .0000 |
| 002 / 20 / center | non_interface | 42/60; .0206 [.0005,.2344] | .0000 [.0000,.0283] | .0000 |
| 003 / 10 / native | interface | 57/60; .1819 [.0129,.6192] | .0000 [.0000,.0000] | .0000 |
| 003 / 19 / center | interface | 48/60; .1846 [.0114,.5319] | .0000 [.0000,.0000] | .0000 |
| 003 / 15 / native | non_interface | 60/60; .0768 [.0123,.2656] | .0050 [.0000,.1461] | .1137 |

Material median is higher for the reviewed negative BASE 11 than the native
positives, but lower for Accum negative 15 than its positive. BASE negative 20
also lies among positive medians. Neither a globally increasing nor decreasing
material-mean threshold is justified. Many true and false proposals have rounded
static median zero and glare identically zero. Zero static/glare cannot certify
an interface; Accum's one negative with glare does not establish a general veto.
Full ranges overlap and summarization discards sector/band arrangement. This is
not proof that all detailed contextual representations are indistinguishable.

## Decision and next boundary

Accept the reported run as completion of the requested **existing-data W3 audit**.
Do not equate it with W3 classifier efficacy or calibrated O2 acceptance. It closes
the questions of whether contextual measurements and exactly linked recorded
funnel facts exist in these packets/bundle. Their availability is now demonstrated
by the transferred execution report; their physical discriminating utility is not.

No repeat audit, additional labels, new video interval, detector rerun or threshold
selection is requested now. Keep the private detailed JSON for later exact-row
queries if a named model/design question needs them.

Next local work is W4 hypothesis/control selection. The leading design question
is whether geometry-indexed support **and opposition** can preserve partial
interface evidence without promoting isolated structure/glare. W1 motivates that
question; this run rejects treating static/glare absence or material magnitude as
its identity certificate. No formula, threshold or implementation is selected by
this report. Fix one mechanism and its primary endpoint only after its positive,
negative and indistinguishable-input controls are explicit. If those controls do
not support a mechanism, record rejection or name the missing observable rather
than adding another descriptor by default. Production phase/selection changes
remain behind O2 acceptance and W5/W6, even where this audit exposes a later loss.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F04`, `S11-F05`, `S11-F09`, `S11-F10`.
- First harmful stage: not causally established. BASE 8/9 are retained in admitted rows without final selection; Accum 10 is absent before retained-ref reporting. Row flags and final absence do not isolate allowed-owner, ambiguity, suppression or earlier retention causes.
- Logic-map impact: NONE — transferred evidence and source interpretation only; no runtime or diagnostic code changes.
- Failure-registry impact: NONE — the report narrows existing uncertainty without proving a new general mechanism or successful repair.
