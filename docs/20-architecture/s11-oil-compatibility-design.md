# S11 Legacy Oil Compatibility

## Responsibility and scope

The exact legacy Oil namespace is owned beside `TrackingSample` in
`domain/results.py`: `has_legacy_oil_flags` and `has_legacy_oil_anchor`.
Event derivation, report eligibility and initial-state reconstruction reuse this
owner. This consolidates a duplicated compatibility decision in existing result
semantics, without adding a resolver or changing sample serialization.

Only normalized `R7_RESOLVED_OIL`, `R7_OIL_ANCHOR` and `R7_OIL_CONTINUATION`
select legacy Oil authority. An unrelated `R7_FOAM_*` or unavailable marker alone
cannot select it. Actual legacy streams retain their existing anchor protection;
no-anchor streams gain no extrema/drop/crossing or appearance authority.

`domain/events.py` retains its event ordering, debounce, drop/recovery thresholds,
contiguous-run and anchor predicates. Modern stored Oil can now produce the
same events with or without unrelated R7 flags. `events.csv` and Review event
lists intentionally change when those flags previously suppressed Oil events.
These are derived observed events, not certification that the detector found the
physical Oil boundary. The returned sample4 review identifies incorrect Oil
observations; this compatibility repair neither hides nor corrects them.

Initial-state reconstruction uses the same namespace. For modern streams,
canonical entrance/direction and hard-barrier handling apply even with R7 Foam
flags. Actual legacy Oil retains anchor-grade direction, its existing unavailable
prefix handling and separate provenance. Current-run confirmation, all-missing
presentation-only hold, opposite-state conflict, immutable observed samples and
observed-only RECOVERY judgment remain unchanged. Confirmed FULL/EMPTY inputs
may therefore receive corrected retrospective outcomes; this scope is explicitly
broader than event enumeration alone.

The [retrospective architecture](initial-state-retrospective-reconstruction-architecture.md)
and [validation](../30-validation/initial-state-retrospective-reconstruction-validation.md)
own the full state contract; the [report architecture](result-observation-report-architecture.md)
owns presentation. No detector candidate, authority, coordinate, score, validity,
Foam episode, recipe, truth or display-gap policy is changed.

## Verification and rollback

Require modern Oil with/without Foam-only flags to produce identical events and
FULL/EMPTY reconstruction, including hard barriers. Preserve legacy anchor and
continuation controls, observed-sample equality, both appearance directions and
shared official/full/interval outcome entry points. Run event/judgment/report/
Review-reader regressions and four fixed-window application/bundle runs. Compare
all 299 tracking rows, list every event addition/removal, verify Foam events and
judgment, and join the persisted Review event delta to the fixed-row event probe.
The four UNKNOWN-prior videos do not substitute for confirmed-prior controls.
Rollback is one logical commit revert, restoring all three compatibility consumers
together. Previously saved bundles retain their historical events.

## History Review

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: third-audit fixed-299-row event probe; report namespace repair; legacy anchor/continuation protection; retrospective FULL/EMPTY versus numeric RECOVERY responsibility; returned sample4 incorrect/correct Oil observations.
- Prior mechanisms rejected: treating every R7 flag as Oil authority, making Foam grant or erase Oil authority, rewriting stored observations to hide false events, and counting added events as physical accuracy.
- Preserved contracts: exact stored coordinates/provenance, independent Foam, unchanged event thresholds, legacy anchor protection, run-scoped prior confirmation, separate retrospective state and observed-only RECOVERY.
- Difference from prior failures: a shared exact namespace corrects downstream compatibility without adding a score, private case rule, coordinate repair or detector authority.
- Logic-map impact: NONE — existing publication/presentation responsibilities and callers remain in place; a duplicated flag predicate is consolidated in the existing sample domain.
- Failure-registry impact: NONE — F09/F10 guards remain active; no physical detector failure is retired.
