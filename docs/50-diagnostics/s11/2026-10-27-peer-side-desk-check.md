# PSD-1 — does a peer-side condition free SPL#4's demoted level? (barrier 1 desk check)

**Status: READINGS FROZEN 2026-10-27, before the local rows are read.** This
is the peer-side desk check of barrier 1, the first piece of E3. It runs on
the user's "1번 먼저 진행하자" (2026-10-27), after
[FER-1](2026-10-27-full-evidence-readout.md) read E-ABSENT for path F. It is
a desk reading of kept data: no run, no Windows request, no detector change.

## The rule and the question

The same-frame superior-partition rule (`_apply_track_opposition`,
[`oil_observation_resolver.py:721`](../../../src/oil_tracker/adapters/vision/oil_observation_resolver.py))
demotes a row to `CANDIDATE_ONLY` with opposition 0.80 when both hold:
- **A peer exists:** a material path with terminal support ≥ 0.60, layer
  topology < 0.5, at least 8 px away, and of comparable local quality.
- **The row has a local contradiction** (`recurrence_hard_contradiction`).

The rule does not look at where the peer lies: above or below, near or far.

**R7 added it** to keep sample4's visually rejected lower-rim and
internal-partition rows (2.5–35.5 s) non-numeric
([partition demotion desk review](2026-10-27-fast-rise-owner-desk-review.md#partition-demotion-desk-review--2026-10-27)).

**On SPL#4 BASE at 25.5–27.0 s it demotes the rising level.** The listed peers
are the stale owner's lower boundary (0018, Y715–721) and untracked rows at
Y693–705, all 165–330 px below the level. A few rows of the level band itself,
8–11 px apart, are also listed (E1 rerun relay).

**Question:** is there a condition on the peer's position that holds for
SPL#4's level rows and not for the rows R7 protects?

## Data

- **SPL#4 BASE 25.5–27.0 s:** the 14 demoted rows within 32 px of the
  review-015 marks, with their listed peers. They come from the
  [E1 rerun relay](2026-10-27-partition-contradiction-readout.md#windows-readout--2026-10-27-rerun),
  kept in `s11-e1-windows-relay-20261027-001`.
- **SPL#1 Accum 669–678 s:** the demoted rows near the review-017 and
  review-012 marks, from the same relay.
- **Local:** the six controls' demoted rows with their listed peers, from the
  FPC-1 JSON kept in `s11-e1-partition-readout-20261027-001`.

**Limit: the peer set is a superset.**
- The listed peers meet every condition of the rule except the comparable
  local quality, which is not traced.
- So which peer actually demoted a row is not known.
- A condition is therefore read as holding only if it holds for **every**
  listed peer of the row.
- A row with no listed peer cannot have been demoted by this rule. Its
  demotion is a recurring-track one, so it is left out.

## Candidate conditions (frozen)

| ID | The row is exempt when … |
|---|---|
| C1 | every listed peer lies at least 64 px below the row (two association steps) |
| C2 | every listed peer lies below the row: the row is above all its partition peers |
| C3 | after ignoring peers within 16 px (the row's own band), at least one peer remains and every remaining peer lies at least 64 px below the row |

**Disclosure.** C2 and C3 were written after seeing the SPL#4 peer lists in
the relay.
- On those 14 rows C2 and C3 hold by construction. C1 fails at 25.5 s and
  26.0 s, because the level's own sibling rows are listed as peers.
- **So SPL#4 is not the test.** The test is the local rows, which have not
  been read for this question, and the SPL#1 Accum rows.

## Frozen readings

**Protected set P:**
- every demoted row with a listed peer on sample4-original and
  sample4-interior at 2.5–35.5 s, R7's protected span;
- sample7's fixed structure row Y380–388, which is in every frame from 35 s
  (FPC-1).

| Reading | Condition |
|---|---|
| **SEPARATES** | Some condition exempts all 14 SPL#4 rows and **no** row of P. Its other local exemptions are listed and read against the FOA-1 surface estimates (sample5/7) |
| **NO SEPARATION** | Every condition exempts at least one row of P |

**What each reading leads to (agreed before reading):**
- **SEPARATES:** the condition becomes the barrier-1 candidate of E3. It
  frees authority only. Barrier 2 (the 32 px association cap) and barrier 3
  (the fill-chain handoff) still block the level, so no row changes from it
  alone. This is reported, and the user decides on E3.
- **NO SEPARATION:** barrier 1 has no peer-side handle in the traced fields.
  E3 is blocked at its first barrier, which leaves path F with new FULL
  evidence. This is reported, and the user decides.

**Information:** the SPL#1 Accum mark-near rows each condition exempts.
- Rows within 10 px of a mark count as possible gains.
- Rows farther away are listed.
- The Foam-layer rows (142–187 px above the marks) were relayed without
  peers, so their exposure is **not readable** here.

No condition is tuned after reading.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`
- First harmful stage: `OIL-AUTHORITY` superior-partition demotion of SPL#4's rising level at 25.5–27.0 s; its listed peers are the stale owner's lower boundary 165–330 px below.
- Existing feature coverage: the same-frame superior-partition rule (R7) with R14's contradiction condition, as traced in the FPC-1 local JSON (reference arm: IFO v2 + top-exit v3, six controls) and the E1 rerun relay of the step-7 reference bundles; no option is exercised.
- Execution scope: a desk reading of kept local JSON and kept relayed text; no run, no Windows request, no code change.
- Logic-map impact: NONE — a desk check.
- Failure-registry impact: NONE — no new mechanism.
