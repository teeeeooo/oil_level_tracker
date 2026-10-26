# FOR-1 — why SPL#4 is `FILL_OWNER_AMBIGUOUS`, and does recent motion separate fill owners?

**Status: READINGS FROZEN 2026-10-27, before the run.** Step 1 of the
fill-owner gate revisit in the [Work Plan](../../00-project/work-plan.md),
approved by the user on 2026-10-27 ("응 이 순서로 진행하자", then
"응 그렇게 진행하자"). Diagnostics only: no detector, flag, threshold or
Recipe change.

## Question

The revisit must answer three questions at 2 fps
([handoff](../../60-evidence/s11/2026-10-26-step8-11-speed-handoff.md#next-the-user-decides-each-step)):
1. why SPL#4 22.5–27.0 s is `FILL_OWNER_AMBIGUOUS` between stationary owners;
2. how the rising level gets admitted (FFF-1, the association cap);
3. which phase owner the fast rise should have.

This record answers question 1 from source and the relayed rows. It then
checks locally whether an existing measure, the tracklet's recent motion,
separates owners that follow the level from owners that do not.

## Question 1 — the source reading (inference, no SPL#4 trace replay)

The SPL#4 bundles stay on Windows, so this joins the relayed rows to source.
It is not a frame-by-frame trace reading.

**The reason:** the lifecycle sets `FILL_OWNER_AMBIGUOUS` when more than one
dynamic fill owner exists, and empties the allowed set
([`oil_phase_lifecycle.py`](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py),
the last branch of the fill decision). On SPL#4 BASE the two owners are
`0025:0018` (Y781–785, then Y756–766) and `0042:0035` (Y742–769)
([follow-up receipt](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)).

**How two owners arise:**
1. **22.0 s:** the fill chain hands off 0018 → 0035 (selected Y756). The
   handoff removes 0018's chain (`_advance_fill_chains`).
2. **22.5 s:** 0018 reappears while 0035 also has an admitted upward row. No
   retained chain is free to receive 0018, because every retained chain has a
   row this frame. So 0018 starts a **new chain** at Y785, near the lower
   entrance.
3. **The new chain is dynamic at once.** Under an EMPTY initial state
   `_chain_is_dynamic_fill_owner` reads the confirmation profile, direction,
   net progress and directional agreement of each observation. For a
   CONTINUING tracklet these are copied from its confirmation witness and
   stay fixed for its life; only motion support and coverage are recomputed
   over the recent window (`oil_interface_tracklets.py`, the continuation
   loop). A chain also qualifies from **any** observation in its window.
4. **So two low, slowly moving rows both count as rising owners.** The level
   itself (Y463 and above) is only new provisional tracklets, never admitted.

**What it means:**
- The ambiguity is not a choice between two level candidates. Neither owner
  is the level. Picking one would publish wrong-target Oil, as the survivor
  did at 27.5–34.0 s (14 rows).
- It is the common factor FOA-1 named: a tracklet keeps fill ownership after
  it stops following the level (`S11-F04`, `S11-F05`).
- **Not answered here:** admission of the rising level (question 2). Any
  owner-validity change leaves FFF-1 open.

**An existing measure:** each tracklet row also carries recent-window values
(`tracklet_recent_direction`, `_recent_net_progress_px`,
`_recent_directional_agreement`). The lifecycle already uses them for the
initial-FULL drain release and the refill witness, but not for EMPTY fill
chains. Before any design uses them, the local fills show whether they
separate owners at the level from low owners.

**Caution, known before the run:** the FOA-1 desk reading found most low
owners rising in parallel with the level, and the user judged sample7's
owner 0016 correct (front and back arcs of one surface). A recent-motion
measure may not separate them.

## Method

- **Inputs:** FOA-1's run unchanged: sample5 and sample7, the frozen
  empty-fill Recipes, an EMPTY initial state, the IFO v2 + top-exit v3 arm,
  2 fps, debug NONE. Surface estimates from FOA-1's `surface-estimates.json`
  (agent estimates, written before any readout; not user truth).
- **Readout:** FOA-1's per-frame owner readout plus, per Oil candidate, the
  confirmation profile and the three recent-window fields. The resolver
  already writes them; the readout copies them only.
- **Identity gate:** rows and the FOA-1 readout fields must equal the kept
  FOA-1 `top_exit` variant. Otherwise nothing is interpreted.
- **Tool:** `tests/diagnostics/s11_fill_owner_recency.py`.

## Readings fixed before the run

**Recent-motion pass `P`** for a row: recent direction upward (< 0), recent
directional agreement ≥ 0.60, and recent net progress ≥ max(4, 0.025 H),
where H is the Glass ellipse height (sample5 12.85 px, sample7 15.15 px).
This is the predicate the lifecycle already applies to the refill witness,
without its span, entrance and material terms.

**Position:** offset = row Y − surface estimate. Level: |offset| ≤ 32 px.
Low: offset > 32 px. Above: offset < −32 px. Frames outside the estimate span
have no position.

Per video:
- **R1:** over the `FILL_OWNER_AMBIGUOUS` frames, every (frame, dynamic owner)
  pair: whether the owner has a row in the frame; if so, its fixed and recent
  fields, `P` and position.
- **R2:** the table `P` × position over owner rows with a position.
- **R3:** per ambiguous frame, the number of owners whose row passes `P`
  (0, 1, 2 or more).
- **R4 (sample5):** every published numeric Oil row more than 32 px below the
  surface (FOA-1 counted 21 after 9.0 s): the selected tracklet and its `P`.
- **R5 (sample7):** every published numeric Oil row of owner 0016 in
  22.0–31.5 s (user-judged correct): its `P`.

**Outcome:**
- **SEP:** on sample5, at least 75 % of low owner rows fail `P` and at least
  75 % of level owner rows pass it (or there are no level owner rows); and on
  sample7, at least 75 % of the R5 rows pass `P`. Recent motion is then a
  candidate owner-validity cue for the design.
- **NO-SEP:** on sample5, the `P` pass rate of low owner rows is within 25
  points of the level rows' rate. Recent motion does not separate them, and
  the design needs another cue.
- **MIXED:** anything else, described as found.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: SPL#4 2 fps 22.5–27.0 s is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` between two low owners, inferred from source and the relayed rows: a reappearing tracklet starts a new fill chain that is dynamic at once from its fixed confirmation fields. Upstream, the rising level is never an admitted `OIL-TRACKLET` owner (FFF-1).
- Existing feature coverage: reuses FOA-1's comparison inputs, frozen empty-fill Recipes, EMPTY initial state, the IFO v2 + top-exit v3 arm, the owner readout and the recent-window tracklet fields the resolver already writes. The recent-motion predicate is the lifecycle's existing refill-witness test, used here only as a reading.
- Execution scope: one local managed run on sample5 and sample7 at 2 fps with debug NONE, with an identity gate against the kept FOA-1 run. Agent surface estimates only; no Windows run, user review, tuning, flag or threshold change.
- Logic-map impact: NONE — diagnostics only; detector code and owners are unchanged.
- Failure-registry impact: NONE — the reading fits existing entries (`S11-F04` stale continuation, `S11-F05` EMPTY-phase ownership lock); `S11-F02` stays open.
