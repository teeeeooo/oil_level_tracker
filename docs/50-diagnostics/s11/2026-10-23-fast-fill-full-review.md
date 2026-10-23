# FFF-1 — fast-fill FULL desk review (step 6 (가))

**Status: DESK REVIEW COMPLETE 2026-10-23 (source and existing receipts only;
no run); the user decides the next step.** This is step 6 (가) of the Mac-only
order in the [Work Plan](../../00-project/work-plan.md), started at the
user's choice ("남은건 3번"). Windows is unavailable for now. No detector,
flag, Recipe, session or truth change.

## Question

On SPL#4 BASE, the user's timeline places the fast rise at 21–25 s and FULL
at 24–25 s. No FULL is ever published, with or without top-exit v3
([receipt](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22)).
The follow-up found two low admitted owners holding fill ownership
(`FILL_OWNER_AMBIGUOUS`, 22.5–27.0 s). The higher rows meanwhile appeared as
new provisional tracklets with `INSUFFICIENT_NET_PROGRESS`
([follow-up](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)).
Why is the rising level never admitted, and which route to FULL fits the
existing architecture?

## Mechanism (from source)

`OIL-TRACKLET`,
[`DirectedTrackletTracker._match_cost`](../../../src/oil_tracker/adapters/vision/oil_interface_tracklets.py):
- **Hard association cap:** a row may extend a tracklet only if
  |Δy| ≤ `maximum_jump_px` × frame gap. It must also lie within
  `maximum_jump_px` of the velocity prediction. Otherwise the pair gets no
  cost and the row starts a new tracklet.
- **The cap is per sample, not per second.** `maximum_jump_px` is the Recipe
  `temporal_max_jump_px` ([`_tracklet_policy`](../../../src/oil_tracker/adapters/vision/oil_observation_resolver.py)),
  32 px on SPL#4 (step-7 table K). At the session's 2 fps that is 64 px/s.
- **Admission needs a chain.** Confirmation needs at least 3 observations in a
  6-frame window and net progress of at least 5 % of the height. On SPL#4
  BASE (`geometry_height` 543.4) that is 27.2 px. A one-row tracklet has zero
  progress, so it fails with `INSUFFICIENT_NET_PROGRESS`.

**SPL#4 fits this exactly (inference; no frame review yet):**
- The level must cross from about Y800 (the last witness, 21.5 s) to the top
  (`geometry_top_y` 291.2) within about 3–4 s. That is about 70 px per 2 fps
  sample, against a 32 px cap.
- Each new level row is therefore too far from every tracklet. It starts its
  own tracklet, which never gains progress.
- Fill ownership stays with the two low owners that the cap does let through.
  Top-exit needs an owner in the top band, so it has nothing to act on.

**Local fills do not reach the cap.** sample5 and sample7 rise 5–25 px per
sample ([FOA-1](2026-10-22-fill-owner-ambiguity-local.md)).

## The existing setting that changes the cap's meaning

The session's sampling rate (`AnalysisSession.sampling_fps`, default 2.0) is a
user setting. The main window's "회/초" spin box goes up to the video's own
fps (30 on SPL#4).
- **Required rate:** at 2 fps the inferred rise is about 70 px per sample. At
  6 fps it would be about 23 px per sample, under the 32 px cap, and leaves
  room for a rise up to about 190 px/s.
- **Never exercised:** every S11 detector run on record used 2 fps. Several
  constants count frames, not seconds:
  - the 6-frame confirmation window;
  - 2 lost frames;
  - top-exit's next-frame repetition;
  - the 3-anchor rule.

  At 6 fps each covers a third of the time. The time-based limits (the 3.0 s
  Foam seed age) do not change. So a higher rate is a different operating
  point, not a neutral refinement.

## Options

1. **A higher sampling rate, no code change (recommended first).**
   - **Why first:** the cap is exactly the mechanism above, and the sampling
     rate is an existing user setting. Nothing is added to the detector.
   - **Cost:** about 3× the frames and the run time.
   - **Unknown behaviour:** every frame-count constant shortens in time. That
     needs controls: does 6 fps change known-good outputs?
   - **Product use:** a user would have to know when to raise the rate. It
     needs guidance (fast fills) or a default change. The user decides after
     evidence.
   - **Check, Mac:**
     - a frozen local cadence check. sample5 at 0.5 fps would show whether a
       local fill loses admission once its per-sample rise exceeds 32 px (the
       mechanism, both ways). sample4, sample5, sample7, base_sample_1 and
       sample2 at 6 fps would show the cost against their 2 fps outputs.
   - **Check, Windows (later):** SPL#4 0–90 s at 6 fps against SPL4_B_ref.
     It would join the held LBT-2 S2 request.
2. **Velocity-aware association (`OIL-TRACKLET` design).**
   - **What it does:** a row beyond the cap may extend a tracklet when a
     bounded chain shows consistent monotonic progress.
   - **Risk:** it crosses `S11-F03` (motion promoted to identity) and
     `S11-F04` ("geometry or recurring Y never proves identity"). The cap is
     what keeps a jump from merging two components.
   - **Evidence base:** SPL#4 is the only case, and it is Windows-only. It
     needs its own frozen design and two-sided controls.
3. **Owner-free FULL evidence (`OIL-PHASE-FILL` design).**
   - **What it does:** FULL comes from a bounded sweep of fill evidence from
     the bottom to the top followed by an interface-free Glass, with no
     admitted owner.
   - **Risk:** the largest design and the highest recurrence risk. That is
     `S11-F05` (a state from weak evidence), `S11-F03` and `S11-F10`. Foam
     racing up with the Oil (SPL#4 from 23 s) would also look like a sweep
     (`S11-F06`/`F07`).
4. **Accept UNKNOWN on fast fills (status quo).**
   - **Behaviour:** the production default already fails closed from 34.5 s
     to 63 s.
   - **Remaining defect:** the 14 wrong-target rows at 27.5–34.0 s, which
     the held gate would remove. The report shows the span as "직접 유면 확인
     어려움" and never FULL.

**Cost of option 1 (user, 2026-10-23: 2 fps already takes long; 6 fps
would take far longer and the bundle could blow up):**
- **Time:** step-7 SPL#1 480–780 s took about 42–44 min per run at 2 fps
  with FULL debug. At 6 fps that is at least about 2 h 10 min, if the time
  stays linear in the number of frames. Completed-sequence resolution may
  grow faster than that.
- **Size:** the SPL#1 FULL debug trace was about 1.8–1.9 GB for 1,202
  records, and the bundle about 2 GB. At 6 fps it would be about 5–6 GB.
  Without FULL debug the size problem largely goes away, but the time does
  not.
- **Meaning:** as a product fix, option 1 roughly triples every analysis.
  That is a product cost, not a detector detail, so it needs the user's
  limit first. As a diagnostic, a short local check (local videos, no FULL
  debug) only confirms the mechanism.

**Recommendation (revised after the cost note):** option 1 is not a product
fix unless about 3× analysis time is acceptable. If it is not, the choice is
between option 2 (a designed association change, evidence on SPL#4 only) and
option 4 (accept UNKNOWN). The short local cadence check is still a cheap
way to confirm the mechanism before choosing option 2.

**Original recommendation:** option 1's local cadence check first. It is cheap, adds
no detector code and tests the mechanism directly. Its result decides between
option 1 (with a Windows SPL#4 run), option 2 and option 4. If the user
chooses it, the check is frozen with its readings before any run.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: inferred `OIL-TRACKLET` association. The per-sample cap (`temporal_max_jump_px` × gap) refuses every pairing of a fast-rising level row with an existing tracklet, so the level never accumulates the 3 observations and 27.2 px progress admission needs; `OIL-PHASE-FILL` then fails closed between two low owners (`FILL_OWNER_AMBIGUOUS`). No frame review confirms the rise rate.
- Existing feature coverage: reads the current tracklet association and confirmation code, the Recipe `temporal_max_jump_px` (32 px on SPL#4, step-7 table K), the session `sampling_fps` (2.0 in every S11 run on record; a user setting up to the video fps), top-exit v3 and the held fill-owner gate as recorded on SPL#4, and FOA-1's local rise rates. No option is enabled or run.
- Execution scope: desk review of source and existing receipts; no run, no Windows request, no tuning.
- Logic-map impact: NONE — a desk review; no owner or edge changes.
- Failure-registry impact: NONE — the mechanism fits `S11-F02` (the level row exists but is never admitted) and the option risks are stated against `S11-F03`/`F04`/`F05`.
