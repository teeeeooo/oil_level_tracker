# S11-R13 Phase-Identity Recovery Architecture

**Implementation status:** implemented and locally validated; exact-head
private-Windows validation pending.

## Purpose

R13 replaces the R12 authority leak and proposal gap identified by the private
Windows replay. It is not a threshold layer over R12. The retained product
output is still two independently observed series: Oil/air interface and Foam
front.

R12 behavior retained as contract:

- motion alone cannot create Oil authority;
- every numeric coordinate is an exact selected same-frame candidate;
- user-confirmed Artifact templates are candidate-local hard negatives;
- broad Foam/material masks are evidence, not topology truth; and
- Oil and Foam validity are independent.

R13 replaces the active semantic-anchor, lower-reserve, trajectory identity and
versioned diagnostic seams that failed Windows.

## One phase-identity decision

Every admitted Oil proposal receives one typed phase identity before authority
or trajectory evaluation:

- `DIRECT_INTERFACE`: sufficiently strong localized phase boundary with typed
  clean/available contradiction evidence;
- `ORDERED_LOWER_INTERFACE`: strong Oil boundary below an active independently
  observed Foam/material front, with normal vertical order and independent
  representation corroboration;
- `CONTINUATION_ONLY`: usable proposal lacking independent identity; or
- `OPPOSED_MATERIAL`: same physical row as active Foam/residue material.

The decision owns its reason and failed gates. Candidate-family names do not
change the gate. In particular, an ordinary `oil_hypothesis` cannot bypass
material-texture conflict merely because it is not a material-path candidate.

`ORDERED_LOWER_INTERFACE` is the explicit exception to a blanket material-mask
conflict veto. The broad mask may legitimately cross the real lower Oil row.
The exception therefore requires all of:

- an active bounded Foam/material identity above the candidate;
- normal front order and a minimum separation;
- strong direct boundary and bounded ambiguity/artifact evidence; and
- same-frame corroboration from an independent proposal family.

Geometric separation alone remains non-authoritative.

## Authority replacement

Authority consumes the typed identity, not candidate source/version.

- `DIRECT_INTERFACE` or `ORDERED_LOWER_INTERFACE` may become an anchor when the
  route-specific evidence gates pass.
- A semantic corridor may corroborate an identity but cannot manufacture one.
- High material-texture conflict blocks ordinary semantic/boundary anchor
  authority uniformly across all families.
- `CONTINUATION_ONLY` may be retained in an anchor-backed component but cannot
  seed it.
- `OPPOSED_MATERIAL` is candidate-only and can never publish as Oil.

The R12 `semantic_sequence_anchor` direct authority route and versioned
`distinct_lower_reserve` policy are removed. Historical enum strings may still
be read from old bundles, but new R13 control flow does not emit them.

## Trajectory and recurrence identity

Trajectory edges require both bounded displacement and compatible phase
identity. A continuation can attach to a neighboring identified Oil component,
but two candidate tracks cannot exchange anchor support through an opposed
Foam/residue row.

Recurring-track opposition remains a static-structure defense. It may lower an
unidentified continuation, but it cannot demote a current-frame independently
identified lower Oil solely because another longer upper track exists. Explicit
Artifact match, invalid topology or failed direct identity still wins.

Qualified anchors, trajectory membership and final run bounds all use the same
identity object. This eliminates the R12 mismatch in which semantic anchors
seeded one component while lower-reserve and Foam identity were merely debug
features.

## Base proposal recovery

R12 high recall still requires a strict local maximum. Private Base has no
proposal near reviewed Oil at 540 and 674 s, so sequence policy cannot repair
it.

R13 adds a bounded phase-transition scan alongside existing row peaks. It uses
multi-scale intensity change across rows and horizontally distributed sector
support. Each vertical band may reserve a strong diffuse transition even when
the response is not a strict one-row maximum. User Artifact templates are
applied before sequence admission.

The scan is proposal-only:

- it has a fixed per-frame budget and non-maximum separation;
- it runs only through the calibrated high-recall lane;
- it cannot become an anchor because it was reserved or because it moves; and
- it must acquire `DIRECT_INTERFACE` or `ORDERED_LOWER_INTERFACE` from the same
  typed authority contract as every other family.

No private timestamp, Y coordinate, Glass ID or video name enters the scan.

## Graph validity

The graph model already stores validity per point. The renderer must convert a
finite but invalid point to a plotting gap independently for Oil and Foam.
Display-only gap bridges may connect valid Oil anchors according to the existing
review contract; invalid points never become anchors. Raw CSV/debug coordinates
remain unchanged for diagnosis.

Initial-state hold remains a disclosed state band when no numeric Oil exists.
It does not create a coordinate.

## Trace and compatibility cleanup

R13 basic trace uses stable semantic names:

- evidence availability;
- phase identity/reason/failed gates;
- authority tier/reason/failed gates;
- candidate-local Artifact result;
- cluster and trajectory component support;
- node selected after best path, continuation bound and suppressors; and
- final selected source/Y.

Active R11/R12 compatibility aliases that have no production reader are
deleted rather than duplicated. Old result-bundle reading and legacy public
flags remain compatible where they are part of stored external data. Candidate
source strings may be accepted at the evidence adapter boundary, but new
control flow and new trace fields are not version-named.

## Ownership and performance

- calibrated proposal generation remains in `oil_supplemental_path.py`;
- typed raster evidence remains in `oil_candidate_evidence.py`;
- phase/composition identity is a separate owner consumed by authority and
  trajectory;
- `oil_candidate_authority.py` owns authority only;
- `oil_observation_resolver.py` orchestrates stages and projects results; and
- the Result Review widget owns validity-aware plotting only.

The new proposal scan reuses preprocessed rasters and bounded box/row
operations. It must not add a per-candidate image pass. Detector and completed
window resolver time are measured separately and compared with R12 in the same
session.
