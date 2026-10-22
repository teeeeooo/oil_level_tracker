# FOA-1 — does the SPL#4 fill-owner ambiguity reproduce on the local fills?

**Status: FROZEN 2026-10-22 before the readout run.** Step 2 of the Mac-only
order in the [Work Plan](../../00-project/work-plan.md), approved by the user on
2026-10-22. Diagnostics only: no detector, flag, threshold or Recipe change.

## Question

The [SPL#4 follow-up](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)
found this chain on Windows only:
- **M1:** while the level rose, every frame was `filling` /
  `FILL_OWNER_AMBIGUOUS` (more than one dynamic fill owner) with an empty owner
  chain, so it published UNKNOWN.
- **M2:** the owners were two admitted tracklets, both low.
- **M3:** the higher candidates were new provisional tracklets each frame,
  `INSUFFICIENT_NET_PROGRESS` with direction 0, never admitted.
- **M4 (inference):** a rise of about 70 px per 2 fps sample outruns tracklet
  association.
- **M5:** afterwards a re-adopted low owner published wrong-target numeric Oil.

Does the same chain occur on sample5 (water) and sample7 (milk)? Both are
public fill videos, EMPTY at the start and never full (user-confirmed). If it
does, they become local development cases for the fast-fill FULL and
stale-owner items. If it does not, the difference narrows the cause.

**Known before this run** (runs 001–003, debug NONE; not new evidence):
- `FILL_OWNER_AMBIGUOUS` covers sample5 at 9.5–19.5, 26.0–35.0 and 36.5–40.0 s,
  and sample7 at 10.0–21.5 s.
- sample5's selected Oil ends 160–200 px below its settled surface (about Y491).
- `temporal_max_jump_px` is 32 px in both frozen Recipes. Tracklet association
  uses it as its maximum jump.
- Under an EMPTY initial state, a chain becomes a dynamic fill owner only if it
  starts in the lower entrance band and shows confirmed upward progress.

## Method

- **Frames first:** `--roi-overlay --grid` writes source-scale frames with a
  source-Y grid at fixed times:
  - sample5: 8.5, 10, 12, 14, 16, 18, 20, 25, 30, 40, 54.5 s;
  - sample7: 9.5, 11, 13, 15, 17, 19, 21, 25, 31.5, 36, 44 s.

  The agent reads the visible liquid surface on the Glass centre line to about
  10 px, or "not visible", and records it before reading any readout. These
  are agent observations, not user truth. Between checked times the estimate
  is interpolated linearly.
- **Readout:** the existing `--compare` mode with the frozen empty-fill Recipes,
  an EMPTY initial state and `--top-exit-comparison`, as in run 003, plus the
  new read-only `--owner-readout`. Per frame it copies fields the resolver
  already emits:
  - phase, reason and owner chain;
  - the lifecycle's dynamic fill owners, allowed set and established owner;
  - each Oil candidate's Y, selection and tracklet fields (id, lifecycle,
    admission, direction, net progress, failure reason, observation count,
    identity contradiction, authority reason).
- **Identity gate:** rows, phases, events and reconstruction must equal the kept
  comparison files (sample5 run 002, sample7 run 001), `run_id` aside.
  Otherwise the readout is void and nothing is interpreted.

## Readings fixed before the run

Per video, with 32 px (one association jump) as the distance unit:
- **R1 (M1, M2):** in each `FILL_OWNER_AMBIGUOUS` frame, the dynamic fill
  owners: count, admission, current Y, and offset from the surface estimate. An
  owner more than 32 px below the surface is low.
- **R2 (M3):** in the same frames, the Oil candidates within 32 px of the
  surface estimate, with their tracklet fields.
  - M3 holds if, in at least half of the frames with a visible surface, such a
    candidate exists, none is admitted, and the commonest failure reason is
    `INSUFFICIENT_NET_PROGRESS`.
  - Otherwise the case is recorded as found: no candidate near the surface (a
    miss before tracklets), an admitted level that is not a fill owner, or
    another failure reason.
- **R3 (M4):** the surface rise per 2 fps sample across each ambiguity window.
  M4 is supported only where it exceeds 32 px.
- **R4 (M5):** the first published numeric Oil after each ambiguity window:
  - its tracklet;
  - whether that tracklet was a dynamic owner in the window;
  - its offset from the surface estimate (more than 32 px below is a wrong
    target).
- **Outcome:** a video shows the same chain when M1, M2, M3 and M5 hold. Any
  difference is named. M4 is reported on its own.
- **Not scored:** the return to `INITIAL_EMPTY_ENTRY_PENDING` while liquid is
  present (sample5 22.5 s, sample7 34.0–44.3 s), unless the readout explains
  it. Foam is not read.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: not yet read on these videos. On SPL#4 it is `OIL-TRACKLET` admission during the rise (inference), with `OIL-PHASE-FILL` failing closed between two low owners; this run checks whether the local fills share it.
- Existing feature coverage: reuses the initial-FULL/top-exit comparison runner and its frozen empty-fill Recipes (`temporal_max_jump_px` 32), the EMPTY initial-state confirmation, the IFO v2 and top-exit v3 options as in run 003, the ROI overlay and fields the resolver already writes into completed detections. The readout and the grid add no decision; the overlay without the grid stays byte-identical.
- Execution scope: one local managed run at 2 fps with debug NONE: grid frames on sample5 and sample7, then the readout comparison on both, gated on identity with runs 001/002. Agent frame estimates only; no user review, Windows run, tuning, flag or threshold change.
- Logic-map impact: NONE — diagnostics only; detector code and owners are unchanged.
- Failure-registry impact: NONE — readings frozen before the run; results will be mapped to existing entries first.
