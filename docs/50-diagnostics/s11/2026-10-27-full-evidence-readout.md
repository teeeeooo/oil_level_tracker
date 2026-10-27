# FER-1 — where does the image FULL evidence stop? (path F readout)

**Status: COMPLETE 2026-10-27. R1 = E-ABSENT.** The readings were frozen at
`b2280da`, before any output. Then came the
[local run](#local-result--2026-10-27) and the
[Windows readout](#windows-readout--2026-10-27).
- **SPL#4 BASE 27.5–63.0 s has no `full` node in any of its 72 rows.**
- **There is no `full` node anywhere:** none in the 1,564 Windows rows (both
  recordings, both Glasses) and none in the 532 local rows.
- **By the frozen consequence,** F1 as drafted has no existing evidence on the
  user's case. Path F would need new FULL evidence.
This is the read-only readout that
[OFF-1](2026-10-27-owner-free-full-review.md#what-must-be-read-before-any-design-proposed-readout-not-frozen)
proposes, run on the user's "시작하자" (2026-10-27). It changes no detector,
flag, threshold or Recipe.

## Question

Path F (OFF-1's candidate F1) would publish an ownerless FULL from the
existing per-frame `full` state node. The
[OFF-1 correction](2026-10-27-owner-free-full-review.md#correction-after-compaction-an-earlier-gate-source-desk-check-2026-10-27)
found that this node is gated three times before selection:
1. **Gate 1:** the frame outcome is no-interface. Absence must be ≥ 0.58 and
   ≥ 0.10 above the best boundary hypothesis. Otherwise the traced FULL
   likelihood is 0.0.
2. **Gate 2:** the FULL likelihood is ≥ 0.58 (the state evidence threshold),
   which creates the `full` node.
3. **Gate 3:** the lifecycle's allowed set is not empty (`allowed_mode` is
   not `hard_gate`).

F1 lifts only gate 3. **Does the user's case (SPL#4 BASE, Oil FULL
27.5–63 s) pass gates 1 and 2?** And where would an F1 fire on cases that are
not full?

## Method

- **Tool:** the new read-only
  [`tests/diagnostics/s11_full_evidence_readout.py`](../../../tests/diagnostics/s11_full_evidence_readout.py),
  with unit tests in `tests/unit/test_s11_full_evidence_readout.py`.
- **Per frame it reads:**
  - the raw outcome status and reason;
  - absence, boundary, and their difference;
  - the outcome Y, as traced (`oil_temporal_projected_source_y`);
  - the FULL and EMPTY likelihoods and whether a `full` node exists;
  - **the first gate that fails** (`gate1:<status or cause>`,
    `gate2:full_below`, `gate3:hard_gate`, `selection:<kind>`, `selected`);
  - the phase, its reason and `allowed_mode`;
  - the resolved kind and the published fill state;
  - the source of a published FULL (image node or top-exit);
  - eligible Foam fronts and admitted Oil rows.
- **Limit:** for a boundary-accepted frame the outcome reports absence as 0.0,
  so absence is not traced there.
- **Sources:**
  - **Windows:** the saved step-7 FULL-debug bundles `SPL4_B_ref` and
    `SPL1_B_ref`, the same as the E1 rerun. The tool reads each record's frame
    metrics and its sequence snapshot.
  - **Local:** the six fill-owner controls, reference arm, as in FPC-1.
- **Correctness check before the Windows request:** on a scratch local
  FULL-debug bundle of one control, the bundle path must equal the local path
  in every row. This tests the tool, not the question.

## Frozen readings

**The sustained unit** is a run of at least 3 consecutive rows with a `full`
node (1.5 s at 2 fps). OFF-1's K is open; 3 is the reading unit, not a
choice of K. The tool also prints the longest run.

**R1, the user's case: SPL#4 BASE 27.5–63.0 s, a run of its own.**

| Reading | Condition |
|---|---|
| **E-PRESENT** | A sustained run starts at or before 30.0 s, and `full` nodes are present in at least 50 % of the window's rows |
| **E-PARTIAL** | At least one sustained run in the window, but not E-PRESENT |
| **E-ABSENT** | No sustained run in the window |

**R2, exposure on cases that are not Oil FULL.** Every sustained run is
listed with whether any of its rows has an eligible Foam front. A run with no
eligible Foam front in any row is an **F1 exposure**: F1's Foam guard would
not stop it.
- **Windows:** SPL#4 Accum 20–90 s (all Foam, review-017) and SPL#1 Accum
  650–700 s (Foam-layered, review-012).
- **Local:** sample5 and sample7, which never become full.

**R3, gate-1 cause on SPL#4 BASE 27.5–63.0 s.** The counts of
`gate1:boundary_accepted`, `gate1:absence_margin`, `gate1:absence_low` and
the other statuses. The boundary-accepted outcome Ys are listed, with no
frozen threshold. The agent reads them against the stale edge (Y693–721,
step 15). The coordinate frame is the trace's.

**R4, gate 3 and selection (information).** For `full`-node rows in the
window: how many are `hard_gate`, and the resolved kind of the rest.

**Information only:**
- SPL#1 BASE 650–700 s: FULL accepted from 672 s, and top-exit FULL from
  674.0 s;
- the whole-recording summaries;
- the other local controls: sample2, base_sample_1 and sample4-interior
  (FULL starts) and sample4-original (initial state unknown).

**What each reading leads to (agreed before output):**
- **E-PRESENT with no R2 exposure:** F1 stays a candidate. A design draft
  follows only after the user settles OFF-1's open questions.
- **E-PRESENT with an R2 exposure:** F1 needs a further guard. The exposures
  are reported, and the user decides.
- **E-PARTIAL:** F1 would have to carry over gaps, which is new. Reported,
  and the user decides.
- **E-ABSENT:** F1 as drafted has no existing evidence on the user's case.
  Path F would need new FULL evidence, a new image feature. The result goes
  back to the user with the peer-side desk check of barrier 1 as the
  alternative.

No reading is tuned after output, and no threshold here changes.

## Local result — 2026-10-27

**Run:** closed managed run `s11-fer1-full-evidence-20261027-001` at
`b2280da`.
- **Tool:** SHA-256 `f205eb2e…`.
- **Arms:** reference arm only, debug NONE, the six controls with FPC-1's
  commands.

**Tool check (scratch, not kept):** on a FULL-debug run of base_sample_1, the
bundle path equals the local path in all 30 rows (0 field differences). The
trace carries every field the tool reads.

| Control | Rows | Raw outcome | `full` node | Gate 1 open | Absence on ambiguous rows (min / median / max) |
|---|---:|---|---:|---:|---|
| sample4-original-unknown | 113 | ambiguous 81, boundary 32 | 0 | 0 | 0.134 / 0.212 / 0.265 |
| sample4-interior-full | 113 | ambiguous 46, boundary 65, pending 2 | 0 | 0 | 0.160 / 0.260 / 0.330 |
| base_sample_1-full | 30 | ambiguous 27, boundary 2, pending 1 | 0 | 0 | 0.318 / 0.327 / 0.539 |
| sample2-full | 5 | ambiguous 5 | 0 | 0 | 0.274 / 0.293 / 0.347 |
| sample5-empty | 111 | ambiguous 94, boundary 15, pending 2 | 0 | 0 | 0.183 / 0.231 / 0.529 |
| sample7-empty | 90 | ambiguous 71, boundary 11, no-interface 5, pending 3 | 0 | 5 | 0.350 / 0.440 / 0.580 |

- **No `full` node in any of the 532 rows.** No control publishes FULL in
  the reference arm.
- **Gate 1 opens only on sample7's EMPTY start.** Five rows at 1.0–5.5 s
  read absence 0.58–0.60, EMPTY 0.68–0.70 and FULL 0.0.
- **On the FULL starts the absence likelihood stays far below 0.58:** sample2
  at most 0.35, base_sample_1 0.54, sample4-interior 0.33. So gate 1 closes
  there because absence is low (`absence_low`), not on the 0.10 margin.
- **Reading (agent):**
  - Locally, the image FULL evidence never forms on a full Glass.
  - R2's local half has no exposure: sample5 and sample7 have no sustained
    run.
  - This does not decide R1, which is SPL#4 BASE on Windows. It does make
    E-ABSENT the expected reading (inference).

## Windows readout — 2026-10-27

**Received:** the relayed stdout, kept outside Git in the closed managed run
`sample/output/s11-fer1-windows-relay-20261027-001`.
- **Identity:** the tool SHA-256 matches `f205eb2e…`. The relayed hashes
  carry OCR slips (`0`/`d`, `0`/`8`).
- **Runs:** `005e0d58…` (SPL#4) and `b0b8403b…` (SPL#1; the E1 relay read
  `b8b8403b`, an OCR slip).
- **Rechecked:** the X-1 counts match the 72 listed rows.
- **One relay gap:** the 36.0 s row lost its values in the relay. By the
  counts it is `gate1:absence_low`.

| Run | Rows | `full` node | Gate 1 closed (absence low / boundary / pending) | Gate 2 (`full_below`) | Published FULL |
|---|---:|---:|---|---:|---|
| X-1 SPL#4 BASE 27.5–63.0 s | 72 | 0 | 31 / 28 / 9 | 4 | none |
| X-2 SPL#4 BASE 20–70 s | 101 | 0 | 35 / 43 / 19 | 4 | none |
| X-3 SPL#4 Accum 20–90 s | 141 | 0 | 92 / 24 / 20 | 5 | none |
| X-4 SPL#1 Accum 650–700 s | 100 | 0 | 90 / 4 / 6 | 0 | none |
| X-5 SPL#1 BASE 650–700 s | 100 | 0 | 84 / 5 / 11 | 0 | top-exit 53 |
| X-6 SPL#4 BASE, all | 181 | 0 | 48 / 89 / 40 | 4 | none |
| X-7 SPL#4 Accum, all | 181 | 0 | 129 / 26 / 21 | 5 | none |
| X-8 SPL#1 BASE, all | 601 | 0 | 494 / 58 / 49 | 0 | top-exit 204 |
| X-9 SPL#1 Accum, all | 601 | 0 | 569 / 17 / 15 | 0 | none |

The "published full" line also counts non-FULL rows as `None` (47 and 397).
That is a printing quirk; it is not a FULL source.

**R1: E-ABSENT.** No sustained run, and no `full` node at all, in SPL#4 BASE
27.5–63.0 s.

**R2: no exposure.** No sustained run on SPL#4 Accum 20–90 s or SPL#1 Accum
650–700 s. Locally, none on sample5 or sample7.

**R3, gate-1 cause on SPL#4 BASE 27.5–63.0 s:**
- **Absence low (31 rows):** on the ambiguous rows absence is 0.32–0.545,
  never 0.58. Absence still beats the boundary in all but one (62.0 s,
  −0.006), so the 0.10 margin is not the cause. The absolute absence is.
- **Boundary accepted (28 rows).** The outcome Ys, as traced:
  - Y570–572 in 18 rows (41.0–63.0 s);
  - Y704 in 6 rows (46.0–50.5 s), inside the stale-edge band Y693–721;
  - Y727 and Y729 once each (46.5, 51.5 s);
  - Y454 and Y456 (28.0, 28.5 s).
- **Reacquisition pending:** 9 rows.
- **Gate 2 (4 rows: 31.0, 32.5, 33.0 and 33.5 s):** gate 1 opens with absence
  0.58–0.593, but FULL reads only 0.106–0.141 and EMPTY 0.142–0.166. The
  no-interface evidence does not call this Glass full or empty.

**R4: no `full`-node rows, so nothing to read.** For context, the lifecycle:
- 27.5–35.5 s: `filling` / `FILL_MOTION_OWNER`, owner-bounded;
- from 36.0 s: `open` / `INITIAL_EMPTY_ENTRY_PENDING` with `hard_gate`.

**Also seen (information):**
- **SPL#4 BASE has eligible Foam fronts from 42.5 s** (Y521–552, nearly every
  row to 63.0 s). In the truth this is FULL, cloudy with residual bubbles
  until about 42 s.
- **The Foam guard would block F1 on those frames,** even if a `full` node
  existed.

**Reading:**
- **The image FULL evidence never forms on any reviewed recording.** That
  holds for Windows and local, for full and not full. Every published FULL in
  these data comes from top-exit (SPL#1 BASE).
- **On SPL#4 BASE the gap is not small.**
  - Absence stays at most 0.545 while the Glass is full.
  - Where absence does win, the FULL share is about 0.14, not 0.58.
- **So lifting gate 3 (F1) changes nothing,** and lowering a threshold would
  not be a bounded change either.
- **Path F therefore means a new FULL evidence,** a new image feature. It
  would have to recognise a uniformly turbid full Glass with a fixed lower
  edge and Foam-like fronts. That is the `S11-F10` and `S11-F05` exposure
  that OFF-1 named (inference).

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `OIL-PHASE-INITIAL`
- Failure-registry entries: `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: on SPL#4 BASE 27.5–63 s no FULL is published; gate 1 stops it (frame absence ≤ 0.545 on ambiguous rows, a boundary accepted on 28 rows), and on the 4 rows where gate 1 opens, gate 2 stops it (FULL 0.106–0.141). Gate 3 never acts.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3 (the step-7 reference bundles and the local reference arm); the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; static preparation active; cost-first, RGB, Local XY, the contested gate, E4 and fast-rise OFF in the arm read.
- Execution scope: a new read-only readout tool with unit tests; one closed managed local run (`s11-fer1-full-evidence-20261027-001`, six controls, debug NONE); a scratch FULL-debug bundle check of the tool (not kept); one Windows readout of saved bundles relayed as text (kept in `s11-fer1-windows-relay-20261027-001`); no detector code change or tuning.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — a readout of existing gates.
