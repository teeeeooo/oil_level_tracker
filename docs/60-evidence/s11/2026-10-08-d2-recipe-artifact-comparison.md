# D2 existing recipe artifact registration — bounded comparison

The existing registration workflow can exclude a reviewed false candidate, but
the tested single-template recipe is **not adopted**: the completed sequence
loses previously selected targets. The [Work Plan](../../00-project/work-plan.md)
owns the next action. O2 remains unmet and Windows disposition remains `FIELD FAIL`.
This is exposed Mac regression, not a new holdout or Windows qualification.

## Exact scope and reuse

Runtime source: `121cd0525fa075bb0668d810b681f891292caf33`. No production code,
threshold, original recipe, packet or label was changed. The
[machine record](2026-10-08-d2-recipe-artifact-comparison.json) preserves source/input
pins, frozen recipes, registration provenance, output hashes and sequence readout.
Local scripts and images remain under
`sample/output/s11-d2-recipe-artifact-20261008-001/`.

Two fresh calls to the real `OpenCvArtifactProposalService` inspect already
reviewed sample4 f1260/42 s and f1320/44 s. The adapter's internal detector call
uses frame 0/time 0; this setup identity is recorded separately from the actual
decoded frame. No static-reference preparation or sequence history is supplied
to these setup calls. Original crop pixels equal the prior A1 captures. Each call
verifies 220 input/source pins before and after; the original Glass is unchanged.

## Proposal-list and geometry limits

The 42 s setup has 23 candidates and the 44 s setup has 25. Both lists contain
10 boundary proposals and two glare regions. At 42 s, the Y844 candidate ranks
18th and is never reached after the ten-proposal cap. It is not missing from the
detector. The inspection reproduces all ten listed boundary geometries exactly.

Its possible template is an 88-pixel-wide line, X551–639, at Y844; the user had
identified a local semicircle in X581–605/Y839–848. The template does not trace
that arc. The diagnostic display `proposal-review.png` makes this mismatch
visible without registering the line or asking the user to repeat the subtype.
Raising the list cap alone would not resolve the geometry problem.

At 44 s, list item **6** is `phase_transition_scan`, Y822, X559–636. It matches
the original candidate idx21 by source/kind/Y and normalized geometry. The prior
human reply said the pink line crosses no actual boundary, and the frozen target
mapping records this candidate as `other_non_target`. That existing evidence
binds the experimental selection; the physical optical subtype stays unresolved.

The real `RoiEditorDialog` selection handler accepts this exact captured proposal
on its private copy. The experimental recipe differs only by this one template.
It is a local diagnostic copy, not a change to `sample4.oilrecipe` or a new human
review. A separate Y844 template is retained only as an unsafe counterfactual;
it was neither selected in the UI nor used in the full pipeline.

## Frozen matcher comparison

Before readout, freeze both recipes, the unsafe control and comparison preflight
SHA-256 `b993f24b397969aa49f585f8983762790f9bbd4ca2488fd50e84a289d8575b41`.
Replay the unchanged `apply_artifact_templates` and `candidate_is_eligible` on
all 153 stored Oil candidates, preserving original index/source/kind/Y and witness
binding. Persist results before the descriptive role join. The existing frozen
reader validates the 7 target / 3 other-non-target / 143 unreviewed mapping.

| Variant | Reviewed targets still eligible | Reviewed non-targets excluded by template | Unreviewed template matches |
|---|---:|---:|---:|
| No template | 7/7 | 0/3 | 0 |
| Registered Y822 | 7/7 | 1/3 | 16 |
| Counterfactual Y844 | 5/7 | 0/3 | 8 |

Y822 excludes the intended f1320 idx21. Of the 16 unreviewed matches, 11 newly
acquire the rejected flag; all 16 become ineligible under the explicit calibrated
match gate. Existing rejection and eligibility are distinct fields. No physical
labels are inferred for these additional matches.

Y844 excludes the known targets f1140 idx9 and f1320 idx9 at match score 1.0.
This is a concrete coincident-geometry counterexample to whole-line exclusion of
the 42 s semicircle. It does not negate the user's local glass-pattern judgment.

## Actual pipeline and report comparison

Freeze the full-run preflight SHA-256
`c9d953aeeee5327dde95bdac6739d7c6debdbb5a7ccfd50b490134ba26953816`.
Run the existing `AnalysisPipeline` twice with fresh detectors, identical
0–56 s / 2 FPS sessions and `UNKNOWN_REVIEW` initial confirmation: baseline recipe
versus Y822 recipe. Each run produces 113 samples, including the normal reference
preparation, completed resolver and unchanged report-presentation builder.
The unsafe Y844 variant is not run. All 224 preflight input/source pins survive.

| Recorded outcome | Baseline | Y822 registration |
|---|---:|---:|
| Non-null raw Oil coordinates | 101 | 105 |
| Oil-valid samples | 101 | 102 |
| Non-null raw Foam coordinates | 26 | 26 |
| Foam-valid samples | 26 | 23 |

Raw coordinate counts are not accuracy or accepted observations. Core Oil/Foam
validity, Oil coordinate or state fields differ at 27 frames; any tracking-field
comparison differs at 102 frames, including flags/confidence. Report payloads
differ. These changes are not a claim of 102 physical regressions.

All 113 raw candidate inventories preserve source/kind/Y across the two runs.
Baseline candidate identities/rejected states at all seven anchors equal the
original A1 capture. Thus existing reviewed candidate references remain usable.

| Time | Baseline selected Oil Y | Registered selected Oil Y | Supported interpretation |
|---|---:|---:|---|
| 44 s | 822 | 842 | Reviewed false candidate removed; proximity to target Y844 does not certify the replacement's scalar/path accuracy. |
| 49.5 s | 836 | 880 | Previously selected reviewed target idx19 is lost to another candidate. |
| 52 s | 833 | 862 | Previously selected reviewed target idx20 is lost to another candidate. |

The assistant inspected `pipeline-review.png` against original saved pixels.
At 49.5 s the new line lies on the lower vessel rim; at 52 s it is below the
reviewed upper boundary. These are assistant observations, not new human labels.
Existing target judgments already establish the loss; no repeated user judgment
is needed to reject this recipe as a correction.

## Recorded sequence boundary and limits

The first difference in the phase witness occurs at f1080/36 s. This is the first
recorded phase divergence, not proof of the first physical error. Tracklet IDs
from different runs must not be treated as shared physical identities.

At f1485/49.5 s, the target at Y836 is not template-rejected in either run. In
both witnesses it remains `ANCHOR_ELIGIBLE`, tracklet-admitted, phase-admitted
and publishable. Before registration, the phase is `filling/FILL_MOTION_OWNER`
with an `owner_bounded` allowed chain and selects that target. After registration,
the phase is `open/FILL_EVIDENCE_ACCUMULATING`, `unconstrained`; selection chooses
the Y880 continuation row. Direct/recovery/delayed route evaluations are not
evaluated in this witness. The target was not removed at the local matcher;
sequence ownership and final competition changed.

The recorded chain is enough to reject promotion. It does not yet establish a
single earlier harmful association/phase predicate. Do not restore the known
false Y822 owner merely to recover the old output, add more exclusions to chase
each new winner, promote a survivor by default, or retune matcher/selector scores.
Use the saved pair to inspect existing tracklet, phase and selector owners before
choosing a bounded repair. The setup registration input remains useful; its
current position veto is not by itself a physical-identity solution.

## Verification and preservation

The real proposal service, real UI acceptance on a copy, frozen matcher, full
pipeline and report-presentation paths were exercised. Prior 23 focused existing
contract tests remain applicable because their source owners are unchanged.
Existing input pins and recipe-only difference were rechecked after all readouts.
Governance, local-link/obligation checks and whitespace checks accompany publication.
No ML, Windows execution, field acceptance, label migration or original-input
mutation occurred. Independent stationary/crossing/occluded controls remain unmet.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the unsafe Y844 counterfactual directly excludes two reviewed targets at calibrated eligibility. For Y822, f1485 target survives admission but loses final selection after phase/tracklet divergence; the first earlier harmful association predicate is UNKNOWN. The earliest recorded phase difference at 36 s is not certified as a physical error.
- Logic-map impact: NONE — existing proposal, matching and sequence owners were exercised without production changes; candidate exclusion is not claimed to grant identity.
- Failure-registry impact: NONE — the observed position collision and altered association competition instantiate existing F04/F10 guards; no new field qualification or accepted mechanism is established.
