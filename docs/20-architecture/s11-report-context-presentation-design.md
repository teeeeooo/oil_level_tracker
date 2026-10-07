# S11 Report Context Presentation Design

This bounded design implements the reviewed namespace/wording portion of the
[third audit](../70-reference/s11-audit-2026-10-07/s11-third-audit-report-context-work-spec-2026-10-07.md).
The [report architecture](result-observation-report-architecture.md) owns the
durable report contract; its [validation](../30-validation/result-observation-report-validation.md)
owns acceptance. The [Work Plan](../00-project/work-plan.md) owns adoption status.
The supplied prototype and recovery archives remain immutable historical inputs.

## Namespace and observation wording

`report_presentation.py` remains the owner. Exact legacy Oil flags retain the
R7 anchor-only rule; unrelated Foam flags do not suppress modern Oil extrema.
One report-local eligible-set helper serves both landmarks and narrative, so a
continuation-only legacy stream cannot fall back to unrestricted summary extrema.
This does not change domain-event or initial-state compatibility predicates.

Endpoint comparison is explicitly qualified, including intermediate variation
and singleton observations. Foam labels describe observation start/interruption,
give last-observed and next non-Foam timestamps, and do not certify physical
formation/disappearance. Existing state-only Foam evidence remains state evidence;
wording does not manufacture a front coordinate. Episode formation is unchanged.

The first change is limited to namespace/wording. The second bounded unit below
adds static gap display and scene context. Tracking samples, detector source,
Recipe/truth, event meanings, judgment and field disposition are unchanged.

## Static gap display and scene context

The report adopts the prototype's two-source-second Oil connection cap as an
explicit display policy. It applies both to missing-row bridges and timestamp
jumps, preserving all anchors. The shared series helper remains uncapped by
default so Result Review keeps its existing behavior. The report trend sentence
does not infer mixed observed motion from pairs across a longer gap.

The existing presentation builder selects the longest internal gap per Glass,
with earliest tie-breaking, and emits at most three `ReportSceneCapture` requests.
Endpoints use their stored samples; the midpoint has no sample and no Oil/Foam
guides. These are presentation requests, not synthetic events or samples. The
existing capture store, cancellation/progress and staged bundle path serve them.
Scene-only requests have a distinct cache identity from annotated landmarks.
The report template exposes them separately with observation-qualified captions.

This extends the supplied prototype with bounded scene context in the existing
owners. It does not claim the two-second value is calibrated, certify physical
identity or make static/interactive presentation identical. Source/report interval
review remains the next decision-bearing step; current field gates remain intact.

## History Review

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R1 observed-run/display-bridge distinction; R7 anchor-only extrema; current independent Oil/Foam validity; the three supplied 2026-10-07 audits and report-context prototype.
- Prior mechanisms rejected: Foam flags granting Oil authority, unrestricted fallback from legacy anchor eligibility, numeric interpolation/carry, treating missing Foam as physical disappearance, and promoting local report checks into field success.
- Preserved contracts: immutable stored observations, same-frame provenance, independent series, actual legacy anchor protection, bounded existing episode/landmark selection, unchanged event history and separate field qualification.
- Difference from prior failures: repair report interpretation inside its existing owner without changing upstream identity, numeric publication, detector thresholds or candidate selection; summary and landmarks share extrema eligibility, long display connections are bounded and context-only captures cannot create measurements.
- Logic-map impact: NONE — existing runtime owners and pipeline edges remain unchanged.
- Failure-registry impact: NONE — existing F09/F10 guards apply; no failed detector mechanism is retired or promoted.
