# FOR-2 — the rising level above the fill owners: admission and phase owner

**Status: IN PROGRESS 2026-10-27 (desk review written; waits for review-015).** Step 2 of the fill-owner gate revisit in
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

## Desk review — 2026-10-27, from existing records

### Where a fast rise is lost: two capped layers (source)

1. **`OIL-TRACKLET`** (FFF-1): a row extends a tracklet only within
   `temporal_max_jump_px` × gap (32 px per 2 fps sample on SPL#4). Beyond it,
   each row starts a new provisional tracklet that fails with
   `INSUFFICIENT_NET_PROGRESS` (27.2 px within the 6-frame window).
2. **`OIL-PHASE-FILL`** (new reading here):
   - `_advance_fill_chains` takes only admitted, upward rows.
   - A chain hands off to a new tracklet only within the same cap
     (`_compatible_handoff`: |Δy| ≤ `maximum_jump_px` × gap). The lifecycle's
     `maximum_lost_frames` is 3, so a handoff can bridge at most 4 samples,
     128 px.
   - FULL (`FILL_SPAN_CONFIRMED`) needs a chain of at least 3 observations
     whose last row is in the top band and which spans at least 20 % of the
     height (`_fill_confirmation_profile`). On SPL#4 BASE that means Y ≤ 437.9
     and a span of 108.7 px.

**So admission alone is not enough (inference).** A rise admitted at the
tracklet layer would still be linked into a fill chain at no more than 32 px
per sample. Any fix must carry the rise through both layers. This matches
step 10, where phase was a barrier at 6 fps as well.

### What is on record for SPL#4 BASE 20–27 s (no reviewed level yet)

| Family | Rows | Source |
|---|---|---|
| Three stacked rows about 50 px apart | `0025:0018` Y801–802 (20.5–21.5 s); `0042:0035` Y740–758 (21.0–23.0 s); `0025:0016` Y702–703.5 (20.5–22.5 s) | step 8 |
| The two owners, rising in the ambiguity | 0018 Y785 → Y704–714 (22.5–27.0 s); 0035 Y742–753 → Y708 (22.5–25.0 s), freshly confirmed 22.0–24.5 s | step 12 |
| Higher rows, never admitted | Y463 (22.5 s); Y462, Y534, Y651–660 (24.5 s); each a new provisional tracklet | follow-up |
| A fixed row near the top | Y323–325 (`…0034`) from 22.0 s, never admitted; at 6 fps `0057` reaches Y323 by 21.3 s | follow-up, step 10 |
| The user's timeline | Oil from about 11 s; FULL reached at 24–25 s | entry conditions |

Two pictures fit these rows, and they conflict:
- **P1, the level is above the owners.** It leaves about Y800 near 21.5 s
  and reaches the top band by 24–25 s, which is more than 360 px in about
  3 s. The higher rows are the level seen once each. The stacked rows are
  other features: foam layers or structure (inference).
- **P2, an owner is the level.** For example, 0035 rises 39 px over
  22.0–24.5 s. This conflicts with the timeline's FULL at 24–25 s unless the
  timeline is off by seconds.

Review-015 tells them apart: ABOVE supports P1, and OWNER-LEVEL supports P2
for the named frames.

### Directions by outcome (for the user's choice; nothing decided)

**If ABOVE (P1):** question 3's answer is that no current owner may hold the
fill during the rise. Three directions remain; each reuses an existing
owner:

| Direction | What it changes | What it gains | Main risk |
|---|---|---|---|
| D1, ownerless fast rise (`OIL-PHASE-FILL`) | While rising rows exist above every dynamic owner, the fill phase publishes no owner (fail closed) instead of the stale owner | removes wrong-target rows such as the 14 at 27.5–34.0 s, using a cue that names a reason (the contested gate only marks outlasting) | sample7's front arc, likely the same cost as the gate (inference); no FULL by itself |
| D2, chain-level sweep (`OIL-PHASE-FILL`, with `OIL-TRACKLET` rows as input) | The fill chain may link unadmitted rows above the owners across samples when they form a monotone rise with material evidence, bounded by the geometry | FULL through the existing top-band `FILL_SPAN_CONFIRMED` | `S11-F03`/`S11-F04`: motion or recurring Y used as identity; step 8 showed geometric triplets can stitch stacked rows |
| D3, owner-free FULL (FFF-1 option 3) | FULL from a bounded bottom-to-top sweep and an interface-free top, with no owner | FULL without identity | `S11-F05`, `S11-F06`/`S11-F07` (Foam racing up looks like a sweep), `S11-F10` |

- **Not reopened:** densification and a higher rate (user, 2026-10-26),
  option 4 (rejected), and the fast-rise seed witness (0 qualifying on SPL#4;
  no retuning).
- **D1 composes with D2 or D3.** D1 alone does not reach FULL, which the user
  requires for fast fills, so it is a first step, not an answer.
- **D2 is testable only against the marks:** do the higher rows follow the
  review-015 marks frame by frame? Today only one or two such rows are on
  record per frame (22.5 s and 24.5 s).

**If OWNER-LEVEL (P2, for the named frames):** the relational cue is wrong
there. The ambiguity is then a true level (for example 0035) against a stale
chain (0018). The question becomes how to retire a reappearing chain that
carries fixed fields from an old confirmation. FOR-1's recency test does not
retire it: 0018 passes `P` in 7 of its 8 ambiguous rows. The timeline
conflict goes back to the user.

**If UNREADABLE:** the choice goes to the user on the timeline alone.

### What the review-015 reply needs next (any outcome)

- **Candidate coverage at the marks.** For D2, each mark needs a candidate row
  near it in that frame. The relayed records list the higher rows only at
  22.5 s and 24.5 s, so per-frame coverage near the marks is not on record.
- **A read-only Windows readout would supply it.** The existing
  `s11_fast_rise_readout.py` or `s11_fill_owner_trace_readout.py` on
  `SPL4_B_ref` can list every Oil candidate per frame, with no new run.
- **It is frozen after the marks are known** and judged against them. It is
  not requested before review-015 returns.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: SPL#4 2 fps 22.5–27.0 s is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` (step 12); upstream, the rising level is not an admitted `OIL-TRACKLET` owner (FFF-1, inferred). Review-015 tests where the level is.
- Existing feature coverage: reuses the saved step-7 `SPL4_B_ref` bundle and its Recipe snapshot, the relayed step-12 and follow-up candidate Ys, and the existing raw review zoom; no detector option is exercised.
- Execution scope: one human review on Windows (review-015, user-forwarded) and a Mac desk review of existing records; no detector run, tuning, flag or threshold change.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — no new mechanism.
