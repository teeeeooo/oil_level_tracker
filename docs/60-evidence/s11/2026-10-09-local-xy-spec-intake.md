# Local XY specification intake and saved-execution verification

**Scope:** inspect/preserve the supplied design and its native experiment outputs;
review validity and update the next implementation plan. No production patch,
frame-detector replay, new physical labels or Windows run is part of this intake.
Base: `167126e5f095e4011bc8f7dfd51049df87dd84f6`.

The [supplied package](../../70-reference/s11-local-xy-2026-10-09/README.md)
contains four byte-preserved files; the standalone summary equals the ZIP entry.
All three original file checksums match. The delivery JSON explicitly calls itself
a derived summary, so the native saved runs were checked separately.
[Receipt](2026-10-09-local-xy-spec-intake.json) and
[import manifest](../../70-reference/s11-local-xy-2026-10-09/import-manifest.json)
separate original claims, this intake's verification and preservation locations.

## Fresh verification

- Inventory and read/format validation cover all **165 files / 201,719,723 bytes**:
  71 JSON, 69 PNG, 7 recipes, 6 Python scripts, 4 logs, 4 CSV, 2 JPEG and 2 HTML.
  All Python runners were inspected; JSON/recipe/image/CSV parsing and local HTML
  asset links passed. The two comparison graphs, two ROI montages and actual
  baseline/shared-mask report graphs were visually inspected. This is not a new
  physical review of every frame or a browser acceptance test of the full HTML.
- All **220 production source pins and 16 input pins** match; originals stayed
  unchanged. The primary and three follow-up runner pins match their preflights.
- Reused the current `ObservationSequenceResolver` on every saved raw detection:
  **8 runs / 751 complete detections reproduce exactly**, including the full
  candidate/debug fields. No video decoding or frame detector rerun was needed.
- Independently recomputed tracking fingerprints, counts, public changes,
  checkpoints, longest nonnumeric runs and current/final Foam comparisons; they
  agree with the supplied summary. The four baseline fingerprints agree with
  the existing frozen comparison.
- The 12 native contract results agree with the delivery. The preserved log
  reports **72 pytest passes**; these tests and synthetic probes were not rerun
  during intake and are not 84 new product unit tests. Their historical PASS
  does not validate the unimplemented opt-in path.

## Experiment disposition

The 751 rows are repeated configurations of exposed regression material, not
751 independent labeled images. Counts below mean non-null raw coordinates,
not valid coverage or physical accuracy.

| Configuration | Oil / Foam numeric rows | Public changed rows | Conclusion |
|---|---:|---:|---|
| Baseline, sample4 | 101 / 26 | 0 | Existing behavior, including known wrong targets. |
| A: shared local XY mask | 77 / 6 | 48 | Reject for adoption: Oil disappears over 41–56 s and Foam changes substantially. |
| B: three Oil measurement lanes only | 105 / 26 | 31 | Useful next implementation seam; not accepted efficacy. 42 s remains missing and new coordinates have no inherited truth. |
| C: B plus global paired phase means | 79 / 26 | 49 | Reject this global numerical replacement: long late loss. |
| D: paired phase means without XY | 78 / 26 | 50 | Confirms that the global replacement can cause the long loss without the new mask. Do not blame all C changes on XY exclusion. |

B retains current Foam metrics/coordinates on all 113 rows, but at 40 s changes
Oil to Y830 while Foam is Y840. Both public validity flags become false under
the existing topology checks. Unchanged Foam count is not preserved final Foam
usability. Do not disable topology/phase checks to rescue the experiment.

The former **NOT TESTED** statement was correct at the parent HEAD. A–D are now
completed, unpromoted experiments. **Affected-footprint-only numerical handling
with a formal opt-in input remains unimplemented and untested.** Preserve both
facts; do not rerun A–D as a new idea or claim they disprove every local exclusion
implementation. The earlier 40/45 patch-overlap result remains a non-error count.

## Design review and necessary qualifications

The proposed direction is reasonable: reuse the existing material path,
raster-material path and phase-transition measurement owners, preserve shared
preprocessing/Foam and use a bounded Oil-only aperture. Local withdrawal is a
sampling policy, not a whole-box physical label or a clean-fluid certificate.
The exclusion fixture is 420 pixels; the earlier human attribution covers only
125 eligible reference edges. No truth is expanded.

Four refinements are required in the current owners before implementation:

1. **Locality must be defined at the right layer.** `_sector_profile` normalizes
   using the sector-wide 10th/90th percentiles and performs later seed/path
   competition. The phase generator also shares a bounded selection budget.
   Passing a reduced mask to either generator does not prove that every other
   candidate stays unchanged. Preserve legacy measurements for truly unaffected
   primitive operations, accounting separately for normalization/context and
   shared selection dependencies. Full candidate/detector equality is required
   for OFF/empty/whole-scope nonintersection, not for every other candidate in an
   actively changed frame. Record propagated selection differences explicitly.
2. **Common-X is a local numerical hypothesis.** Apply it only where exclusion
   actually withdraws usable samples, with original support denominators and
   unchanged minimum area. Preserve full legacy calculations elsewhere. Before
   coding, freeze how material-profile normalization and Sobel/material terms
   retain their basis; a narrow contrast window is not its entire dependency
   set. The global C/D replacement is not this new operation.
3. **Runtime scope and diagnostics must agree.** Bind scope to the intended
   Glass/geometry/reference and include its policy/version in run identity.
   Existing A1 helpers must record the actual changed aperture and numerical
   rule; rerunning the old unmasked helper would produce misleading lineage.
   Preserve original-versus-used support, bounded resources and debug neutrality.
   Do not silently toggle unrelated recipe templates or apply the same reference
   as both a withdrawal and a new whole-candidate veto.
4. **No automatic success label or stage jump.** Unchanged rules can assign
   different authority/phase after changed evidence; the old candidate's ID or
   authority tier cannot simply be copied. Compare final Oil/Foam validity and
   the actual report, plus the existing seven target/three wrong-target bindings.
   Other samples with scope OFF prove compatibility, not cross-Glass efficacy.
   O2 controls, later authority/phase stages and Windows field acceptance remain.

The source and original specifications are preserved rather than edited to
retroactively include these qualifications. The
[architecture contract](../../20-architecture/s11-interface-observability-witness-architecture.md#local-xy-oil-measurement-exclusion--proposed-contract)
and [validation contract](../../30-validation/s11-interface-observability-witness-validation.md#local-xy-measurement-exclusion-controls)
own the adopted proposal; Work Plan alone owns live sequencing.

## Next work mapping

| Supplied task | Repository plan |
|---|---|
| WP0 | Preservation/intake complete; do not restart an inventory or rerun A–D. |
| WP1–WP3 | One bounded opt-in implementation: scope binding and actual candidate calls, local numerical/support rule, matching lineage. First freeze the dependency/budget details above in the existing owners; no new UI, recipe schema or classifier framework. |
| WP4 | One frozen full-window comparison through the existing replay, evaluator and report; all four Mac windows, explicit OFF/ON and debug equality scopes, existing protected controls and resource checks. |
| WP5 | Record retention/rejection and remaining unknowns. New output identity requiring human judgment is reviewed only on a concrete image/sequence. Prepare Windows work only after a suitable candidate exists. |

No new physical judgment or Windows execution is required to prepare WP1–WP3.
This request ends at preservation, review and planning, without implementing the
challenger. No ML, threshold/rectangle sweep, dense-contour rewrite, downstream
repair or new scalar labeling is adopted.

## Preservation and reproduction limits

All 165 native files remain in their original ignored directory and in a verified
local ZIP; every archive entry matches its inventoried hash. Selected native
text/runners and overview figures are additionally copied into the reference
package for Git preservation. Full raw traces and HTML assets are indexed by the
receipt and retained locally; the local archive is not an off-machine backup.

The supplied specification has one extra blank line at EOF. Preserve its original
hash rather than normalize it; whitespace verification excludes that one imported
file and passes for all other changes. Link/anchor and S11 governance checks pass.

The supplied rerun instructions are historical: native runners depend on their
original directory depth and exact pins. `summarize_experiments.py` can overwrite
derived outputs, despite the specification's general overwrite-guard description.
Do not rerun it over originals. The intake verifier is explicit-path and refuses
an existing output receipt. No evidence files were deleted or regenerated.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: A changes shared measurement input; C/D change phase measurements globally; recorded late phase barriers are downstream outcomes, not proof of the first physical error. B's 40 s public topology invalidity is verified; new candidate physical identities remain unresolved.
- Logic-map impact: NONE — saved-resolution verification and a proposed implementation contract change no executing source owner or entry path.
- Failure-registry impact: NONE — existing starvation, identity, cross-coupling, provenance and global-change guards explain the bounded results; no field mechanism is retired.
