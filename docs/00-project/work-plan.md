# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Trust-boundary redesign starting head:** `b12cd4d51d9b6ffef7abea390ac669560f89b116`
- **Starting parent:** `e937a4b77319377598c6927a9967559bf249e631`
- **Third S5-B2 audit:** `AUDIT: FAIL`
- **Decision:** Stop the narrow field-validator repair loop and redesign the internal production-result trust boundary
- **Current gate:** Independent trust-boundary redesign architecture audit
- **Source implementation:** Blocked until architecture audit `PASS`
- **Controlled comparison:** Blocked until implementation re-audit `PASS`

This is the operational SSOT for the active milestone. Closeout results follow the [closeout policy](./closeout-policy.md); branch-local work is not a formal completion declaration, and this plan does not use formal `DONE` status.

## Gate history and redesign trigger

S5-B1 established immutable observations, bounded proposals, continuous semantic evidence, typed current observations and Glass-local temporal reasoning. Its independent architecture/source gate passed and authorized the later S5-B2 production cutover, but not accuracy acceptance or merge readiness.

S5-B2 then cut production oil-boundary/no-interface/temporal ownership over to the typed pipeline. Three independent audits repeatedly found cross-field coherence gaps in the generic `OilShadowFrameResult` and `ShadowTemporalDecision` representation.

The confirmed failure classes include class/status/identity/Y disagreement, forged current internal kind, frame availability conflicting with accepted status, failure results producing numeric oil or selection, unauthorized smoothing clear, unavailable no-interface evidence accepted as positive evidence, resource-count disagreement and post-construction non-finite scalars.

The third audit returned `AUDIT: FAIL`. Additional field-level validator repair is no longer the accepted path because each patch depends on manually remembering another cross-product invariant while the generic model continues to represent contradictory states.

## Interrupted Worker recovery

The first trust-boundary redesign Worker was interrupted when every Codv endpoint returned `Resource not found: codv.<function>` during rollout. It left an uncommitted partial replacement of `docs/20-architecture/s5b-oil-boundary-hypothesis-architecture.md`; `docs/00-project/work-plan.md` remained unchanged.

The recovery session performed real process/shell and file-read health calls before touching the repository. It then verified:

- local branch identity and required exact head/parent;
- remote feature head equality at `b12cd4d51d9b6ffef7abea390ac669560f89b116`;
- exactly one modified architecture document;
- no staged changes and no untracked files;
- a documentation-only partial trust-boundary redesign diff.

Only the interrupted architecture document was restored from `HEAD`. No checkout reset, clean, branch switch, stash or unrelated-file recovery was used. The worktree was confirmed clean before the redesign was restarted from the exact head.

## Accepted architecture direction

The architecture document now requires a closed discriminated internal model:

- current observation variants derive `kind` from concrete class;
- temporal decision variants derive status, observation kind and smoothing action;
- boundary smoothing clear derives only from `reacquired` acceptance mode;
- ambiguous and reacquisition-pending decisions structurally lack clear authority;
- successful and failed pipeline frames replace the generic availability/failure pair;
- one trust-boundary normalizer reconstructs a fresh canonical production outcome;
- detector, fill-state, tracker, flags and debug consumers read only the canonical outcome;
- old generic fields and the manual cross-product validator are removed after atomic consumer cutover.

The normalizer must freshly validate finite scalars, canonical identity/content/Y, positive no-interface availability, success/failure coherence, actual tuple/resource counts, limits, failure-frame empty evidence, candidate/debug JSON safety and selected canonical membership.

## Required implementation and validation sequence

Proceed in the following order only after the architecture audit returns `PASS`.

1. Internal observation variants and derived properties.
2. Temporal decision variants.
3. Pipeline success/failure frame variants.
4. Canonical production normalizer.
5. Detector/fill-state/debug consumer cutover.
6. Old generic fields and manual validator removal.
7. Systematic adversarial/property tests.
8. Compatibility regression.
9. Independent exact-head source audit.
10. Controlled comparison.

Old and new models must not simultaneously influence production candidate selection, numeric oil, smoothing/tracker action or fill-state input. Legacy oil generation, scoring, no-interface evaluation and temporal ownership remain prohibited as production fallback.

The systematic test matrix must cover legal variant construction, structurally absent illegal fields, derived status/kind/action, outer success/failure mutation, identity/content/Y mutation, finite/range mutation, evidence availability, resource counts/limits, smoothing action, candidate provenance, JSON safety and deterministic property-style cross-products.

Every malformed result must fail closed to unavailable/failure with no numeric oil, no selected candidate, no tracker update, no unauthorized smoothing clear, no legacy fallback and no input-raster mutation, while preserving independently valid S5-A Foam processing.

## Compatibility and blocked work

The redesign does not change observation extraction, proposal/hypothesis algorithms, likelihoods, thresholds, temporal transitions, Glass-local state, external `PhaseDetection`, Recipe/settings persistence, benchmark/truth/fixture/result/CSV/debug schema versions, detector version, S5-A Foam or dependencies.

Source implementation is blocked until the independent trust-boundary redesign architecture audit returns `PASS`. Controlled comparison remains blocked until the resulting source exact head passes independent re-audit. Canonical validation, Windows/manual GUI validation, packaging validation, merge and cleanup are outside the current gate.

## Deferred controlled accuracy findings

The previously recorded controlled oil failures remain separate deferred findings and are not hidden, relaxed or reclassified by this architecture work:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

These findings concern detector accuracy and temporal recovery evidence. They do not justify weakening the production-result trust boundary and are not evaluated in this documentation-only task.

## Documentation validation contract

Before commit, this recovery Worker must verify:

- changed files are exactly the two governed Markdown documents;
- complete diff has been reviewed;
- `git diff --check` passes;
- tracked Markdown files end with a final newline;
- relative links and path case resolve;
- no source, test or dependency delta exists.

After the ordinary fast-forward commit and push, local and remote feature heads must be equal and the worktree clean.

## Next action

Perform an independent trust-boundary redesign architecture audit against the immutable resulting documentation head. That audit decides whether source implementation may begin; it does not authorize controlled comparison, canonical validation, merge or cleanup.

## Latest recorded closeout

- **Starting exact head:** `b12cd4d51d9b6ffef7abea390ac669560f89b116`.
- **Starting parent:** `e937a4b77319377598c6927a9967559bf249e631`.
- **Third audit:** `AUDIT: FAIL`; generic typed result coherence remains structurally unsafe.
- **Recovery:** Interrupted partial architecture draft was exclusively restored after exact-state verification.
- **Current artifact:** Documentation-only discriminated-variant and canonical-normalizer redesign.
- **Current gate:** Independent trust-boundary redesign architecture audit.
- **Deferred findings:** Two controlled oil accuracy failures remain unchanged.
