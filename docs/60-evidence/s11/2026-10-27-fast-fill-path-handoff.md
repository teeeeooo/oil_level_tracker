# S11 fast-fill path handoff — 2026-10-27 (session close)

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state
and authorization. Everything below is committed and pushed to `main`.

- **No production detector default changed.** E4, the contested gate,
  top-exit v3, IFO v2 and fast-rise association are opt-in and default OFF.
  FIELD FAIL / O2 OPEN and review-006 pending are unchanged.
- **Windows request queued (after compaction):** the read-only
  [FER-1 request](../../40-operations/s11-current-windows-field-qualification.md#fer-1-full-evidence-readout-request).
  Its readings were frozen at `b2280da`, and the local half is done
  ([FER-1](../../50-diagnostics/s11/2026-10-27-full-evidence-readout.md)).
- **Managed runs:** 145, all clean.
- **Next free review ID:** review-018.
- **The previous handoff,** the
  [fill-owner revisit handoff](2026-10-27-fill-owner-revisit-handoff.md),
  covers steps 12–15, reviews 015–016 and the E4 approval.

## What this session settled

The order the user chose was E4 → E2 → E1 → E3. The goal is FULL on fast
fills at 2 fps (SPL#4 BASE: Oil FULL 27.5–63 s).

| Step | Outcome | Record |
|---|---|---|
| E4, co-located fill owners | Implemented at `9ee11a4`, opt-in. Local FAIL on a frozen stop condition: sample5 events changed outside the predicted frames, and the user accepted that as a gain. **Windows SPL#4 PASS:** exactly 23.0 and 23.5 s publish Y781.0 and Y757.0, +13.0 and −4.5 px from the marks. Default OFF | [E4 evidence](2026-10-27-fill-owner-colocation-local.md) |
| E2, undercut fill owner | **PARKED** (user: "응 E2 보류하고 E1 설계 초안으로 넘어가자"). It does nothing on SPL#4: nothing admitted lies above 0018 at 27.0–34.5 s. By user truth it removes 4 wrong rows against 12 correct ones (sample7 9; SPL#1 Accum 3, review-017). Draft only, no code | [OAR-1](../../50-diagnostics/s11/2026-10-27-owner-above-readout.md) |
| E1, Foam-aware partition contradiction | **NOT VIABLE as drafted.** Every local post-track demotion rests on texture alone (2,057 rows). On SPL#4 25.5–27.0 s neither the ordered-lower scope nor the Foam-front scope frees the level, because the detector sees no Foam there from 24.0 s. On SPL#1 Accum a Foam scope frees 1,874–2,644 rows. Draft only, no code | [FPC-1](../../50-diagnostics/s11/2026-10-27-partition-contradiction-readout.md) |
| Path F, owner-free FULL | **REVIEW DRAFT** (OFF-1). It is the agent's recommendation after reading the review photos, and the user chose to draft it before the peer-side desk check | [OFF-1](../../50-diagnostics/s11/2026-10-27-owner-free-full-review.md) |

**Reviewed truth gained:**
- **Review-017:** SPL#1 Accum 669.0–672.0 s marks Y501/506/513/492/476/471
  and Y492.5, the last agreeing with review-012 within 1 px. The ordinary
  output at 669.5–671.5 s is correct.
- **SPL#4 Accum 65.0–67.0 s:** no Oil boundary; all Foam.

**User decisions, verbatim where they decide:**
- E4: "1번으로 진행하자. 범위 밖 변경이지만 오히려 신뢰도가 올라가는 변경으로 생각됨".
- E2: "review017 진행하고 확인해서 E2가 구현 할 의미가 있는지 한번 확인해보자",
  then "응 E2 보류하고 E1 설계 초안으로 넘어가자".
- E1 readout: "응 진행하자".
- Order and handoff: "그럼 이렇게하자 대화 세션 compact 한번 할때가 됐거든. 1번
  진행하고 handoff 작성하자. 그리고 compaction 후 handoff 확인하고
  이어가는걸로". Here "1번" means the OFF-1 review draft first and the
  peer-side desk check later.

**The agent's judgment, given at the user's request (2026-10-27):**
- In the SPL#4 review photos the level and the stale lower edge differ
  clearly to the eye. The difference is temporal: the level rises fast, and
  the lower edge stays still through FULL.
- The detector's frame-local rules invert it: they trust the clean static
  edge and distrust the textured moving level.
- So E1 and E2 have no handle. The clearest visual fact is the FULL state
  from 27.5 s, which favours path F.

## Next

1. **The user reviews [OFF-1](../../50-diagnostics/s11/2026-10-27-owner-free-full-review.md).**
   It covers:
   - candidate rule F1: ownerless FULL after an observed fill, with K
     samples of the existing `full` state node, no interface and no Foam;
   - its risks: `S11-F05`, `S11-F06`, `S11-F07` and `S11-F10`. The main one
     is a Glass full of Foam (SPL#4 Accum);
   - three open questions: K, the stale low owner's rows, and the report
     label.
2. **If the user agrees,** build a read-only FULL evidence readout and freeze
   it before its output. It reads gate 1 first: whether the raw frame
   outcome is no-interface, since the `full` node exists only then
   ([OFF-1 correction](../../50-diagnostics/s11/2026-10-27-owner-free-full-review.md#correction-after-compaction-an-earlier-gate-source-desk-check-2026-10-27)).
   Then it reads per frame the `full` and `empty`
   likelihoods (presence first; an older trace lacked them), the phase and
   reason, the `full` node and its fate in `_constrain_layer`, Foam fronts
   and admitted rows.
   - **Windows:** SPL#4 BASE 20–70 s, SPL#4 Accum 20–90 s, SPL#1 BASE and
     Accum 650–700 s.
   - **Local:** the six fill-owner controls.
3. **Fallback if path F is blocked:** the peer-side desk check of barrier 1.
   It reads the kept FPC-1 local JSON and the relayed SPL#4 peers to see
   whether a peer-side condition separates SPL#4 from sample4's R7 rows. It
   is the first piece of E3.

## Tools added this session (read-only diagnostics)

- `tests/diagnostics/s11_owner_above_readout.py`: OAR-1, the E2 cue. It
  reads comparison files or FULL-debug bundles.
- `tests/diagnostics/s11_partition_contradiction_readout.py`: FPC-1, the E1
  scopes. Its `local` mode runs a control through the comparison runner;
  its `bundle` mode reads a trace.

**Trace lesson:** a trace record's top-level `candidates` are written before
sequence resolution. Resolved tiers, opposition, identity and tracklets live
in `record["sequence"]["candidates"]`. Join them on (kind, source, canonical
Y), as FPC-1's `merge_record` does. The first E1 relay was void for this
reason.

## Working rules confirmed this session

- **Freeze every design and its checks before code.** No tuning after
  results, and no edits to frozen criteria.
- **Event and retrospective changes** that follow from changed rows are
  listed and read, not frozen stop conditions. E4's stop fired on exactly
  this.
- **Before freezing,** read the user's case on Windows with a read-only
  readout. Both E2 and E1 failed on SPL#4 only at that step.
- **Windows relays are text with OCR slips** (`0`/`8`, `b`/`8`). Identify
  runs by run_id and counts. Keep relays and photos in closed managed runs
  under `sample/output/`.
- **Commit and push in logical units without asking.** The user decides each
  step.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: SPL#4 BASE 2 fps fast fill. `OIL-AUTHORITY` demotes the level at 25.5–27.0 s; `OIL-TRACKLET` caps the association; `OIL-PHASE-FILL` holds a stale owner and then an ownerless episode that reduces any `full` node to UNKNOWN.
- Existing feature coverage: E4 (implemented, opt-in), the E2 and E1 drafts (no code), the contested gate, top-exit v3, IFO v2 and fast-rise association, all default OFF.
- Execution scope: a handoff; no run, code or Windows execution in this record.
- Logic-map impact: NONE — a handoff.
- Failure-registry impact: NONE — no new mechanism.
