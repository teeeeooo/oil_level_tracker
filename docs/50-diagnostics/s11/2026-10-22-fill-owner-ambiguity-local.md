# FOA-1 — does the SPL#4 fill-owner ambiguity reproduce on the local fills?

**Status: COMPLETE 2026-10-22.** The readings were frozen at `6e8c412` before
the readout run and are unchanged below; the [findings](#findings) follow
them. Step 2 of the Mac-only order in the
[Work Plan](../../00-project/work-plan.md), approved by the user on
2026-10-22. Diagnostics only: no detector, flag, threshold or Recipe change.

**Result in short:** the local fills reproduce the fill-owner ambiguity and,
on sample5, the re-adopted low owner's wrong-target Oil. They do not reproduce
SPL#4's unadmitted level or its fast rise: the level is admitted and rises
below the jump limit, yet tracklets that stopped following it keep fill
ownership.

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

## Run

Closed managed run `sample/output/s11-fill-owner-readout-20261022-001` at
`6e8c412`.
- **Identity gate: PASS.** In both arms the rows, phases, events,
  reconstruction, report, raw-input hash and detector version equal runs 002
  (sample5) and 001 (sample7), `run_id` aside. The readout is identical in
  both arms.
- **Estimates first:** `surface-estimates.json` (`3bacd6d3…`) was written
  before the readout existed and is unchanged.
  - sample5 is water poured into a dark scene. From 12 s to 30 s its top is a
    turbulent, bubble-filled mass, sloped and splashing by ±40–50 px. A
    horizontal surface stands by 40 s and settles near Y495.
  - sample7 is opaque milk. The estimate is the top of the white mass, froth
    included; it settles near Y575.
- **Kept:** the grid sheets, the estimates, both comparisons with the readout
  (gzipped), `readings.json` (`5ab28aba…`), the two scripts and
  `foa-timeline.png` (surface, owners, admitted level tracklets and published
  Oil over time).

## Findings

| Reading | sample5 (water) | sample7 (milk) |
|---|---|---|
| M1 `FILL_OWNER_AMBIGUOUS` | Yes: 9.5–19.5, 26.0–35.0 and 36.5–40.0 s (48 frames) | Yes: 10.0–21.5 s (24 frames) |
| M2 owners low | Windows 2–3: yes, every owner 140–269 px below. Window 1: partly. Owner 0011 follows the level at 11.5–17.5 s (−19 to +44 px); 43 of 59 owner-frames are low | No. Always two owners: one at the level (0006, then 0013; −19 to +20 px) and one low (0001, 0014, 0016; +51 to +100 px) |
| M3 level never admitted | No. An admitted tracklet is within 32 px of the level in 31 of 48 frames; only unadmitted candidates in 11; none in 6 | No. A level candidate in all 24 frames, admitted in 18 |
| M4 rise above 32 px per sample | No. About 13 px per sample on average in window 1, at most about 25 (10–14 s) | No. About 5 px per sample |
| M5 re-adopted low owner, wrong target | Yes. After each window a window owner publishes: 20.0 s +54 px (turbulent surface, marginal), 36.0 s +141 px, 40.5 s +188 px. All 21 rows after 9.0 s lie 54–226 px below. The 40.5–54.5 s rows lie 144–214 px below a clean settled surface | Re-adoption yes. Owner 0016, low at 21.5 s (+76 px), publishes 22.0–31.5 s while rising with the milk, 25–68 px below the froth top. Target undecided: it may be the froth bottom |
| Outcome | Same chain except M3 and M4: an admitted level that is not the fill owner | Differs: a level owner exists, and the ambiguity comes from a low second owner |

Unadmitted near-level candidates mostly carry no recorded failure reason
(sample5 54, sample7 51) or `INSUFFICIENT_AUTHORITY` (24, 107).
`INSUFFICIENT_NET_PROGRESS` appears 16 times in each.

**Reported, not scored:**
- **Why low owners persist (source reading; inference to verify in design):**
  - every dynamic owner reports the same direction (−1, upward) and net
    progress at every frame of its life. sample5 owner 0004 shows −1 and
    29 px from 9.5 to 15.0 s while its Y stays within 766–819; sample7 owner
    0001 shows −1 and 50 px;
  - `_advance_fill_chains` extends a fill chain with any admitted row whose
    tracklet direction is upward;
  - `_chain_is_dynamic_fill_owner` qualifies a chain from any past
    observation;
  - so a tracklet that stopped following the level keeps fill ownership while
    it is still seen.
- **`INITIAL_EMPTY_ENTRY_PENDING` is explained:** the label names an open
  phase with no fill chain under an EMPTY initial state. It does not claim an
  empty glass, and the frame publishes UNKNOWN.
  - sample5, 22.5 s: owner 0016 was last seen at 20.0 s. At 24.0 s new low
    chains from the lower entrance (0053, 0051) start another fill. They
    publish the 24.5–25.5 s rows about 200 px below the level.
  - sample7, 34.0–44.3 s: no chain follows 0016, last seen at 31.5 s.

## What it means

- **Common factor:** on all three recordings, a tracklet that no longer
  follows the level keeps dynamic fill ownership.
  - SPL#4: 0018 at Y756–785 while the level was far higher.
  - sample5: 0004, 0051, 0053, 0063, 0065, 0064 and 0082.
  - sample7: 0001, 0014 and 0016.

  `FILL_OWNER_AMBIGUOUS` and the later wrong-target rows follow from it
  (`S11-F04` stale continuation, `S11-F05` EMPTY-phase ownership lock,
  `S11-F08` owner loss).
- **Not reproduced:** SPL#4's unadmitted level (M3) and fast rise (M4). The
  SPL#4 admission inference (`S11-F02`) stays open and still needs the Windows
  `temporal_max_jump_px` and a frame review.
- **Use:**
  - sample5 is a local development case for the stale-owner wrong target.
    Its late rows sit against a clean settled surface.
  - Neither video reproduces an unadmitted fast rise, so fast-fill FULL keeps
    SPL#4 as its only case.
  - Fixing admission alone would leave sample5's ownership failure
    (inference).
- **Not decided here:** nothing is changed or tuned. Owner persistence is
  input for the step-3 D review and the step-6 design.

**Later (2026-10-22):** two readings above are corrected.
- **Owner motion:** a desk reading of these readouts (closed run
  `s11-fill-owner-contest-desk-20261022-001`) finds most low owners rising in
  parallel with the level. "Stopped following the level" fits sample5 0004
  only. The wrong rows come from a survivor of the ambiguity; see the
  [contested fill-owner gate](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate).
- **sample7:** the user judged 0016's rows correct. 0016 and the upper owners
  (0006, 0013) are the front and back arcs of one obliquely viewed surface. So
  sample7's "low" owner is not a wrong target, and its M5 target is decided:
  correct.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: on the local fills, `OIL-PHASE-FILL` ownership. A tracklet that stopped following the level stays a dynamic fill owner, so the lifecycle fails closed (`FILL_OWNER_AMBIGUOUS`) and later re-adopts a low owner, which publishes wrong-target Oil on sample5. `OIL-TRACKLET` admission is not the first harmful stage locally, because the level is admitted. On SPL#4 the admission inference stays open.
- Existing feature coverage: reuses the initial-FULL/top-exit comparison runner and its frozen empty-fill Recipes (`temporal_max_jump_px` 32), the EMPTY initial-state confirmation, the IFO v2 and top-exit v3 options as in run 003, the ROI overlay and fields the resolver already writes into completed detections. The readout and the grid add no decision; the overlay without the grid stays byte-identical.
- Execution scope: one closed local managed run (`s11-fill-owner-readout-20261022-001`, at `6e8c412`) at 2 fps with debug NONE: grid frames on sample5 and sample7, agent estimates written before the readout, then the readout comparison on both, identity gate PASS against runs 001/002. Agent frame estimates only; no user review, Windows run, tuning, flag or threshold change. A later note (2026-10-22) cites the desk run and the user's sample7 judgment; no new run.
- Logic-map impact: NONE — diagnostics only; detector code and owners are unchanged.
- Failure-registry impact: NONE — the findings fit existing entries: stale continuation blocking the level (`S11-F04`), EMPTY-phase fill ownership locking out an admitted level (`S11-F05`) and re-adoption after owner loss (`S11-F08`). `S11-F02` (the level not admitted) is not reproduced locally.
