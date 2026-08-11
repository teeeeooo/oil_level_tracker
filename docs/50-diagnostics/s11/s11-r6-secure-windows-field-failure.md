# S11-R6 Secure-Windows Field Failure

**Status:** `FIELD FAIL — PRIVATE RASTER UNAVAILABLE LOCALLY`

## Scope and oracle

This diagnostic records the operator's direct source-video/LVLM comparison for
the exact private Base/Accum workflow after the locally accepted R6 replay. The
private video cannot leave the secure Windows environment, so the observations
below are field evidence supplied by the operator rather than locally
reproducible truth. The source review remains the physical oracle; aggregate
coverage and old fingerprints do not override it.

The active repair is specified by the
[R7 Evidence-Tiered Trajectory Architecture](../../20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md).

## Field outcome

| Glass | Valid samples | Total | Coverage | Dominant state |
|---|---:|---:|---:|---|
| Base | 121 | 601 | 20.1% | `UNKNOWN_REVIEW` 79.9% |
| Accum | 19 | 601 | 3.2% | `UNKNOWN_REVIEW` 96.8% |

R6 removed R5's false prior-only coverage but did not recover the field
trajectory. Base remained mostly unavailable and still produced wrong low-level
Oil/Foam observations. Accum remained unavailable through the visible rise and
published a false draining boundary while the Glass was empty.

## Direct-review contradictions

### Base

- The Glass starts full, contains no Foam, later exposes a descending interface
  and recovers.
- R6 did not publish FULL or the visible 85–90% level over most of the run.
- A low-confidence ambiguous hypothesis near source Y `221.6` was accepted as
  continuous Oil and created `OIL_DROP_START` at the wrong level.
- A later ambiguous shadow near zero produced a false minimum although direct
  review kept the real interface materially below that row.
- Strong Foam publication near zero combined two wrong observations: fixed
  glare/reflection as Foam and a shadow row as Oil.

### Accum

- The Glass starts empty, later rises, has bounded turbulent Foam, reaches a high
  and drains.
- R6 missed the visible rise and stayed almost wholly unavailable.
- In the empty interval, several generic material-path candidates were generated
  from internal reflection/gradient. A wrong prior accepted row later appeared
  in tracking output as draining Oil.
- The high near `689 s` was visually supportable and retained strong narrow-edge
  evidence, proving that useful field signal exists in at least part of the
  sequence.

## Source audit

### 1. Eligibility does not express semantic authority

Production hypothesis projection sets `sequence_eligible` from visibility,
availability and glare/exclusion/border conflict. Boundary likelihood, artifact
dominance, ambiguity dominance and the hypothesis label do not determine the
bit. Consequently an ambiguous hypothesis is admitted to the final lattice even
when ambiguity is its strongest current-frame explanation.

Admission is useful for preserving alternatives, but R6 has no separate
candidate-only versus anchor authority. That missing type boundary is the first
defect.

### 2. Current-frame temporal selection becomes a final anchor

`OilObservationResolver` treats an existing candidate `selected` by the old
serialized current-frame tracker as a semantic anchor. A selected candidate can
become `direct_anchor` without the strong-anchor ambiguity ceiling, and selected
semantic candidates receive `anchor_support = 1.0` even when they are not part of
an independently qualified cluster.

The final emission then adds both a direct-anchor bonus and an anchor-support
bonus while ambiguity receives a substantially smaller penalty. Therefore
`continuous_shadow_boundary` and `bounded_shadow_reacquisition` are not merely
debug history: they can seed the R6 completed-window truth. This violates the R6
claim that the current-frame reducer is preview/evidence only.

### 3. Conservative run censoring is independent of anchor quality

After path selection, R6 removes every Oil run without a qualified direct anchor
and censors candidate-bearing intervals more than a small fixed horizon from
anchors. This produces very high UNKNOWN coverage on weak transparent Oil.

The combination is internally inconsistent: a few selected ambiguous candidates
receive excessive authority, while many same-frame continuation candidates are
discarded solely because strong anchors are sparse.

### 4. Initial-state correction removed legitimate interpretation

R6 correctly stopped the R5 sequence owner from emitting prior-only valid
FULL/EMPTY rows. It then made every R6 stream `NOT_APPLICABLE` to the existing
Initial-State Retrospective Reconstruction owner. This also removed the desired
product behavior: once a trusted descending/rising boundary trajectory confirms
the initial FULL/EMPTY context, the preceding unresolved prefix should be
interpreted as that state with explicit inference provenance.

This is not detector evidence and must not increase observed detector coverage,
but it is legitimate result interpretation and report context.

### 5. Foam episode confirmation remains too weak

R6 rejects a single isolated component, but a grouped episode needs only one
frame crossing the registered internal-motion threshold. A fixed glare component
with one exposure/registration disturbance can therefore become public Foam.
The Base false Foam shows that static overlap plus one dynamic sample is not a
sufficient change-point proof.

## Interpretation of the score report

Boundary, artifact and ambiguity likelihoods are correlated evidence terms, not
calibrated mutually exclusive probabilities. The rule cannot simply be
"ambiguity is numerically largest, therefore reject": the visually correct Accum
high also has high ambiguity. The valid correction is an authority split:

- weak/ambiguous evidence may remain a candidate;
- it may continue a path only inside independently trusted anchors;
- it cannot start, reacquire or anchor a path by current-frame continuity alone;
- only trusted anchor observations may independently create extrema and lifecycle
  events.

## Disposition

R6 fails the secure-Windows gate. Its local checked-video evidence remains
historical mechanism evidence, not current field acceptance.

The next repair must replace, rather than tune around, the final authority seam:

1. remove current-frame `selected`/tracker outcome from final anchor authority;
2. introduce explicit candidate, continuation and anchor evidence tiers;
3. preserve same-frame coordinates while allowing bounded sequence-supported
   continuation between real anchors;
4. restore separately persisted initial-state retrospective interpretation for
   the leading prefix;
5. require multi-frame Foam onset/material evolution; and
6. prevent continuation-only observations from independently creating events or
   extrema.

If direct review proves that the real interface is absent from the raw candidate
lattice over visually clear field transitions, stop scoring work and reopen
representation/acquisition instead of lowering global thresholds.
