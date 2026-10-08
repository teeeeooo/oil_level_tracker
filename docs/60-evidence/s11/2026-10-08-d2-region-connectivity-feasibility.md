# D2 region-connectivity feasibility — 2026-10-08

Base: `dd557b4bc5ecd8f4517a95bc5bb6c966d2cd3013`, clean main. The user authorized
the proposed local D2 hypothesis/control work, autonomous commit/push and a stop
for necessary user decisions or Windows work. This is a new **synthetic mechanism
feasibility experiment**, separate from the closed Windows support review.
The [machine receipt](2026-10-08-d2-region-connectivity-feasibility.json) preserves
the preflight, exact test/model file hashes, environment and counterexamples.

## Question, reuse and fixed scope

Does global 2-D region connectivity add information beyond the existing local
appearance summaries, and can it independently establish target identity while
preserving a candidate with mixed local support?

Discovery checked region/adjacency/connected-component responsibilities across
source, diagnostics and tests. `s11_region_competition._adjacency` already owns
immediate-neighbour energy; its fixed plane/partition/ribbon model does not measure
global region connectivity. Production connected-component uses are Foam/artifact
or mask owners, not Oil physical-identity authority. The new oracle lives only in
[contract tests](../../../tests/unit/test_s11_region_connectivity_contract.py),
following the existing W1 synthetic-counterexample pattern. No runtime module,
diagnostic CLI, image loader, model dependency or prediction route is added.

Before execution, preflight SHA-256
`f01adec3ee75effc30650a080ebbd6f6d82e9ac257966d842d6fe8aabb2e4790`
fixed the controls and stop rule. A test-only oracle receives exact **nominal
region maps supplied by construction** and a visibility mask. It computes
four-connected observed components, viewport/missing-pixel contacts, enclosure,
and ordered above/below component IDs at each candidate sample. IDs are canonical
by first observed pixel, invariant to nominal-class renaming/polarity. Unknown
pixels cannot connect regions or certify enclosure. Fixtures are at most 96×64.

This deliberately optimistic input removes segmentation error from the question.
It is not a segmentation algorithm, material map, hand-labeled private input or
trained classifier. No physical label enters the oracle; `identity_decision` is
always `NOT_EVALUATED`, not a measured successful abstention rate.

## Results

| Control | Verified result | Meaning |
|---|---|---|
| Two 4×4 patterns with equal row/column sums and equal existing horizontal/vertical adjacency energy | 8 versus 9 connected components; both adjacency energies are 2/3 with 12 pairs per direction | Global connectivity can preserve information discarded by these specific local summaries |
| Main partition plus enclosed pocket | Above-side component differs at the pocket; the common below-side component is preserved | Geometry can distinguish a local enclosed feature under ideal visible segmentation |
| Five-sample mixed path | Component pairs `(2,1), (0,1), (0,1), (0,1), (0,1)` remain separate | Local disagreement is representable without deleting a sample, voting or relabeling the candidate |
| Constructed fluid partition versus same-appearance stationary structural step | Identical input and complete oracle output for opposite required target roles | Connectivity alone cannot resolve this physical ambiguity |
| Pocket return outside viewport | Visible pixels and topology equal a partition; zero certified enclosed components | A crop boundary cannot establish the extent of the real feature |
| Pocket return hidden by mask | Same visible input as a partition; all observed components touch unknown; hidden-value changes have no effect | Missing pixels cannot prove closure or absence |

Ten focused tests passed in the project environment:

```bash
.venv/bin/python -m pytest -q tests/unit/test_s11_region_connectivity_contract.py
```

The tests also cover unavailable sample support, four-neighbour corner contact,
input immutability and nominal-class renaming. Python/NumPy/OpenCV versions and
source hashes are in the receipt. Local preflight/full readout remain under
`sample/output/s11-d2-connectivity-20261008-001/`; the compact receipt retains the
two exact collision patterns and the reproducible test owner.

## Disposition and limit

**CLOSED WITHOUT PROMOTION for standalone connectivity-to-target identity.**
There is useful geometric information, but promoting the partition observation
to target also accepts its structural countermodel. Rejecting it loses the true
partition; abstaining on the pair demonstrates ambiguity, not recovery.
This rules out the proposed standalone identity certificate, **not every
conditional classifier or model combining connectivity with other evidence**.
The contract permits useful decisions elsewhere and unresolved output for genuine
collisions; perfect separation of every reflection is not required.

No operating point, real-image segmentation, learned model, Mac efficacy test,
Windows experiment or production change follows from these synthetic results.
The predeclared synthetic stop condition was reached, so real-media work would
not resolve this standalone information limit and was not run. The Windows idx13
reply is motivation only: the constructed pocket is not a reconstruction of that
frame, and idx12 remains NOT_ESTABLISHED. D1 and bounded D2 reviews stay closed;
O2/D3 and FIELD FAIL are unchanged.

## Next research decision

The next allocation is a method/data decision, not another version of the same
topology rule. Two routes remain plausible; this experiment does not prove which
will succeed:

- **Recommend a bounded learned-challenger readiness assessment.** First define
  what a model would predict and audit existing truth granularity, prior exposure,
  recording partitions and secure-PC execution constraints. The existing passive
  75 candidates are three scenes, not an adequate independent train/test corpus;
  Mac A2's seven targets/three wrong targets retain their existing roles. Identify
  the concrete missing controls and estimate additional human review before any
  training. This can demand new Windows environment/data preparation and user
  annotation effort, so the direction is presented for user choice. No model is
  selected; installation and fitting are outside this readiness proposal, and
  acceptance gates remain intact.
- **Continue non-learned research on existing recordings.** Require a genuinely
  different measurable cue or conditional mechanism with opposing controls;
  do not retune connectivity, region residuals, polarity or votes. This avoids
  committing to a learning/data workflow but has no currently established new
  discriminator. New filming, hardware purchases and private-file export are not
  assumed available or requested by either route.

Learning is not a cure for identical observations. Its possible benefit is a
conditional decision using richer observed patterns and explicit abstention,
which must still demonstrate true-target retention and wrong-target suppression.
The [Work Plan](../../00-project/work-plan.md) owns the user's direction decision.
No additional Windows instruction is issued before that decision.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: synthetic identity promotion from observed region connectivity admits a same-observable structural countermodel. This establishes no new first cause in Windows production.
- Logic-map impact: NONE — only test-owned oracle controls and evidence are added; no executing detector, proposal, selector or publication route changes.
- Failure-registry impact: NONE — the counterexamples reinforce F04 geometry/identity and F09 censoring boundaries; no new field failure or accepted mechanism is asserted.
