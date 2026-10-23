# SBD-1 — sample4 early drop at 54.0–54.5 s under the strict Oil boundary

**Status: DESK REVIEW COMPLETE 2026-10-23 (read-only replay, stdout only);
the user decides the next step.** Asked by the user on 2026-10-23 while the
[step-7 Windows request](../../40-operations/s11-current-windows-field-qualification.md#step-7-combined-request)
runs. No detector, flag, Recipe or truth change.

## Question

Under the strict rule, the
[review-014 result](2026-10-22-layer-bottom-topology-2.md#review-014-result--2026-10-23)
places the sample4 Oil boundary near Y831–836 through 54.5 s and at the Foam
region's bottom (Y854–858) from 55.0 s. Both baseline arms leave it one sample
early: the ordinary arm publishes nothing at 54.0 s and Y851 at 54.5 s; the
LBT-2 arm publishes Y844 at 54.0 s. Which stage moves the output first?

**Reference confidence (user):** the dense boundary is clear through 53.5 s,
breaks up from 54 s, and is not visible from 55 s. So 54.0–54.5 s is an
ambiguous transition, not a decisive error.

## Method

- **Input:** the saved P5 sample4 capture (`s11-p5-default-linkage-20261011-001`,
  `raw.json`) and its Recipe snapshot, replayed through
  `ObservationSequenceResolver` by the existing SOI entry
  (`tests.diagnostics.s11_single_observation_influence.execute`). This is the
  LBT-2 ordinary arm; it reproduces the recorded values at 52.0–56.0 s
  (Y833, 829, 829, 833, none, 851, 851, 852, 851).
- **Read:** every candidate's tracklet, lifecycle, authority and identity
  features at 50.0–56.0 s, and the decision witness at 54.0–54.5 s.
- **Oracle edits, diagnostic only (not candidate fixes):** at 54.0 s only,
  (A) the Foam front candidate moved to its neighbours' Y813; (B) the Oil rows
  at Y840–856 made ineligible; and A+B.
- **Storage:** scratch scripts with stdout only; no managed run or kept output.

## Findings

**Tracklets around the drop (ordinary arm):**

| Time | Level tracklet `0021` | Lower tracklet `0023` | Published |
|---|---|---|---|
| 50.0–53.0 s | Y822–839, continuation | Y880–886 (lower structure), intermittent | `0021` from 52.0 s (none at 50.0–51.5 s) |
| 53.5 s | Y830/833 | none (lost) | Y833 (`0021`) |
| 54.0 s | **none** | **Y844/852, confirmed** | none |
| 54.5 s | Y818/820 (inside the Foam) | Y851/852, ordered lower interface | Y851 (`0023`) |
| 55.0–56.0 s | Y829 at 55.0 s | Y851–854 | Y851–852 (`0023`) |

**Three events in the 54.0–54.5 s step:**

1. **The Foam front candidate drops onto the Foam bottom (54.0 s).** Its Y833
   equals the Foam component's bottom (`material_component_bottom_y` 833); at
   53.5 and 54.5 s the front is Y813/808 above a bottom at Y835/834. The
   2026-10-09 reply already calls Y833 at 54.0 s internal Foam texture, not the
   front. The level rows then lie above the front: Y830 loses
   `ordered_lower`, gains Foam identity 0.4 and a texture-conflict failure, and
   the Y828 rows stay outside top-K. `0021` gets no observation. The Foam front
   itself is not published (temporal pending).
2. **The lower-structure tracklet re-associates upward (54.0 s).** `0023`
   followed rows at Y880–886, missed 53.5 s, then linked 29–37 px upward to the
   newly strong rows Y844/852 and became confirmed. Y851–852 is the rough
   boundary (the clear-oil top), which turns into a strong edge as the dense
   boundary breaks up.
3. **The strict row is not tracked at 54.5 s.** Rows at Y828–829 exist (the
   strict mark is Y833.9–835.7): Y829 is `material_layer_terminal` without a
   tracklet, and Y828 is outside top-K. `0021` associates to Y818/820 inside the
   Foam instead. `0023` at Y851 is the ordered lower interface and is
   published.

**Oracle edits (ordinary arm, 53.5–56.0 s):**

| Edit at 54.0 s | 54.0 | 54.5 | 55.0 | 55.5 | 56.0 |
|---|---|---|---|---|---|
| none | none | Y851 `0023` | Y851 | Y852 | Y851 |
| A, Foam front at Y813 | none (`0021` gets Y828) | Y851 `0023` | Y851 | Y852 | Y851 |
| B, rows Y840–856 out | none | Y851 **`0026`** (new) | Y851 | Y852 | Y851 |
| A + B | **Y828** `0021` | Y818 | Y829 | Y852 | Y873 |

- **No single stage explains the step.** Removing the Foam front error alone
  changes no output. Removing `0023`'s rows lets a new tracklet take the same
  Y851 row.
- **Keeping the level tracklet does not track the strict boundary.** With both
  edits, 54.0 s is right under strict (Y828 against Y831.1–831.6), but 54.5 s
  (Y818), 55.0 s (Y829) and 56.0 s (Y873) are wrong. These match LBT-2's two
  54.0 s withdrawal conditions.
- **Reading:** from 54.0 s the rough boundary Y851 is the strongest ordered
  lower row, and the current evidence has no tracked strict row through the
  breakup. The output switch is the detector's response to the same breakup
  the user sees, one sample early.

## Options for the user

1. **Record and close (recommended).** Treat 54.0–54.5 s as an ambiguous
   transition. The ordinary arm already fails closed at 54.0 s; 54.5 s is
   15–17 px from an approximate mark. Keep the three events as named limits;
   no detector work.
2. **Fail closed during an identity transfer.** Abstain while the publishing
   tracklet has just re-associated across a lost frame onto a new row
   (`S11-F04`). Event 2 makes this plausible, but edit B shows a fresh
   tracklet claiming Y851 the next sample, so it would need its own frozen
   design and controls.
3. **Track the strict boundary through the breakup.** Under the strict rule
   the dense-Foam bottom is the Oil target, and the detector already marks it
   (`material_layer_terminal`, the Foam component bottom). Giving it Oil
   authority would be a larger design change across `FOAM-IDENTITY` and
   `OIL-AUTHORITY` (`S11-F06`), with sample4 52–56 s as its only local case.

Separately, event 1 is a Foam front error (front placed at the component
bottom) that changes Oil authority in the same frame (`S11-F06`), although
here it changes no output.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`
- First harmful stage: no single stage. At 54.0 s `FOAM-CANDIDATE` places the Foam front at the Foam component bottom and `FOAM-IDENTITY`/`OIL-AUTHORITY` demote the level rows (`S11-F06`), while `OIL-TRACKLET` re-associates a lower-structure tracklet 29–37 px upward onto the rough boundary (`S11-F04`); at 54.5 s the strict row is untracked (`S11-F02`) and `OIL-SELECTOR` publishes the ordered lower interface. Oracle edits show neither 54.0 s event alone changes the output.
- Existing feature coverage: the saved P5 sample4 capture and Recipe snapshot (the LBT-2 ordinary arm), the existing SOI replay entry and the resolver's own candidate features and decision witness; the review-014 references and the 2026-10-09 Foam-texture labels. Top-exit, the fill-owner gate, LBT-1/LBT-2 consumers and Windows data are not involved.
- Execution scope: read-only replays of the saved capture through the SOI entry with scratch scripts, stdout only, including three oracle edits at one frame for diagnosis; no managed run, kept output, detector change, tuning or Windows run.
- Logic-map impact: NONE — diagnosis only; no owner or edge changes.
- Failure-registry impact: NONE — the events map to existing entries (`S11-F02`, `S11-F04`, `S11-F06`); no new mechanism is claimed.
