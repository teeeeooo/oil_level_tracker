# DSR-1 — D scope review: Accum entry, post-Foam and drain gaps, with the stale fill owner

**Status: DESK REVIEW COMPLETE 2026-10-22; the first sub-scope awaits the
user's choice.** Step 3 of the Mac-only order in the
[Work Plan](../../00-project/work-plan.md), approved by the user on 2026-10-22.
Existing records only: no run, detector change or Windows request.

## What D covers

The Work Plan's open field risks name Accum entry, layered/post-Foam continuity
and drain re-entry as unrepaired. The layered-Foam interval belongs to B
(LBT-2). D takes the rest of Accum on SPL#1, plus the stale-owner wrong target
(나) that the
[SPL#4 follow-up](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)
and [FOA-1](2026-10-22-fill-owner-ambiguity-local.md) found.

## Accum on SPL#1 today

The ⑩ output (the
[⑩ interval table](../../60-evidence/s11/2026-10-21-top-exit-v3-local.md)).
Its Accum rows equal ④'s, and its 22 drain rows match R20. Row counts are
about 2 per second.

| Truth segment | Rows | Numeric Oil | What blocks it, as far as known | Owner of the question |
|---|---:|---:|---|---|
| `WS1-ACCUM-EMPTY`, 480–653 s | ~347 | 0, correct | Published UNKNOWN, not EMPTY: the reconstruction stays `UNRESOLVED` behind the Foam barrier | E3, not D |
| `WS1-ACCUM-ENTRY-SPLASH`, 653–672 s | ~39 | 4 | Not read on the current detector. R20 also published 7 Foam rows here, where Foam must be absent. Truth rejects splash and wall marks as the Oil owner | **D** |
| `WS1-ACCUM-FOAM-LAYERED`, 672–680 s | ~17 | 10 | Role errors: the Foam top or interior is published ([ATG-1](2026-10-20-accum-texture-gate.md#decision), [review-010](2026-10-20-approach-review.md#review-010-result)) | B (LBT-2) |
| Collapse onset, 678.5–680 s | — | — | 678.5 s: the air–liquid top is present and anchored, yet another row is published. 679 s: nothing. At 679.0 s the R18-era [D1 readout](../../60-evidence/s11/2026-10-08-next-work-intake.md#consistent-named-candidate-statements-in-the-return) (review-003) allowed only the fill owner 0181 and excluded ten admitted rows owned by other tracklets (`OWNER_NOT_ALLOWED`, for example idx19). The reviewed interface idx10 (Y217) was lost earlier, before the retained refs | B and D |
| `WS1-ACCUM-POST-FOAM`, 680–700 s | ~41 | 0 | Tracklet association ambiguity near the level. The ⑩ census finds `INCOMPATIBLE_BRANCH` blanks from 679.5 s, with in-band runs at 679.5–682.5 and 697.5–701.5 s. A branch that two tracks or two rows contest ends the track and is never admitted. [ARV-1](2026-10-20-approach-review.md#split-the-problem-by-foam-state) lists the segment as not studied | **D** |
| `WS1-ACCUM-DRAIN`, 700–780 s | ~161 | 22, all in 711.0–724.0 s, unchanged since R20 | `S11-F08`: Accum partial release is the narrowed owner, and R17 had no Oil here. The census blanks continue to 736.5 s. The 22 rows' accuracy was never evaluated | **D** |

## The stale fill owner across recordings

| Recording | Where | What the owner did | Source |
|---|---|---|---|
| SPL#4 BASE (Windows) | 27.5–34.0 s | Re-adopted low owner 0018 published 14 rows (Y704–739) inside the reviewed FULL interval | SPL#4 follow-up |
| sample5 (local) | 20.0–54.5 s | Re-adopted low owners published 21 rows, 54–226 px below the level | FOA-1 |
| sample7 (local) | 10.0–21.5 s | A low owner competed with the level owner, so the frames went UNKNOWN; afterwards 0016 published 25–68 px below the froth top | FOA-1 |
| SPL#1 Accum (Windows, R18-era) | 679.0 s | The allowed set held only the fill owner 0181, and ten admitted rows of other tracklets were excluded. The reviewed interface was lost before that filter, so this record does not show the owner removing the level | D1 review-003 |

**The mechanism**, from FOA-1:
- Fill ownership qualifies from any past observation and is extended by any
  admitted upward row. A tracklet that stopped following the level therefore
  keeps ownership while it is seen.
- Under an EMPTY initial state only chains starting in the lower entrance
  qualify. A level re-acquired mid-glass, such as sample5's 0059/0060, is
  admitted but cannot become an owner.

Both points come from source reading and the readout; the design step must
verify them.

The SPL#1 Accum row is from an older detector and has not been re-read since.
So on SPL#1 the stale owner is a hypothesis: Accum entry runs through the same
EMPTY-initial fill ownership (inference), and no current record shows it there.

## Options for the first sub-scope

| # | Sub-scope | Gap it targets | Local case | Windows needed first? | Main risk |
|---|---|---|---|---|---|
| 1 | **Fill-owner validity:** a fill owner keeps ownership only while it follows the level | (나) wrong target (SPL#4, sample5); possibly Accum entry (unshown) | sample5 (decisive), sample7 | No. Windows checks come after: SPL#4 27.5–34 s, SPL#1 Accum 653–682 s | `S11-F05`/`S11-F08`: losing a real owner, or a new false owner. Controls must show neither |
| 2 | **Post-Foam association ambiguity** | Accum 680–700 s (0 of ~41) | None known | Yes: which hypotheses contest the branch near the level | `S11-F04`: relaxing association merges components |
| 3 | **Accum drain release** | Accum 700–780 s (22 of ~161) | None known | Yes: the release evaluations, and a review of the 22 rows | `S11-F08` |

## Recommendation

**Option 1 first.**
- **False output:** it removes numeric Oil on a wrong target. The product
  treats that as worse than UNKNOWN (fail closed).
- **Local cases:** it is the only D sub-scope with them, so it can proceed
  while Windows is unavailable.
- **Accum coverage:** the same mechanism may also block Accum entry. No current
  record shows it there; the step-7 request would check it.
- **Options 2 and 3** need Windows readouts first. Their extraction items join
  the step-7 request:
  - Accum 680–700 s: per frame, the contested hypotheses near the band, and
    which track ended as `AMBIGUOUS_BRANCH`;
  - Accum 700–780 s: the DRAIN release evaluations, and a human check of the
    22 rows.

**Order:** option 1 is the (나) half of step 6. Doing it next, before E3 and B,
would put the largest locally testable correction first. Its design must be
frozen before any code change. B's sample4 baseline may then shift; B would
develop on top of it. Keeping the original order (E3, then B, then step 6) is
equally valid. The user decides.

**Later (2026-10-22):** the user chose option 1 first.
- **Changed form:** a desk reading showed that motion does not separate the
  owners. Option 1 therefore became the
  [contested fill-owner gate](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate),
  frozen before implementation as an opt-in comparison.
- **sample7 corrected:** its "low owner" is the front arc of the same,
  obliquely viewed surface (user judgment), not a stale owner.
- **Cost:** locally the gate removes 17 wrong sample5 rows and 20 correct
  sample7 rows. The user accepted this because product videos are mostly
  head-on.
- **sample4:** it never reports `FILL_OWNER_AMBIGUOUS`, so B's baseline should
  not move.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: per segment. Accum entry: unknown on the current detector. Collapse onset: the selector publishes another row although the target is anchored (678.5 s); in the R18-era readout the reviewed interface was lost before the retained refs (679.0 s). Post-Foam: `OIL-TRACKLET` association ambiguity near the level. Drain: `OIL-PHASE-DRAIN` partial release (F08). Stale owner: `OIL-PHASE-FILL` ownership (FOA-1, SPL#4).
- Existing feature coverage: reuses the reviewed SPL#1 truth segments, the ⑩ interval counts, the ⑩ census, the closed D1 readout, ARV-1 and review-010, the F08 entry and FOA-1. No new extraction, run or Recipe use.
- Execution scope: desk review of committed records; no run, Windows request, tuning, flag or threshold change. A later note (2026-10-22) records the step-6 outcome and the user's sample7 judgment; no run.
- Logic-map impact: NONE — review only; detector code and owners are unchanged.
- Failure-registry impact: NONE — every gap maps to an existing entry (F04, F05, F08); no new mechanism or failure.
