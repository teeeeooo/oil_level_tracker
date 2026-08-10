# Post-S11 Structural Maintainability Assessment

## Responsibility and snapshot

This diagnostic records the maintainability assessment requested before future
structural refactoring. It is not architecture authority and does not activate
source work. Milestone order remains owned by
[`../00-project/roadmap.md`](../00-project/roadmap.md), and the executable gate
remains owned by [`../00-project/work-plan.md`](../00-project/work-plan.md).

- Assessment date: `2026-08-10`
- Assessed source head: `f85654d7fdc6a0c61e7f477070a4441c52b55216`
- Scope: hand-written production Python under `src/`
- Exclusions: tests, generated/package output, `.venv` and replay output

## Measurement interpretation

The repository-local soft limits are useful review signals, not automatic
split requirements:

| Signal | Recommended interpretation |
|---|---|
| Physical LOC `> 400` | review warning |
| Physical LOC `> 800` | require a responsibility review or explicit cohesion rationale |
| One function/method `> 80–100` lines | strong extraction warning |
| Behaviorful top-level classes `> 5` | review warning |
| Internal module import fan-out `> 10` | coupling/orchestration warning |
| Flat package modules `> 10` | navigation notice only |
| Flat package modules `> 20` | feature/package taxonomy review |

Behaviorful class count excludes simple data-transfer dataclasses, enums,
protocols, exceptions and internal command messages. Flat module count is not
dependency fan-out: a package containing many cohesive modules does not
necessarily import or coordinate all of them.

Refactoring should normally activate when at least two material signals agree,
or when a single file above 800 LOC contains multiple change axes or a very long
callable. Composition roots such as `bootstrap.py` and bounded type-algebra
modules may retain explicit exceptions.

## Repository snapshot

| Measurement | Result |
|---|---:|
| Production Python files | `192` |
| Files above 400 physical LOC | `27` |
| Files above five raw top-level classes | `13` |
| Files above five behaviorful top-level classes | `0` |
| Modules with internal import fan-out above ten | `8` |
| Directories with more than ten flat Python modules | `6` |

The raw class threshold has substantial false positives. For example,
`oil_shadow_types.py` contains 39 related enums/dataclasses, while
`oil_shadow_pipeline.py` contains seven small command/input dataclasses and two
behavior owners. Neither should be split merely to reduce class count.

The largest flat packages are:

| Package | Modules excluding `__init__.py` |
|---|---:|
| `ui/widgets` | `28` |
| `adapters/vision` | `26` |
| `application/services` | `21` |
| `ui` | `20` |
| `adapters/storage` | `17` |
| `domain` | `16` |

These counts justify a later navigation/taxonomy review, not immediate file
moves. Ownership must be separated before package paths are reorganized.

## Confirmed responsibility hotspots

| Owner | Evidence | Assessment |
|---|---|---|
| `adapters/vision/oil_shadow_observations.py` | 2,174 LOC, 53 top-level functions, longest callable 151 lines, 2 production and 10 test importers | strongest active detector monolith |
| `ui/main_window.py` | 1,096 LOC, fan-out 22, 98 callables, 12 direct test importers | playback/Profile extraction helped, but editing, validation and analysis routing remain concentrated |
| `ui/result_review_window.py` | 903 LOC, fan-out 16, 50 callables | bundle/video/render/debug/export lifecycles remain in one window |
| `adapters/vision/opencv_phase_detector.py` | 550 LOC, fan-out 12, `detect()` 209 lines, 15 direct test importers | central detector composition and debug projection remain concentrated |
| `adapters/vision/oil_pipeline_validation.py` | 1,143 LOC, longest methods 172 and 152 lines | cohesive stateless validator; split only after higher-value boundaries, if independent current-frame versus temporal/store axes remain clear |

`oil_shadow_pipeline.py` remains large at 1,238 LOC, but its remaining two
behavior owners are the fixed reducer and serialized pipeline. The post-S11
split is already one-way and independently replay-verified, so another split is
not size-driven priority work.

`oil_shadow_types.py` is a cohesive canonical type family. Its 1,162 LOC and 39
classes are navigation concerns rather than evidence of a behavior owner
violation; any future split must first prove cycle-free type-family boundaries.

## Legacy Vision retirement candidate

The static production import graph has no path from a production entry point to
the following legacy Oil selection cluster:

- `candidate_generators.py` — 179 LOC;
- `candidate_scorer.py` — 930 LOC;
- `oil_candidate_consensus.py` — 362 LOC;
- `oil_no_interface.py` — 147 LOC;
- `oil_temporal_path.py` — 724 LOC.

The cluster totals 2,342 production LOC. Existing tests currently prove that
the production detector does not call these legacy owners, and the Windows
checklist still names that negative authority. Before deletion, verify there is
no supported diagnostic or dynamic-import consumer, replace obsolete
behavior-unit tests with an explicit absence/cutover guard, and reconcile the
manual checklist. The preferred outcome is retirement, not modularization of
unused behavior.

## Sequencing decision

The maintainability program belongs after S11 and before S12:

- starting it before S11 closure would invalidate or move the exact candidate
  that still requires target-Windows acceptance;
- postponing it until after S12 would add new Workbench and Result Review UX
  behavior to the same confirmed hotspots and then rework those features during
  the later split;
- executing it between milestones preserves a field-validated S11 behavior
  baseline while giving S12 stable ownership boundaries for new UI behavior.

S11-M is therefore a planned post-S11/pre-S12 gate, not an extension of S11
detector tuning and not an after-S12 cleanup backlog.

## Planned post-S11 slice order

This sequence activates only after S11 receives final target-Windows acceptance:

1. **R1 — Legacy Vision retirement:** prove and remove the isolated five-module
   legacy cluster; preserve a production-cutover guard.
2. **R2 — Current-frame Oil evidence decomposition:** split raw extraction,
   current-observation interpretation, evidence summaries and semantic
   hypothesis construction without changing thresholds, ordering or outputs.
3. **R3 — OpenCV phase orchestration decomposition:** reduce `detect()` and
   separate bounded frame preparation, detector composition and debug-artifact
   projection while preserving the detector port.
4. **R4 — Result Review shell decomposition:** transfer bundle/video lifecycle,
   review rendering/navigation and export coordination out of the Qt window.
5. **R5 — Workbench shell completion:** transfer remaining Glass editing,
   validation routing and analysis-completion coordination out of `MainWindow`
   while retaining only bounded compatibility delegates.
6. **R6 — Conditional taxonomy pass:** only after responsibilities stabilize,
   consider feature-oriented `ui` and `vision` subpackages and reassess whether
   the validation/type modules still require division.

Detector slices must preserve the accepted `111/299` four-video stream and all
four fingerprints. UI slices must preserve Qt lifecycle, close/data-loss,
preview-staleness, bundle immutability and export cleanup contracts. Each slice
must remain independently reviewable; a package-wide move or LOC-compliance
rewrite is not authorized.

## Scale and exit boundary

The targeted program is medium-to-large but incremental: approximately four to
six independent source gates, 15–25 affected source modules, 20–35 validation
targets and 6,000–10,000 changed lines, mostly moves plus the potential 2,342
LOC legacy deletion. This is materially smaller than forcing all 27 LOC
warnings and six flat-package notices below their thresholds.

Completion does not require every file below 400 LOC or every package below ten
modules. It requires that the confirmed multi-responsibility owners be reduced,
the legacy cluster be removed or explicitly retained with evidence, actual
fan-out exceptions be justified, and all behavior-preservation gates pass.
