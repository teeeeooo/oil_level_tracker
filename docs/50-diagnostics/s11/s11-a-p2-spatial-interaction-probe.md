# S11-A P2 × Spatial Evidence Interaction Probe

## Status and authority

- Role: S11-A P2 × Spatial Evidence Interaction Probe Worker
- Lane: B — Bounded Change
- Starting `main`: `fd3c7baa6cc6f6095343a1da2cdba4375914c799`
- Probe branch: `feature/s11-a-p2-spatial-interaction-probe`
- Scope: diagnostic implementation, tests, manifest and source-completing evidence only
- Production `src/` mutation: none
- Product truth: existing S6 repository-local `.oiltruth` corpus only
- Truth denominator: `15 reviewed / 13 usable / 2 unusable`

This probe isolates the interaction between two already-merged diagnostic mechanisms: P2
exposure-decoupled no-interface evidence and the five-sector cross-ROI Spatial Path gate. It does
not introduce a new no-interface formula, spatial algorithm, threshold search, production cutover,
temporal history, schema, setting, or dependency.

The deterministic interaction manifest is
`docs/50-diagnostics/s11/s11-a-p2-spatial-interaction-probe-manifest.json`. Its timing-free result
fingerprint is `621295cc84adad7736d29917f693560ee39290e80b6fbacf3e589a926c7ef2fa`; the manifest
SHA256 is `963788eb494714f7a68fccf7ca0087a7e31415ecee85bd94a592483470bd9420`.

## Owner and mechanism reuse

The directly inspected current-frame owner chain remains geometry/masks → preprocessing → S5-A
Foam → S5-B raw observations/proposals/hypotheses → typed current observation → serialized
canonical reducer → projection. The adjacent retained owners are the S5-B observational-equivalence
fixtures, historical glare negatives, and S6-D4 accepted-Foam spatial protection.

The experiment reuses merged diagnostic code rather than reimplementing either mechanism:

1. **P0** is exact current production diagnostic behavior from `s11_evidence_probe.run_variant`.
2. **P2 only** uses the same `_p2_no_interface` and `_evaluate_current` path accepted as diagnostic
   evidence in PR #79. P2 can change positive no-interface to ambiguity but cannot create Oil.
3. **Spatial only** is exact PR #80 `run_spatial_variant`, including its relative-phase candidate,
   five sectors, current glare/Foam exclusion, bounded local row search and non-degenerate path gate.
4. **P2 + Spatial** begins from P2. Only when P2 leaves an ambiguous current observation does it
   ask the existing P3 route for the same relative-phase canonical candidate under P2 no-interface
   semantics. A numeric candidate is retained only when the unchanged PR #80 spatial gate accepts it.

The combined experiment never constructs a new numeric Y. Any candidate comes from the existing
typed/canonical diagnostic route and the spatial stage may only retain or reject it. This remains a
diagnostic composition outside production ownership; it is not authority for post-owner production
injection.

## Native comparison

All four conceptual states were directly executed on the same 13 usable native truth rows.

| variant | numeric Oil | matched MAE | interpretation |
| --- | ---: | ---: | --- |
| P0 | `7/13` | `4.428571 px` | current production baseline |
| P2 | `7/13` | `4.428571 px` | no native numeric delta |
| Spatial | `9/13` | `4.888889 px` | PR #80 recoveries retained |
| P2 + Spatial | `9/13` | `4.888889 px` | identical to Spatial on native corpus |

The two native Spatial recoveries remain `sample2:30 → 599` (`7 px` error) and
`sample2:60 → 598` (`6 px` error). P2 does not alter either result and the combined route adds no
new native recovery. The remaining native misses are unchanged: `base_sample_1:156`,
`base_sample_1:240`, `sample2:0`, and `sample3:900`. Existing P0/Spatial accepted anchors do not
move under the combined diagnostic.

## Known P2 false-no-interface interaction cases

The probe proportionally reuses only the low-exposure transforms where PR #79 directly showed a
P2 difference. These are metamorphic diagnostics, not additional product truth.

| transform / case | P0 | P2 | Spatial only | P2 + Spatial |
| --- | --- | --- | --- | --- |
| `0.60×` / `sample3:900` | no-interface | ambiguity | no numeric | no candidate / no numeric |
| `0.45×` / `base_sample_1:144` | no-interface | ambiguity | no numeric | no candidate / no numeric |
| `0.45×` / `sample3:900` | no-interface | ambiguity | no numeric | no candidate / no numeric |
| `0.45×` / `sample3:1035` | no-interface | ambiguity | no numeric | no candidate / no numeric |

P2 therefore performs the expected semantic repair in all four cases, but none exposes a canonical
relative-phase candidate for the Spatial gate. The measured interaction is **false no-interface →
ambiguity only**, not false no-interface → ambiguity → numeric Oil.

A separate low-light row demonstrates why this distinction matters. At `brightness 0.60`,
`sample3:1035` is already P0 ambiguity; Spatial recovers `245 px` versus truth `243 px`, and the
combined route keeps the same `245 px`. That is an existing Spatial recovery, not a P2-enabled
interaction recovery. At `brightness 0.45`, P2 is required to convert that scene from no-interface
to ambiguity, but the relative candidate then disappears, so the combined route remains non-numeric.

The full bounded transform aggregates are:

| transform | P0 | P2 | Spatial | Combined | combined-only |
| --- | --- | --- | --- | --- | ---: |
| `1.00×` | `7/13 @ 4.43` | `7/13 @ 4.43` | `9/13 @ 4.89` | `9/13 @ 4.89` | `0` |
| `0.60×` | `1/13 @ 11.0` | `1/13 @ 11.0` | `2/13 @ 6.5` | `2/13 @ 6.5` | `0` |
| `0.45×` | `2/13 @ 11.0` | `2/13 @ 11.0` | `2/13 @ 11.0` | `2/13 @ 11.0` | `0` |

## Protection evidence

The combined mechanism was directly exercised against retained negatives rather than inferring
protection from the two parent probes.

- S5-B observational-equivalence collisions: `0/16` combined false numeric Oil.
- The P3 candidate exists on `14/16` collision scenes, but all 14 remain rejected by the unchanged
  Spatial gate as `degenerate_scalar_row`; latent-glare/Oil pair outputs remain equal.
- Historical glare negatives: `0/21` combined false numeric Oil.
- D4-style structural/Foam stress scenes: `0/9` combined false numeric Oil.
- S5-A Foam remains accepted and position-identical to P0 on all `9/9` structural/Foam scenes.

The prior low-light warning also remains closed. On `sample4:450` at brightness `0.60` and `0.45`,
the P2-relative candidate is again `804 px`, a `48.5 px` truth error, but the unchanged spatial
protection rejects it as `candidate_lacks_symmetric_phase_window`. The combination therefore adds
no new material-error case in the bounded interaction evidence.

## Flat / near-horizontal claim limitation

PR #80's `path_span > 1 px` condition remains a conservative diagnostic discriminator only. This
probe does not promote it to a physical statement that valid Oil must slope or curve. A real
near-horizontal Oil surface can legitimately produce a flat cross-ROI path, and the current S5-B
collision fixtures also produce flat/near-flat paths. The gate is useful here only because it asks
whether the candidate carries information beyond the already-known scalar row fact.

Consequently, `no material interaction` does not prove that P2 and every future production spatial
representation are intrinsically non-complementary. It proves only that **the already-probed PR #80
diagnostic mechanism**, with its conservative non-degeneracy gate unchanged, gains no additional
numeric recovery from P2 on the current reproducible interaction evidence.

## Resource / compute boundary

The combined mechanism adds no retained raster, cross-frame history, per-Glass state, setting,
schema, or dependency. When P2 is not ambiguous, no combined spatial fallback is needed. When P2
is ambiguous, the diagnostic may perform one existing relative candidate pass; only a canonical
numeric candidate reaches the unchanged five-sector path gate.

The spatial deterministic bound remains `5 × 25 = 125` sector-row evaluations per candidate, with
phase windows bounded by the existing broad scale and retained temporal state `0`. The comparison
harness deliberately executes P0, P2, Spatial-only and Combined separately to attribute interaction,
so its wall time is not a production cost estimate. A later production design would need its own
exact-owner compute evidence if authorized.

## Decision

**Conclusion: `no material interaction` in the bounded reproducible probe.**

P2 and Spatial remain independently meaningful, but their tested effects are additive only in the
weak sense of preserving separate protections: P2 converts known exposure-driven false no-interface
to fail-closed ambiguity, while Spatial preserves its native and one already-ambiguous low-light
recovery. P2 does not expose any new accepted Spatial candidate in the four cases where it actually
changes current-observation semantics. Combined-only numeric recovery is `0` across native,
`0.60×`, and `0.45×` evidence.

This result does not invalidate P2 as a separate no-interface semantics repair candidate or PR #80
Spatial as a separate positive-evidence candidate. It does mean the present corpus provides no
interaction evidence that requires them to be implemented as one production mutation for numeric
Oil recovery. Production scope, sequencing and Lane remain Orchestrator decisions.

No production/shared-contract boundary was crossed by this probe. Applying P2 to production would
still change S5-B no-interface/observability meaning and therefore remains a separate authority
question; integrating Spatial into production likewise requires a fresh production mutation design.

## Validation and intentional non-runs

Direct development evidence includes the 39-row bounded interaction matrix (`13` truth rows ×
three retained brightness states), all four known P2 semantic-rescue cases, the retained 16-scene
collision corpus, 21 glare negatives, 9 structural/Foam scenes, and the two known `sample4:450`
low-light false-boundary warnings.

- `python -m pytest -q tests/test_s11_p2_spatial_interaction_probe.py` → `8 passed` during development.
- Deterministic manifest fingerprint and SHA256 are recorded above.
- Final stabilized targeted-suite and `git diff --check` results belong to the Worker handoff after
  the exact final commit is prepared.

Intentionally not run: the prior 416-result photometric matrix, full canonical/E2E, Windows
packaging, private company field-video acceptance, production P2/Spatial mutation, temporal history,
offline trajectory reconstruction, optical flow/background subtraction, ML, segmentation, or new
dependency experiments.

## Next gate

The exact next authority is **Lane B Orchestrator exact-head bounded review**. The Orchestrator owns
whether P2 and Spatial should remain separate production candidates, whether either source mutation
is now justified and at what Lane, or whether single-frame probing should stop and the separately
owned offline temporal trajectory probe should begin. This Worker does not merge, synchronize
`main`, Close S11/S11-A, or claim detector/general-field accuracy PASS.
