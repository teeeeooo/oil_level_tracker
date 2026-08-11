# S11-R5 Sequence-First Observation Evidence

**Status:** `LOCAL_RESULT RETAINED — FIELD REJECTED`

**R4 comparison baseline:** `20d6b47e94f38a4a12c4bc1b9f1d571300408bca`

**Design commit:** `87d35a5fbeacf9f1e2a31353da663a070521cc37`

**Sequence resolver commit:** `a8177a130f79dd499fa969e12e29b06bb2be8b1c`

**Production integration commit:** `fa8e77393bd77c9be1b8c2723140524d773769aa`

**Lifecycle event repair commit:** `62dbb7095db9321f0b0f9fb8dcef4cf8e303339c`

**Replay authority commit:** `06d9859cba716ada8745eb476e3de9d462ec6568`

**Direct-image guard correction commit:** `ac45a027ffe6676f64d83a7a741d87a3b3a741b9`

## Outcome

> **Field disposition (2026-08-11):** the synchronized secure-Windows
> Base/Accum holdout rejected this local result. Base published false Foam on
> `490/601` frames despite no visual Foam, and Accum stayed initial-EMPTY through
> the visible rise/high/fall cycle. The counts below remain truthful local
> provenance; they are not current acceptance evidence. See the
> [field-failure diagnostic](../../50-diagnostics/s11/s11-r5-secure-windows-field-failure.md)
> and the [R6 replacement architecture](../../20-architecture/s11-r6-optics-aware-observation-architecture.md).

R5 locally accepts a change in final-analysis authority rather than another current-frame threshold adjustment. Raw current-frame observations remain available, but the production analysis now compares bounded Oil candidates, explicit FULL/EMPTY states and UNKNOWN over the complete sampled window before creating public `TrackingSample`, event, judgment and report data.

The accepted behavior is:

- every numeric Oil coordinate is selected from that same sampled frame; R5 never interpolates, predicts or carries a coordinate through a gap;
- confirmed initial FULL/EMPTY is a state prior, not injected detector truth or a numeric level;
- hard unavailable, severe glare/exclusion/border and physical-topology conflicts remain hard barriers;
- recurring fixed appearance is soft competing evidence, while a real stationary material interface can remain selected;
- long paths require independent material anchor clusters, so a chain of weak candidates cannot manufacture a continuous artifact line;
- Foam is resolved independently from adjacent-frame component change and composes only after Oil/state resolution; and
- report crossings and Oil-drop onset require persistent observed movement, so a lone reacquired point cannot create a lifecycle event.

This changes the user-facing report in the intended direction: graphs express directly supported trajectory runs, FULL/EMPTY intervals and explicit unavailable gaps; Foam/high/low/drop events retain source captures. Debug scores and alternate candidates stay outside the primary report.

## Design basis and rejected direction

The R5 root cause is recorded in the [current-frame authority diagnostic](../../50-diagnostics/s11/s11-r5-current-frame-authority-root-cause.md). Direct review showed that roughly ten hypotheses already existed per frame on the private Windows run while most final observations were UNKNOWN. The demonstrated loss was therefore not simply missing Canny/Hough proposals: current-frame reduction discarded alternatives before a human-like sequence comparison could use motion, persistence and fixed-appearance context.

The prior external review in the [implementation reference log](../../70-reference/implementation-reference-log.md) was applied conservatively. Transparent-vessel work supports relative phase cues, cross-vessel paths and multiple vertical observations; optics research treats illumination/refraction as competing causes. Those sources support candidate preservation and bounded spatiotemporal comparison. They do not justify global threshold relaxation, treating every smooth horizontal path as Oil, or giving Foam publication authority over Oil.

Three material variants were rejected during direct graph/source review:

1. An unconstrained candidate path produced superficially attractive coverage (`30/30`, `2/5`, `147/151`, `113/113`) but made the Base explanatory overlay numeric, chose approximately `352 px` in sample2 and filled visually unavailable spans. It was reverted.
2. A second-order acceleration term removed one sample4 spike but over-smoothed sample3's real fast inflow. It was reverted.
3. Relaxed candidate motion preserved sample3's incorrect approximately `294 px` first choice and changed a later visually compatible candidate from approximately `271 px` to approximately `299 px`, reducing blind range agreement from `3/6` to `2/6`. It was reverted.

The accepted resolver deliberately publishes less than those variants and preserves UNKNOWN where independent support is missing.

## Deterministic four-video replay

The reproducible production/report command is:

```text
PYTHONPATH=src .venv/bin/python -m tests.diagnostics.s11_r5_sequence_replay
```

It uses each checked-in MP4 with its matching Recipe, production `OpenCvPhaseDetector`, static-artifact preparation, whole-window sequence resolution and production report generation at `2 Hz`. It verifies accepted tracking fingerprints, same-frame numeric provenance, blind provisional annotations and checked-in user truth. Generated bundles under `sample/output/s11-r5-sequence-first/` are ignored forensic output; source, Recipe, truth, code and the diagnostic are Git authority.

| Video | R4 numeric Oil | R5 numeric Oil | R5 Foam episodes | R5 tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | `2/30` | `0/30` | `0` | `a28aeaa603fb5912aaedf132423d8f78badf9a8a898bcdc9e937af911503af80` |
| `sample2` | `2/5` | `2/5` | `0` | `61a55cc9f0992f8027d0add32c3679e994c4f62688be79893ea438cafd8db9ae` |
| `sample3` | `21/151` | `49/151` | `1` | `476f49c9f13b3fc93e0aaff97238fb0bdf85cfc69353b29de074023cbc6c68f5` |
| `sample4` | `64/113` | `97/113` | `3` | `8cb1785825eab4124000c56bc5d4e20859a712c63302f2a0e996cb1ccf37b21b` |
| **Total** | **`89/299`** | **`148/299`** | **`4`** | — |

`148/299` is observation density, not detector accuracy and not the acceptance target. The increase is accepted because it is concentrated in visually reviewable sample3/sample4 movement, while Base overlay false numerics are removed, sample2's retained interface remains, black/reframed sample3 frames stay unavailable and no coordinate lacks same-frame candidate provenance.

The replay generated `22` Glass-focused captures and `25` report landmarks. Its state distribution includes:

- Base: all `30` samples UNKNOWN, with no Foam, because the short qualification interval is visually unclear and later contains an explanatory horizontal overlay;
- sample2: `2` PARTIAL, `1` EMPTY and `2` UNKNOWN observations, retaining the user-truth boundary near `598–599 px`;
- sample3: `49` numeric observations, `52` `FULL_NO_INTERFACE` plus one `FULL_WITH_FOAM` state, one `30.53–39.04 s` Foam episode and `49` UNKNOWN samples concentrated in the reframe/black and later unsupported spans; and
- sample4: `97` numeric and `16` UNKNOWN observations, including an explicit unavailable gap around `46–51 s` instead of a stored invented trajectory.

## Direct visual and truth reconciliation

Generated detail graphs, source captures and representative decoded frames were inspected directly:

- sample3 now tells the visible empty/inflow/agitation/full story from approximately `30–39 s`, keeps the full/no-interface phase as state, leaves the `65–85 s` reframe/black span unavailable and resumes the later drain near `86 s`;
- sample3 report events are Foam start `30.53 s`, upward zero crossing `32.53 s`, maximum `38.04 s`, Foam end `39.04 s`, observed Oil-drop start `88.02 s`, downward zero crossing `94.03 s` and minimum `101.53 s`;
- sample4's graph is mostly observed, while its material missing interval remains visually dashed/display-only and does not enter CSV, cursor, event or judgment truth;
- Base's seven blind Foam-absent annotations and sample4's ten evaluated Foam annotations all agree with R5 publication; and
- sample2 retains two user-truth coordinates with `6.5 px` MAE despite its older provisional no-interface notes, a documented conflict resolved by direct image review rather than by optimizing to either file.

The two-second sample2 window publishes no Foam episode because its bubbly/static appearance lacks the adjacent-frame change required by R5. Its provisional annotation labels Foam unclear, so this is conservative unresolved evidence rather than proof that Foam is absent. The Oil boundary remains independently observed.

Checked-in user-truth results on this bounded replay are:

| Video | Numeric / usable truth | MAE | Maximum error | Interpretation |
|---|---:|---:|---:|---|
| `base_sample_1` | `0/3` | — | — | old anchors are overlay-conflicted and visually censored |
| `sample2` | `2/3` | `6.5 px` | `7.0 px` | retained stationary interface |
| `sample3` | `2/2` | `12.0 px` | `22.0 px` | detected, but first inflow selection remains displaced |
| `sample4` | `3/5` | `1.83 px` | `4.5 px` | high coordinate agreement where published |

Blind visible-range audit gives sample3 `5/6` numeric and `3/6` in range, and sample4 `14/16` numeric and `8/16` in range. These residuals prevent an accuracy-complete claim. In sample3 the first selected point is around `294 px` while a visually closer same-frame candidate near `321 px` exists, and a later point near `90 s` is around `297 px` versus the blind `326–344 px` range. The tested motion relaxation worsened overall agreement, so R5 records these as future representation/selection evidence instead of adding another sample-tuned rule.

## Mechanism and integration validation

Controlled tests cover:

- continuous material paths versus stronger disconnected artifacts, retained stationary interfaces and conjunctive recurring-artifact opposition;
- confirmed FULL/EMPTY persistence, evidence-backed state entry/release and near-black hard unavailability;
- same-frame coordinate membership, deterministic tie-breaking, long unsupported gaps and no numeric interpolation;
- static Foam rejection, dynamic onset, bounded dropout, state independence and per-Glass/reset isolation;
- production whole-window ordering, legacy-detector compatibility, manifest provenance and fail-closed resolver failure; and
- persistent zero crossings/Oil drop plus report graph/capture behavior.

Final validation on the closeout worktree:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_sequence_trajectory_resolver.py \
  tests/unit/test_sequence_foam_resolver.py \
  tests/unit/test_events.py \
  tests/unit/test_analysis_debug_trace_pipeline.py \
  tests/test_initial_state_retrospective_reconstruction.py \
  tests/integration/test_analysis_and_reporting.py \
  tests/unit/test_graph_renderer.py \
  tests/unit/test_graph_series.py \
  tests/unit/test_report_presentation.py \
  tests/test_s4_graph_axis.py
75 passed in 2.36s

PYTHONPATH=src .venv/bin/python -m pytest -q
1508 passed in 110.74s

PYTHONPATH=src .venv/bin/python -m tests.diagnostics.s11_r5_sequence_replay
# 299 rows, 148 numeric Oil, 22 captures, 25 report landmarks;
# all accepted counts and tracking fingerprints verified

.venv/bin/python -m compileall -q src tests
git diff --check
```

The complete suite initially exposed one stale R4 real-video guard that classified the visible sample3 upper meniscus at `37.04–38.04 s` as a full-like cap. Direct review of the `38.04 s` source capture confirmed the material boundary. The guard now starts at the actual post-transition interval (`39 s`) and is stronger there: no numeric cap coordinate is permitted through `66 s`.

## Remaining secure-Windows gate

The private Base/Accum video is not present in this checkout and was not simulated from local samples. The synchronized Windows replay remains mandatory:

- Base must preserve confirmed FULL until a real upper interface enters, reject the fixed lower appearance, follow descent/recovery and publish no Foam when the source has none;
- Accum must preserve confirmed EMPTY until real entry, follow rise/high/fall and retain only the visually confirmed turbulent Foam interval;
- representative selected source coordinates, recurring-artifact diagnostics, raw/confirmed Foam masks and report captures must be reviewed against the actual frames; and
- the contradictory historical Accum Foam timestamps near `492 s` and `672 s` must be resolved from the private source before latency is scored.

If R5 still follows the Base fixed row or misses the Accum trajectory, the next repair starts at the recorded candidate/image evidence. This local acceptance does not authorize lowering global thresholds, interpolation or private-video-specific rules.
