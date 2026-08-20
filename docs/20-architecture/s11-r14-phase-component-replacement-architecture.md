# S11-R14 Phase-Component Replacement Architecture

## Purpose

R14 replaces R13's local-identity and component-free path policy. One detector
must support Base and Accum. Product code must not contain field-video Y bands,
timestamps or Glass-specific branches.

## Candidate proposal and calibration

Artifact templates are rejection data only. Their count must not enable a
generator or change its proposal budget. The calibrated high-recall and
phase-transition lanes run with fixed bounded limits so Base proposal recall is
available with or without templates. Template matching remains candidate-local
and cannot grant authority to an unmatched row.

Proposal recall is reported independently from authority and publication.

## Phase identity

R14 has three usable states: `CONTINUATION_ONLY`, `DIRECT_INTERFACE` and
`ORDERED_LOWER_INTERFACE`; opposed Foam material remains ineligible for Oil
identity.

- A direct identity requires texture-clean phase evidence. Calibrated/scan
  proposals additionally require a genuinely different representation near the
  same row. A scan by itself stays continuation-only.
- An ordered-lower identity is a short-lived composition of a directly
  detected Foam seed and the first independently supported interface below it.
  The seed must be at most three seconds old, the row must meet minimum
  separation and cross-representation support must be at least 0.12. A stale
  Foam-material continuation is opposition evidence only and never grants Oil
  authority.
- Direct interfaces remain texture-clean. The recent-Foam ordered-lower case is
  the one bounded exception because the accepted Foam/material mask can overlap
  the physical Oil row and therefore make material-texture conflict high. Only
  the nearest plausible lower interface may anchor; deeper rows are demoted to
  continuation-only.
- Motion, persistence, source name and candidate density never create identity.

## Track opposition

Track recurrence is a ranking penalty. It may hard-demote a candidate only when
paired with candidate-local artifact, optics, material-texture or phase
contradiction. A low-conflict direct interface is not changed to candidate-only
by recurrence alone. This protects a real level that remains stationary.

## Component-owned trajectory

The anchor/trajectory graph assigns a deterministic component identifier to
each supported candidate. Edges require adjacent sampled frames, bounded Y
motion and compatible phase identity. A continuation-only row may extend one
compatible component but cannot join two independently identified components.

Oil-to-Oil Viterbi transitions require equal non-empty component identity.
Changing component requires an UNKNOWN observation followed by a new
independent anchor. Continuation bounding splits runs whenever component identity
changes, and each sub-run must contain its own independent anchor. This is not a
large-distance penalty and does not interpolate missing coordinates.

A completed-fill barrier can reopen only when an observed component enters
through the upper 40% of the Glass and shows net downward progress with at least
0.60 directional agreement inside the bounded lookahead. Moving internal caps
cannot release the barrier merely because they form a coherent component.

## Publication and observability

Every numeric Oil remains one eligible selected candidate from the same frame.
Debug trace exposes phase identity, component identifier, component transition
rejection and each post-path stage. Final numeric counts use final resolved kind
and source Y only.

## Artifact editing UX

Confirmed templates support normal single selection, Shift range selection,
Ctrl/Cmd toggle, select-all, clear-selection and one bulk deletion. All selected
templates are highlighted together. Changes remain on the editor's private
copy until Apply and then persist through the existing Recipe repository.
