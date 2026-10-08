# D2 registered-artifact sequence causality

The saved comparison now identifies the numerical chain behind later target
loss. Registration changes retained candidates and row grouping; track assignment
then changes phase ownership and selector continuity. A narrowly guarded
reciprocal-assignment probe produces **no change in all 226 completed detections**.
It is closed without promotion. No production repair, recipe adoption or field
acceptance follows. [Work Plan](../../00-project/work-plan.md) owns current state.

## Scope and reproducibility

Source HEAD: `b977d4e26b409739b640342ddea526a954551202`. Reuse the
[registered/unregistered pair](../../60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md)
from 0–56 s at 2 FPS. Deserialize saved raw candidates and call the existing
`ObservationSequenceResolver`, including both Oil and Foam owners. Wrappers
observe admission, opposition, row/track assignment, phase and bounded selection;
they return the original results. All 113 complete detections per variant equal
their saved originals, including candidates, flags, metrics and decision witnesses.
Assignment-edge observation independently preserves the same full equality.

The [machine record](2026-10-08-d2-registration-sequence-causality.json) preserves
source/input pins, output hashes, decisive edges, control results and diagnostic
script text. Large full traces remain in
`sample/output/s11-d2-registration-sequence-20261008-001/`. This investigation
reads no video or image and reruns no frame detector. Original inputs, labels,
recipes and production source remain unchanged. This is exposed Mac regression.

## Supported causal chain

Offsets below refer to the 113-sample sequence; source frame = offset × 15.
Cross-run tracklet IDs are never assumed to denote the same physical object.

1. **Exclusion also changes the competitors.** Admission first differs at 0.5 s:
   Y822.5 is removed and another candidate enters the bounded retained set.
   Admission inventories differ at 85 frames. Recurrence opposition differs at
   112 frames, including candidates that were not themselves template-matched.
   These are computational differences, not 85/112 physical errors. The previously
   reported first phase-witness difference at 36 s is not the first input change.
2. **39.5 s: row grouping changes.** Without registration, idx15/Y821 groups
   with Y827/830/830; idx17/Y838 remains a separate row. Removing idx15 lets
   the greedy 12 px span grouping place Y827/830/830/838 together. In the
   registered run, two established tracks compete for this row at costs
   0.363229 and 0.400729, inside the existing 0.08 ambiguity margin. Both
   terminate. Before registration, the Y838 row continues the existing owner.
   Earlier confirmation histories also differ, so row membership alone is not
   isolated as the sole cause.
3. **41.5 s: established priority selects a distant predecessor.** For the
   registered Y833/835/837 row, a provisional predecessor at Y836 has cost
   0.011469; an established predecessor at Y805 has cost 0.990219. The existing
   established-first rule assigns the latter. The complete reciprocal exchange
   exception does not apply: the provisional owner has no separately assigned
   residual child. This records a geometry/history link, not proof of shared
   physical identity. No nearest-row replacement is inferred.
4. **44.5 s: nonpreferred merge edges terminate both established owners.**
   The registered upper owner has a clear low-cost edge to Y837.5; the lower
   owner has a clear low-cost edge to Y882. Their less-preferred edges into an
   intermediate Y862 row differ by only 0.04. The many-to-one ambiguity rule
   terminates both owners before assignments are made. The upper row restarts
   provisionally and is not publishable at this frame.
5. **45–49.5 s: selection establishes and retains a different owner.** At
   45 s, after an UNKNOWN reset, the Y881 lower row wins the six-frame score
   (3.674397 versus UNKNOWN 3.515751). At 45.5 s it abstains, then at 46 s
   Y881 wins again (5.090026 versus upper Y833 4.390146). By 49.5 s the
   reviewed Y836 target is admitted and publishable but its score is `-inf`:
   switching from the committed lower track is forbidden without an explicit
   phase owner-chain handoff. Y880 wins at 4.545856. This is a supported
   selection barrier, not direct rejection by the artifact matcher.
6. **52 s has a distinct earlier loss.** The reviewed Y833 target survives
   calibrated matching but belongs to a new, unadmitted tracklet. It does not
   reach the publishable layer. Y862 continues the lower owner. The 49.5 s
   explanation must not be generalized to every later target loss.

The decisive registered 44.5 s edges are:

| Predecessor | Next Y837.5 row | Next Y862 row | Next Y882 row |
|---|---:|---:|---:|
| Upper established owner, last Y840 | **0.069451** | 0.632589 | no feasible edge |
| Lower established owner, last Y882 | no feasible edge | 0.592589 | **−0.035866** |

The baseline also terminates its upper/lower owners at this intermediate row.
It has an additional established owner whose preceding row includes the reviewed
false Y822 candidate; this owner then claims the upper row and eventually the
reviewed Y836 target. Therefore restoring baseline track IDs or the false candidate
would preserve an accidental recovery, not prove a correct physical association.

## Fixed reciprocal probe and result

Freeze one diagnostic-only rule before reading its outputs: when an established
track and a distinct current row are mutually clear best matches under the
**existing** margin, and that row has the existing `has_physical_proposal` witness,
its nonpreferred edges cannot attribute a merge conflict to that track. All other
ambiguity, assignment, authority, confirmation, phase and selection rules stay
unchanged. No coordinate, source-family preference or new threshold is introduced.
The existing class is patched only inside the local probe process.

The witness guard is material. At 44.5 s, the upper row consists of
`phase_transition_scan` and `calibrated_high_recall`; the lower row consists of
`phase_transition_scan`. All carry `calibrated_high_recall=1`, so neither row
has the existing physical-proposal witness. A phase-scan source name does not
override this flag. The proposed exception cannot apply safely under that contract.
The flag is an implementation category, not independent certification of truth.

| Check | Outcome |
|---|---|
| Synthetic two moving parents, clear physical children and an intermediate competing row | Original terminates parents; probe preserves both clear continuations and gives the middle row no inherited ID |
| Same scene with only calibrated children | Probe retains the original ambiguity/termination guard |
| Existing tracklet tests under the probe, including merge/split/crossing and physical-child constraints | **29 passed** |
| Unregistered saved sequence | **113/113 entire completed detections unchanged** |
| Registered saved sequence | **113/113 entire completed detections unchanged** |

An initial synthetic fixture had unequal merge costs because both parents moved
in the same direction; its assertion failed before evaluation. The corrected
control uses symmetric approaching parents to create the intended equal-cost
competition. The probe implementation and real-run preflight were not changed.

Exact selection of the seven reviewed candidate IDs remains 4/7 without
registration and 1/7 with registration, both before and after the probe. At 42.5 s
the registered row representative changes from reviewed idx12/Y835 to idx18/Y833;
shared row membership does not transfer the existing judgment. The three original
misses at 40/42/44 s predate this registration: the exact targets are absent from
retained refs, `CANDIDATE_ONLY`, and `CANDIDATE_ONLY`, respectively. Target survival
at the matcher is not authority, association, selection or scalar acceptance.

## Disposition and remaining boundary

The numerical failure path is no longer a generic "selector changed" unknown.
It combines candidate-set-dependent grouping, confirmation-dependent assignment,
merge attribution and committed-owner continuity. A single earliest **physical**
mistake is still not certified: unreviewed neighboring rows and their physical
correspondences lack truth. This is not a reason to rerun D1, request private
images or repeat closed human judgments.

The guarded reciprocal probe is **CLOSED WITHOUT PROMOTION**. Relaxing its
physical-proposal guard, preserving geometry-only owner IDs, lowering ambiguity
margins or adding exclusions for lower winners is not a justified continuation.
The next design must establish how the registered structural evidence and a
surviving boundary's actual support distinguish ownership **before** row merging
and track confirmation. It must cover structure/fluid overlap and ambiguous
support, using existing owners and stored controls first. No discriminator has
yet met that requirement; this audit does not authorize a new classifier or
declare the operator's existing structure registration sufficient for efficacy.
ML stays excluded; O2 is unmet and field disposition remains `FIELD FAIL`.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: exact registration regression at 49.5 s is the committed-owner selector barrier; 52 s target loss is tracklet non-admission. Recorded antecedents include regrouping at 39.5 s, established-first assignment at 41.5 s and merge termination at 44.5 s. First physical cause remains UNKNOWN because intermediate candidate correspondences are not certified.
- Logic-map impact: NONE — all production owners and policies are unchanged; the process-local reciprocal probe is ineffective on both real saved sequences and is not adopted.
- Failure-registry impact: NONE — changed competition, unsupported physical correspondence and candidate/public distinctions instantiate F04/F09/F10; no new accepted mechanism or field result is established.
