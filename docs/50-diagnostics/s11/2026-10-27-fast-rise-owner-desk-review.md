# FOR-2 — the rising level above the fill owners: admission and phase owner

**Status: IN PROGRESS 2026-10-27.** Step 2 of the fill-owner gate revisit in
the [Work Plan](../../00-project/work-plan.md): the questions-2/3 desk review
(A). The user chose (2026-10-27, "그렇게하자") to send review-015 to Windows
first and run this desk review from existing records while it is out. No
design is frozen before review-015 is read. Diagnostics only: no detector,
flag, threshold or Recipe change.

## Question

The revisit's questions 2 and 3 at 2 fps
([handoff](../../60-evidence/s11/2026-10-26-step8-11-speed-handoff.md#next-the-user-decides-each-step)):
- **2.** How does the rising level get admitted? (FFF-1: the association cap
  of 32 px per 2 fps sample refuses SPL#4's fast rise.)
- **3.** Which phase owner should the fast rise have?

**Starting point** ([FOR-1](2026-10-27-fill-owner-recency-local.md),
[step-12 receipt](../../60-evidence/s11/2026-10-27-step12-windows-receipt.md)):
- SPL#4 BASE 22.5–27.0 s is `FILL_OWNER_AMBIGUOUS` between a reappearing 0018
  chain on fixed fields from a confirmation that ended at 14.5 s and a freshly
  confirmed rising 0035 (22.0–24.5 s). Both rise in the window.
- An owner's own motion does not separate a low owner from the level (NO-SEP).
  The remaining cue is relational: a higher rising interface above the owners
  (inference).
- **Open premise:** no reviewed frame says where the level is in 20–27 s.
  The user's timeline gives only "FULL reached at 24–25 s". Whether 0035 is
  the level in 22.0–24.5 s, and whether the higher provisional rows (Y463 at
  22.5 s; Y462, Y534, Y651–660 at 24.5 s) are the level, is not reviewed.

## Review-015 — readings frozen 2026-10-27, before its output

**Purpose:** test the relational premise on SPL#4 before any design builds on
it. The user marks the Oil surface on a raw zoom (no detector value is drawn).
The marks are compared on the Mac with the candidate Ys already relayed.

**Material:** SPL#4 BASE, 20.0–27.0 s at 2 fps, 15 panels, source frames 600,
615, …, 810 (the step-12 rows). Video `SPL#4_Cooling_onoff_#2.mp4`
(53,165,455 bytes); Recipe = the `SPL4_B_ref` bundle's
`recipe_snapshot.oilrecipe`, Glass BASE. Tool
`tests/diagnostics/s11_review_zoom.py` (`prepare`, then `read-marks`).

**Mark Y:** a panel's mark Y is the median of its mark Ys. A panel with no
mark, or the user's "가득" or "안 보임", has no mark Y; "가득" is counted
separately. "Near" means within 32 px (FOA-1's distance unit).

**Candidate Ys compared** (as relayed; OCR):
- owners, from the step-12 readout: 0018 and 0035 rows in 22.0–27.0 s;
- higher candidates, from the
  [SPL#4 follow-up](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22):
  Y463 at 22.5 s; Y462, Y534 and Y651–660 at 24.5 s; Y323–325 (`…0034`)
  from 22.0 s.

**Readings:**
- **K1, owner position:** each 0018 and 0035 row in 22.0–27.0 s on a panel
  with a mark Y is *level* (its candidate Y nearest the mark Y is within 32 px of it), *low* (more
  than 32 px below) or *above*.
- **K2, the premise:** in each of the 10 ambiguous panels (22.5–27.0 s), the
  mark Y is more than 32 px above every owner row of that frame, or the user
  says "가득".
- **K3, higher candidates:** at 22.5 s and 24.5 s, which higher candidate is
  near the mark Y, if any.
- **K4, timeline:** the first "가득" panel, against the timeline's 24–25 s.
  Reported only.

**Outcome:**
- **UNREADABLE:** fewer than 5 of the 10 ambiguous panels have a mark Y or
  "가득". The desk review proceeds on the timeline alone, and this is named.
- **ABOVE:** otherwise, if K2 holds in every ambiguous panel that has a
  mark Y or "가득", and no K1 row is level. The relational premise holds on
  SPL#4.
- **OWNER-LEVEL:** otherwise. The premise fails for the named frames: the
  design may not prefer a higher interface over that owner there.

## Desk review

Pending (this session, from existing records).

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: SPL#4 2 fps 22.5–27.0 s is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` (step 12); upstream, the rising level is not an admitted `OIL-TRACKLET` owner (FFF-1, inferred). Review-015 tests where the level is.
- Existing feature coverage: reuses the saved step-7 `SPL4_B_ref` bundle and its Recipe snapshot, the relayed step-12 and follow-up candidate Ys, and the existing raw review zoom; no detector option is exercised.
- Execution scope: one human review on Windows (review-015, user-forwarded) and a Mac desk review of existing records; no detector run, tuning, flag or threshold change.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — no new mechanism.
