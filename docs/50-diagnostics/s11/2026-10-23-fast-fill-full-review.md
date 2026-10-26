# FFF-1 — fast-fill FULL desk review (step 6 (가))

**Status: DESK REVIEW COMPLETE 2026-10-23. The user chose option 2. The
local cause check (frozen `116aa72`) is CONFIRMED
([result](#local-cause-check-result--2026-10-23)). After the SPL#4 readout
found no seed, the user rejected option 4 (accept UNKNOWN) on 2026-10-26.
The next step is a frozen SPL#4 cadence diagnostic for local densification
([decision](#user-decision--2026-10-26)).** This is step 6 (가) of the Mac-only
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

## Decision — 2026-10-23

The user ruled out option 1 for products, because analysis is already slow
and speed work is planned after the detector work:

> 지금 시간도 오래걸려서 디텍터 개선 후에는 검출 속도 개선을 할 예정이라 1번은 안될거같고. 2번으로 로컬 원인 확인 해보자

The user chose option 2 and asked for the local cause check first. The
sampling rate is used below only as a diagnostic lever.

## Local cause check (frozen 2026-10-23, before any run)

**Question:** on a local fill, does a per-sample move above the tracklet
association cap stop the level from being admitted, as inferred for SPL#4?

**Tool:** `tests/diagnostics/s11_fast_fill_cadence.py`, with 4 unit tests. It
is one managed run.

**Inputs, the same as FOA-1's integrated arm:**
- the frozen empty-fill Recipes (`s11-empty-fill-roi-20261022-001`);
- an EMPTY initial state;
- IFO v2 and top-exit v3;
- the full window;
- debug NONE.

**Arms:**

| Arm | Sampling | Tracklet association cap | Why |
|---|---|---|---|
| baseline | 2 fps | Recipe (32 px) | identity with FOA-1 |
| fps0.5 | 0.5 fps | Recipe (32 px) | the natural route: sample5's rise of about 20 px per 2 fps sample becomes about 75 px per sample, about 2.3× the cap, near SPL#4's 2.2× |
| cap9 | 2 fps | 9 px, `DirectedTrackletPolicy.maximum_jump_px` only | the same ratio without changing any frame-count constant; the row tolerance and every other policy keep the Recipe value |
| fps1 | 1 fps | Recipe | descriptive (about 40 px per sample on sample5) |

- **Videos:** sample5 runs all four arms. sample7 runs baseline, fps0.5 and
  cap9. sample7 rises about 5 px per 2 fps sample, so at 0.5 fps it stays
  under the cap (about 20 px). cap9 on sample7 is descriptive only, because
  its froth jitter of about ±15 px already exceeds 9 px.
- **Confounds, stated before the run:**
  - fps0.5 also lengthens every frame-count constant fourfold in time.
  - cap9 cannot tell the rise from jitter; both are per-sample motion.
  - Only an agreement of both arms supports the mechanism.

**Readings,** over the rising window with an agent surface estimate
(FOA-1's `surface-estimates.json`). The windows are sample5 10.0–18.0 s and
sample7 9.5–21.0 s.
- **Near the level:** an Oil candidate within 32 px of the interpolated
  estimate. This is FOA-1's unit, not the cap.
- **L:** the share of frames with an admitted near-level candidate.
- **N:** frames whose near-level candidates are all unadmitted and include
  `INSUFFICIENT_NET_PROGRESS`.
- **Also reported:** FOA-1's M3, the reasons, `FILL_OWNER_AMBIGUOUS`
  frames, numeric rows and the published offsets.
- **Baseline, from the kept FOA-1 readout (seen):**
  - sample5: L 0.824 (14 of 17), M3 no;
  - sample7: L 0.792 (19 of 24), M3 no.

**Identity gate:** the baseline rows and owner readout must equal FOA-1's
kept integrated arm. Otherwise the check is void.

**Predictions:**
- **H1, sample5 fps0.5:** L ≤ half of the baseline (0.412), and N is at
  least half of the frames with only unadmitted near-level candidates.
- **H2, sample5 cap9:** the same two conditions.
- **C, sample7 fps0.5:** L ≥ half of the baseline (0.396).

**Outcome:**
- **CONFIRMED:** H1, H2 and C all hold.
- **PARTIAL:** H2 holds, but H1 or C does not; the failing part is named.
- **NOT CONFIRMED:** H2 fails.
- **Either way:**
  - No tuning, and no change of window, distance or cap after the results.
  - A confirmation supports the SPL#4 inference only by analogy. A design
    for option 2 still needs its own frozen protocol, local controls and a
    Windows SPL#4 run.

## Local cause check result — 2026-10-23

One closed managed run, `sample/output/s11-fff-cause-check-20261023-001`, at
`116aa72`.
- **Kept:** seven per-arm JSONs (gzip, `mtime` 0) and the log, about 100 KB.
- **Time:** each analysis took 9–39 s.
- **Identity gate: PASS.** Both baselines equal FOA-1's kept integrated arm
  in rows and owner readout.

| Video / arm | Frames in window | L (admitted level) | N / unadmitted-only frames | M3 | Phase in window | Numeric Oil rows (whole run) |
|---|---:|---:|---:|---|---|---:|
| sample5 baseline | 17 | 0.824 | 1 / 3 | no | `FILL_OWNER_AMBIGUOUS` 17 | 23 |
| sample5 fps0.5 | 5 | **0.400** | **2 / 3** | yes | open: `FILL_EVIDENCE_ACCUMULATING` 3, `INITIAL_EMPTY_ENTRY_PENDING` 2 | 0 |
| sample5 cap9 | 17 | **0.059** | **14 / 16** | yes | open: `FILL_EVIDENCE_ACCUMULATING` 12, `INITIAL_EMPTY_ENTRY_PENDING` 5 | 15 |
| sample5 fps1 (descriptive) | 9 | 0.556 | 3 / 4 | no | `FILL_MOTION_OWNER` 7, open 2 | 20 |
| sample7 baseline | 24 | 0.792 | 1 / 5 | no | `FILL_OWNER_AMBIGUOUS` 23, `FILL_MOTION_OWNER` 1 | 21 |
| sample7 fps0.5 | 6 | **0.500** | 1 / 3 | no | `FILL_OWNER_AMBIGUOUS` 6 | 2 |
| sample7 cap9 (descriptive) | 24 | 0.000 | 20 / 24 | no | `FILL_MOTION_OWNER` 13, open 11 | 9 |

**Against the frozen predictions:**
- **H1, holds:** L 0.400 ≤ 0.412, and N is 2 of 3. This rests on 5 frames;
  0.400 sits just under the line.
- **H2, holds:** L 0.059 ≤ 0.412, and N is 14 of 16.
- **C, holds:** L 0.500 ≥ 0.396.

**Outcome: CONFIRMED.** On a local fill, a per-sample move above the
tracklet association cap stops the level from being admitted. The
near-level rows then fail with `INSUFFICIENT_NET_PROGRESS`. This holds both
when the move comes from a lower sampling rate and when only the cap is
narrowed at 2 fps. Nothing is tuned.

**Reported, not scored:**
- **The downstream differs from SPL#4.**
  - Unlike SPL#4's ambiguity between two low owners, sample5's test arms never
    open a fill (open, `FILL_EVIDENCE_ACCUMULATING` or
    `INITIAL_EMPTY_ENTRY_PENDING`) and publish nothing in the window.
  - On SPL#4 two low owners still kept up with the cap; here no owner forms in
    the window.
  - So admission matches SPL#4's M3, but its fill-phase picture (M1/M2) is not
    reproduced.
- **sample5 at 1 fps (about 40 px per sample) is in between.** The level is
  admitted on 5 of 9 frames. A fill owner publishes 19.6–105.4 px below the
  estimate, the same stale-owner pattern as at 2 fps.
- **sample7 at 0.5 fps keeps admission but loses publication** (2 numeric
  rows against 21). The frame-count constants confound this, so it is not
  read further.
- **sample7 cap9 loses admission entirely,** as expected from its froth
  jitter. It publishes 52.2–85.5 px below the froth top, the low arc the user
  judged correct on sample7.

**What it means for option 2:**
- The cap is the mechanism, so an option-2 design has a concrete target. It
  must let a consistent fast rise extend one tracklet beyond the per-sample
  cap.
- The same cap also separates components that merely lie near each other.
  sample7 shows jitter alone breaking association once the cap is tight, and
  sample5 at 1 fps shows a stale low owner.
- **A design needs, before any run:**
  - **Positive local cases:** sample5 at 0.5 fps or sample5 cap9 as a
    stand-in for a fast rise. There is no real local fast fill.
  - **Controls:** the 2 fps baselines of every local control must not change.
    That covers sample4, base_sample_1, sample2, sample5 and sample7.
  - **A Windows run:** SPL#4 0–90 s, compared with SPL4_B_ref. It joins the
    held LBT-2 S2 request.

## User decision — 2026-10-26

**Context:** the
[SPL#4 readout](../../60-evidence/s11/2026-10-26-step8-windows-receipt.md#f--spl4-fast-rise-readout)
found no qualifying seed for option 2. The two geometric triplets each join
three near-stationary rows, so a weaker witness would admit the `S11-F04`
transfer. By the readout rule, the user chose between a successor witness
and option 4.

**Option 4 is rejected.** The user:

> 빠른 충전도 실무에서 충분히 자주 나오는 케이스라 이걸 unknown으로 닫아버리면 지금 이 프로젝트를 하는 의미가 많이 상실되지. 샘플링 속도를 올리는건 좋은 생각이지만, 이번보다 더 빠르게 차오르는 케이스라면? 그럼 그땐 거기에 맞춰서 샘플링 속도를 더 올려야할거고 그러다보면 끝이 없어질 것 같아

**Proposed direction: local densification.** This is a proposal, not
frozen.
- **What it does:** keep the session rate. Where the completed sequence shows
  a fast-change signature, decode the source frames between the two samples
  and observe them with the same detector.
  - A signature is a lost level, or new beyond-cap tracklets with
    `INSUFFICIENT_NET_PROGRESS`. SPL#4 BASE shows both at 20.5–22.5 s.
- **The rate is chosen per gap, not by the user.** The step shrinks until the
  per-step move stays inside the association cap.
- **The rate is bounded.** The ceiling is the video's own fps. At 30 fps the
  32 px cap allows 960 px/s, about 7× the inferred SPL#4 rise. That would fill
  the 543 px BASE geometry in about 0.6 s. A faster event has no
  frame-to-frame information to recover at all.
- **Difference from option 2:** it adds real observations instead of
  inferring identity across a gap, so it does not cross `S11-F04`. A false
  trigger costs time, not output.
- **Costs to design for:**
  - The schedule is uniform today (`timestamp_schedule`). Re-detection
    reruns a range on the same schedule.
  - The frame-count constants (6-frame confirmation, 2 lost frames,
    top-exit's next-frame repetition, 3 anchors) need time semantics, or rules
    for a densified span.
  - The review and report code assume a spacing of `1/sampling_fps`.
- **Gate before any design:**
  - SPL#4 has never been run above 2 fps.
  - A frozen Windows diagnostic of SPL#4 0–90 s at 6 fps against
    `SPL4_B_ref` comes first. It shows whether denser observation admits the
    level and closes FULL at all.
  - Its readings are fixed on the Mac before the run.

**Unchanged:**
- The fast-rise association stays implemented, default OFF and not adopted.
  No successor witness is chosen.
- The user agreed the order on 2026-10-26 ("응 순서에 동의함. 진행하자"):
  1. record the decisions;
  2. reduce the debug-trace cost (output unchanged);
  3. freeze the cadence diagnostic;
  4. send one Windows request with the diagnostic and a timing measurement.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: `OIL-TRACKLET` association, confirmed locally by the cause check (both arms) and inferred on SPL#4. The per-sample cap (`temporal_max_jump_px` × gap) refuses every pairing of a fast-rising level row with an existing tracklet, so the level never accumulates the 3 observations and 27.2 px progress admission needs; `OIL-PHASE-FILL` then fails closed between two low owners (`FILL_OWNER_AMBIGUOUS`). No frame review confirms the rise rate.
- Existing feature coverage: the cause check reuses FOA-1's empty-fill Recipes, EMPTY initial state, IFO v2 + top-exit v3 arm, owner readout and agent surface estimates, the session `sampling_fps` and a diagnostic-only wrapper on `_tracklet_policy`. The review reads the current tracklet association and confirmation code, the Recipe `temporal_max_jump_px` (32 px on SPL#4, step-7 table K), the session `sampling_fps` (2.0 in every S11 run on record; a user setting up to the video fps), top-exit v3 and the held fill-owner gate as recorded on SPL#4, and FOA-1's local rise rates. No option is enabled or run.
- Execution scope: desk review of source and existing receipts; then, at the user's choice, one frozen local managed run (the cause check: sample5 and sample7 at 2/1/0.5 fps and a 2 fps arm with only the tracklet association cap narrowed, debug NONE). No Windows request, no detector change, no tuning. 2026-10-26: the user's decision and a densification proposal only; no run.
- Logic-map impact: NONE — a desk review; no owner or edge changes.
- Failure-registry impact: NONE — the mechanism fits `S11-F02` (the level row exists but is never admitted) and the option risks are stated against `S11-F03`/`F04`/`F05`.
