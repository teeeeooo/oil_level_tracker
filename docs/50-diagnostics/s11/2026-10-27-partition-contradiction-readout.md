# FPC-1 — what would a Foam-aware partition contradiction (E1) free?

**Status: LOCAL COMPLETE 2026-10-27; the first Windows relay is VOID (tool defect, [below](#first-windows-relay--void)); the rerun is QUEUED.** This is design
input for the
[E1 draft](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-foam-aware-partition-contradiction-e1),
run on the user's "응 진행하자" (2026-10-27). It is read-only: no detector,
flag, threshold or Recipe change.

**Result in short:**
- **Every post-track demotion on all six local controls rests on texture
  conflict alone.** That is 2,057 rows: none has an artifact, optics or
  opposed-material contradiction.
- **Both candidate scopes are broad.**
  - **Scope A** (R14's ordered-lower flag) would free 479 rows.
  - **Scope B** (an eligible Foam front above) would free 167.
  - **The freed rows** include fixed structure (sample7 Y384 in every frame
    35–44 s) and sample4-interior rows (Y847–859) at three of R7's protected
    times.
- **Whether either scope frees SPL#4's level at 25.5–27.0 s** is the Windows
  question.

## Method

- **Run:** closed managed run `s11-e1-partition-readout-20261027-001` at
  `5468d3e`.
  - **Controls:** the six fill-owner controls at 2 fps with debug NONE.
  - **Arm:** only the reference (IFO v2 + top-exit v3) is read. Its rows,
    events and version equal the OAR-1 reference arm.
- **Tool:** the new read-only
  [`tests/diagnostics/s11_partition_contradiction_readout.py`](../../../tests/diagnostics/s11_partition_contradiction_readout.py),
  with unit tests in `tests/unit/test_s11_partition_contradiction_readout.py`.
  - **Hash:** SHA-256 `8a3c7ae1…` for the local run; `b658568b…` after it
    compacts its printout; `a7315bf8…` after the bundle-path fix below. The
    local path, and so the local results, are unchanged.
  - **Sources:** the local run reads the completed detections; on Windows it
    reads a saved FULL-debug trace.
- **Demoted row:** an Oil candidate whose initial tier is eligible and whose
  post-track tier is `CANDIDATE_ONLY`, with opposition ≥ 0.60.
- **Contradiction inputs:** recomputed with the production
  `OilCandidateEvidence` normaliser:
  - texture ≥ 0.60;
  - artifact signature ≥ 0.44;
  - optics ≥ 0.46;
  - `opposed_material`.
- **Texture-only:** texture conflict is the only one of these present.
- **Scope A:** texture-only and `sequence_ordered_lower`. The Foam seed age
  that R14 also requires is not traced, so A is an upper bound.
- **Scope B:** texture-only, with an eligible Foam-front candidate
  (`sequence_foam_eligible` ≥ 0.5) above the row in the same frame.

## Local results

| Control | Frames | Demoted rows | Texture-only | Scope A (frames) | Scope B (frames) |
|---|---:|---:|---:|---:|---:|
| sample4-original-unknown | 113 | 643 | 643 | 26 (11) | 17 (9) |
| sample4-interior-full | 113 | 142 | 142 | 53 (25) | 42 (16) |
| base_sample_1-full | 30 | 26 | 26 | 0 | 0 |
| sample2-full | 5 | 67 | 67 | 10 (1) | 12 (1) |
| sample5-empty | 111 | 239 | 239 | 119 (21) | 70 (10) |
| sample7-empty | 90 | 940 | 940 | 271 (28) | 26 (3) |

**Where the freed rows lie** (from the kept JSON):
- **sample7 (scope A):**
  - Y384 in every frame from 35.0 to 44.3 s; it is the fixed top row seen in
    every FOR-1 frame;
  - rows at Y536–565 throughout 32.5–44.3 s;
  - 6–8 rows per frame at Y638–760 at 17.0–19.5 s.

  sample7's published Oil there is UNKNOWN.
- **sample5 (scope A):** 3–14 rows per frame spread over Y622–816 at
  19.0–27.5 s. The surface is turbulent at about Y550–560 (agent estimate).
- **sample4-interior (scope A):**
  - Y847–859 at 1.0–9.5 s, including 2.5, 3.0 and 9.5 s, which are among
    R7's visually rejected lower-rim and internal-partition times;
  - Y820–843 later.

  Those R7 times were recorded on R7's Recipe, so whether these are the same
  rows is not reviewed.
- **sample4-original-unknown:** scope A frees Y874–875 and Y813–842 at
  39.5–55.0 s, against published rows of Y829–868.

## Reading

- **Texture conflict is the only contradiction anywhere.** So "texture does
  not count", even under a Foam scope, removes the demotion's only grip on
  the rows in scope. The rows freed are mostly not a level: fixed structure,
  rows inside turbulent water, and rows near R7's protected times.
- **Freed is not published.** A freed row becomes `CONTINUATION_ELIGIBLE`;
  whether it is then admitted and published depends on tracking. This readout
  does not run that. The count is the exposure, not the row change.
- **Neither scope is narrow on these controls.** A scope that frees SPL#4's
  level would need a further discriminator. Its Windows rows show what the
  level's demoted rows have that the freed structure lacks.

## Windows readout

The read-only
[E1 partition readout request](../../40-operations/s11-current-windows-field-qualification.md#e1-partition-readout-request)
runs the same tool on the saved bundles:
- **SPL#4 BASE 20–35 s and SPL#1 Accum 660–690 s:** per frame, with every
  demoted row near the review-015, review-012 and review-017 marks;
- **SPL#4 and SPL#1, both Glasses, all frames:** totals only.

## First Windows relay — VOID

**Received 2026-10-27, kept in the closed managed run
`sample/output/s11-e1-windows-void-relay-20261027-001`.** All six runs, on
both recordings and both Glasses, printed `demoted 0`.
- **Why that is not a result:** step 14 read the same `SPL4_B_ref` trace and
  found post-track `CANDIDATE_ONLY` level rows at 25.5–27.0 s.
- **The defect:** a trace record's top-level `candidates` are the frame's
  detector candidates, written before sequence resolution. They carry no
  resolved tier or opposition; those live in the record's `sequence`
  snapshot. The tool's bundle path read the top-level list. Its local path
  reads completed detections and was unaffected.
- **The fix:** the bundle path joins each snapshot candidate to its detector
  candidate on (kind, source, canonical Y).
  - From the snapshot: the tiers, opposition, identity, ordered-lower flag,
    tracklet and Foam eligibility.
  - From the detector candidate: the raw features and penalties.
  - Join misses are printed.
- **Verified:**
  - On a local FULL-debug bundle of sample2 (scratch, not kept), the bundle
    path equals the local path in every row: 67 demoted, scope A 10, scope B
    12, 0 join misses.
  - A unit test pins that the detector candidates alone yield no demotion.
- **Not traced in the snapshot:** the Foam-material identity, which now reads
  0 on the bundle path.

The rerun uses tool SHA-256 `a7315bf8…`.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F06`, `S11-F03`, `S11-F04`
- First harmful stage: `OIL-AUTHORITY` post-track demotion of SPL#4's level at 25.5–27.0 s (steps 13–15); locally, every post-track demotion is texture-only, so the E1 exemption would reach far beyond the level.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3; the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB, Local XY, the contested gate, E4 and fast-rise OFF in the arm read.
- Execution scope: one closed managed local run (six controls, debug NONE) and a new read-only readout tool with unit tests; one Windows readout relayed as text, void by a tool defect (kept in `s11-e1-windows-void-relay-20261027-001`), the fix verified on a scratch local FULL-debug bundle; no detector code change or tuning.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — the breadth is an `S11-F06` exposure count, not a new mechanism.
