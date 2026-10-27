# OFF-1 — owner-free FULL on fast fills: review draft

**Status: REVIEW DRAFT 2026-10-27; no design, no code, nothing frozen.** The
user chose this order (2026-10-27): "그럼 이렇게하자 … 1번 진행하고 handoff
작성하자". It follows the agent's judgment, given the same day after reading
the SPL#4 review photos:
- the photos show the FULL state from 27.5 s as the clearest visual fact;
- tracking the rise needs barriers 1–3 lifted together (E3);
- E1 and E2 found no frame-local handle on SPL#4.

This is FFF-1's option 3 and FOR-2's D3, reviewed against what is now known.
The peer-side desk check of barrier 1 stays as the E3 fallback.

## Why this path

- **Truth (review-015/016, user):** SPL#4 BASE is Oil FULL from 27.5 s,
  cloudy with residual bubbles until about 42 s, and drains from 63 s.
- **What the detector publishes there today:**
  - 27.5–34.0 s: the stale owner 0018, 14 wrong-target rows (Y704–739);
  - 34.5–63 s: UNKNOWN.
- **What the photos show** (review-015/016, kept in
  `s11-review-015-photos-20261027-001` and
  `s11-review-016-photos-20261027-001`; agent reading of photos of a screen):
  - **Up to 27.0 s:** a bright, air-like region sits above the rising
    boundary. At 26.0–27.0 s the boundary is a sharp horizontal step, bright
    above and turbid blue-grey below.
  - **From 27.5 s:** the glass is uniformly turbid from the bottom band to
    the top, and the bright region is gone.
  - **Y700–720:** the top edge of a dark bottom band is visible throughout
    22–28 s, including after FULL. It behaves like background or structure,
    not a surface (inference). 0018 tracks it.
- **The tracking path is blocked three times over at 2 fps:**
  - authority: the partition demotion (E1: no Foam-based handle on SPL#4,
    [FPC-1](2026-10-27-partition-contradiction-readout.md));
  - the 32 px association cap (the fast-rise seed is unqualified; 6 fps
    gave no FULL in step 9);
  - the fill-chain handoff.
- **Densification and a higher rate are not reopened** (user, 2026-10-26).

## What already exists (source; to be confirmed by a readout)

From the
[October 15 source reading](2026-10-15-initial-full-comparison.md) and
[top-exit v3](../../20-architecture/s11-current-detector-logic-map.md):
- **A per-frame `full` state node already exists.**
  `_state_and_unknown_nodes` creates it when the current
  `oil_no_interface_full_likelihood` meets the state-evidence threshold. The
  frame classifier's own FULL rule is full ≥ 0.45 with a margin of 0.12 over
  empty.
- **The lifecycle blocks it.** `_constrain_layer` reduces an empty
  allowed-owner set to UNKNOWN even when a `full` node exists. Projection
  publishes FULL only when the selected node is `full`.
- **A non-empty allowed set keeps the `full` node.** `_constrain_layer`
  filters only Oil nodes by owner. So at 27.5–34.0 s a `full` node, if
  present, competed in selection with 0018's rows and lost; that is not
  read.
- **So a fill episode without an owner at the top can never publish FULL,**
  even if every frame says "full". On SPL#4, 34.5–63 s may be exactly this
  case (not read).
- **Top-exit v3** (opt-in) emits coordinate-free FULL only after a bounded
  same-owner rise into the top band. That is why it found no FULL on SPL#4
  (P FAIL, 2026-10-22): no owner ever rose into the band.
- **IFO v2** already accepts FULL without an interface at the start of a run
  (initial observation). Path F would do the same in mid-run, after a fill.

### Correction after compaction: an earlier gate (source desk check, 2026-10-27)

The section above names the lifecycle as the block. Source shows that the
`full` node is gated once more, before the lifecycle:
- **The likelihood reaches the sequence only from a no-interface frame
  outcome.** `oil_runtime_metrics` writes
  `oil_no_interface_full_likelihood` from a `NoInterfaceOutcome`, and 0.0
  for any other outcome
  ([`oil_pipeline_diagnostics.py:59`](../../../src/oil_tracker/adapters/vision/oil_pipeline_diagnostics.py)).
  `_raw_state_evidence` reads that value
  ([`oil_interface_selector.py:525`](../../../src/oil_tracker/adapters/vision/oil_interface_selector.py)).
- **A frame becomes no-interface only if absence beats every boundary.**
  `_positive_no_interface_is_authoritative` needs an absence likelihood of at
  least 0.58, and at least 0.10 above the best boundary hypothesis
  ([`oil_shadow_observations.py:556`](../../../src/oil_tracker/adapters/vision/oil_shadow_observations.py)).
- **So the gates run in this order:**
  1. the frame outcome is no-interface;
  2. its FULL share reaches 0.58;
  3. the lifecycle allows it (the empty allowed set).

  F1 as drafted lifts only gate 3.
- **Records already show gate 1 closed on real FULL frames:**
  - The [October 15 reading](2026-10-15-initial-full-comparison.md) found
    FULL likelihood 0 on three initial-FULL losses. The raw outcomes were
    ambiguous or an accepted boundary.
  - On SPL#1 BASE 670–678 s, all 17 traced rows read 0.0 with reason
    `not_available` ([OTR-1](2026-10-21-full-observable-top-review.md)).
  - On SPL#1 BASE 675–780 s every published FULL row came from the top-exit
    route, none from the image node
    ([top-exit v3](../../60-evidence/s11/2026-10-21-top-exit-v3-local.md)).
- **On SPL#4 BASE this is not read.** The static edge at Y700–720 and the
  residual bubbles are plausible competing boundaries (inference).
- **If gate 1 is closed there,** F1 has no existing evidence to use. Path F
  would then need a new FULL evidence that tolerates a fixed low edge. That
  is a new image feature and a larger `S11-F10` exposure, which the
  candidate below excludes.

## Candidate rule shape (not a design)

**F1, ownerless FULL closure after an observed fill.** In a fill episode
(phase FILLING or OPEN after fill onset), the lifecycle may allow the `full`
state node with no owner when all of these hold:
- **Episode:** a fill onset was observed in this run, with bottom-entry or
  fill-owner evidence. FULL never comes without a fill.
- **Full evidence:** the current `full` node meets the existing state
  threshold on K consecutive samples. The existing no-interface evidence is
  used; no new image feature.
- **No interface:** no admitted Oil row lies inside the Glass above the lower
  band. A stale low owner's rows below that band would not block FULL; how to
  bound that is open.
- **Not Foam:** no eligible Foam front or Foam-material row in the frame. A
  Glass full of Foam must not become Oil FULL. This is the main risk below.

FULL then holds as top-exit FULL does, until a drain release or EMPTY
evidence.

**Effect on SPL#4 (expected, not read):** FULL from about 27.5 s plus K
samples, if the `full` node is present there.
- The 14 wrong-target rows would end, since a FULL phase stops the
  single-owner fill path (inference from the phase order).
- 34.5–63 s would become FULL instead of UNKNOWN.

## Risks (the registry's names)

| Risk | Where it bites | What would guard it |
|---|---|---|
| `S11-F06`/`S11-F07`: Foam racing up looks like a fill; a Glass full of Foam looks like a full Glass | SPL#4 Accum 28–85 s is all Foam (review-017; the user's timeline) | Foam absence in the frame; the Accum readout must show no `full` node there, or a Foam signal on every such frame |
| `S11-F05`: a state from weak evidence | Cloudy, turbid, glare frames | K consecutive samples; the existing threshold; episode required |
| `S11-F10`: an evidence shortcut | Publishing FULL where the selector has no observation | FULL is coordinate-free and names its source (as `OIL_TOP_EXIT_FULL` does) |
| `S11-F03`/`S11-F04`: identity from position or motion | — | none needed: F1 uses no owner identity, which is its point |
| A false FULL on an empty or partial Glass with no visible interface | sample5/sample7 (never full), drains | the episode condition; the local negatives must show no FULL |

## What must be read before any design (proposed readout, not frozen)

A read-only "FULL evidence readout" over saved FULL-debug traces and local
runs. Per frame:
- `fill_state`;
- gate 1 first: the raw `oil_decision_status` and `oil_decision_reason`,
  `oil_no_interface_score` against `oil_boundary_score` (the 0.58 and 0.10
  test), and `oil_no_interface_reason`;
- `oil_no_interface_full_likelihood` and the empty likelihood, if traced;
  the R17 field notes found the full likelihood absent from an older trace,
  so presence is the first check;
- the sequence phase and reason;
- whether a `full` state node exists, and its fate in `_constrain_layer`;
- eligible Foam fronts;
- admitted Oil rows and their Y.

**Where:**

| Recording | Window | Role |
|---|---|---|
| SPL#4 BASE | 20–70 s | positive: FULL 27.5–63 s |
| SPL#4 Accum | 20–90 s | Foam-only negative |
| SPL#1 BASE | 650–700 s | positive: FULL accepted from 672 s; top-exit v3 FULL from 674.0 s |
| SPL#1 Accum | 650–700 s | Foam-layered negative (review-012) |
| sample5, sample7 (local) | — | never-full negatives |
| sample2, base_sample_1, sample4-interior (local) | — | FULL starts, IFO positives |

**Answers sought:**
- Is the raw outcome no-interface on SPL#4 BASE from 27.5 s? If not, which
  boundary hypothesis beats absence, and at what Y?
- Is the `full` node present on SPL#4 BASE from 27.5 s, and absent on SPL#4
  Accum?
- What blocks it today on SPL#4 BASE: the empty allowed set, or a phase
  rule?
- Does any never-full local control carry a sustained `full` node?

## Open questions for the user

- K, the persistence: the frame rate is 2 fps, so 2–3 samples means
  1–1.5 s of delay.
- Whether FULL may begin while a stale low owner still has rows below the
  lower band. On SPL#4 0018 keeps rows at Y704–739.
- Whether the report should name this FULL's source separately, as it does
  for top-exit FULL.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `OIL-PHASE-INITIAL`
- Failure-registry entries: `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`, `S11-F03`, `S11-F04`
- First harmful stage: on SPL#4 BASE 27.5–63 s, `OIL-PHASE-FILL` holds a fill episode with no owner at the top, so a `full` state node (if present, not read) is reduced to UNKNOWN by the empty allowed set (`_constrain_layer`); 27.5–34.0 s the stale owner publishes instead. Earlier still, a `full` node exists only if the raw frame outcome is no-interface (absence ≥ 0.58 and ≥ 0.10 over the best boundary); not read on SPL#4.
- Existing feature coverage: reviews the existing per-frame no-interface FULL evidence, `_state_and_unknown_nodes` / `_constrain_layer`, top-exit v3 (opt-in), IFO v2 and the fill-owner records; no option is exercised and no Recipe changes.
- Execution scope: a desk review of existing records, source and the kept review photos; no run, code or Windows execution.
- Logic-map impact: NONE — a review draft.
- Failure-registry impact: NONE — no new mechanism.
