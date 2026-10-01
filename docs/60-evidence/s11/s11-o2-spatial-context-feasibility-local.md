# S11 O2 candidate-relative spatial-context feasibility

Base: `3a37805c329fef1df0ed9f5480619a9fd2ea20b2`.
Scope: local source review and actual-extractor counter-controls after the
[bounded Windows inspection](s11-o2-spatial-context-windows-run-001.md#three-native-centers-reconciled--bounded-inspection-closed).
No private raster was opened here. No production, scoring, artifact-spec, label,
or Windows execution change. FIELD FAIL and O2 acceptance remain unchanged.

## Decision

Retain the ordered strip probe as a diagnostic measurement. Do not implement
a candidate-identity score from strongest peak, nearest peak, return distance,
or sustained brightness on the current evidence. Candidate-relative coordinates
can describe where a measured feature lies; they do not identify which feature
is Oil. This is a bounded no-promotion decision for this proposal, not a proof
that all spatial classifiers are impossible or that no empirical benefit could
ever be validated.

Close the one-dimensional profile-to-identity feasibility investigation without
another private extraction. It has established information retention, not the
physical meaning required to select an identity mechanism. W4's identity
challenger remains open; the existing local-position result is unaffected.

## Existing responsibility and reuse audit

| Owner | Already available | Consequence for a challenger |
|---|---|---|
| `oil_interface_witness._center` and diagnostics `_measure_sector` | Candidate/native geometry, four side bands across scales, local gradient peaks and support | A central row excluded from band means can still affect existing peak fields. Band coverage alone is not all of O1 |
| Entire `FrameInterfaceWitness.candidates` inventory | Other candidates sample their own neighborhoods | Outside one candidate's bands does not imply absence from the whole packet |
| `s11_spatial_context_probe.measure_context` | Full ordered raw-gray row means/counts, shared exact-X profiles and point references | Candidate-relative row offsets can be computed from existing source_y; another extraction owner is unnecessary |
| `row_features.masked_band_intensity_profiles`, `oil_shadow_observations._broad_profiles`, `oil_spatial_fallback._relative_broad_summary` | Existing rowwise contrast profiles and bounded proposal-relative broad summaries | A new broad contrast score is not a novel observable merely because it uses relative coordinates |
| `oil_material_path._material_row_profile` / `_terminal_material_partition` | Material-map row profile and multi-depth upper/lower summary | Different raster semantics; not Oil truth or an independent physical cue |
| `oil_phase_topology.dark_border_cap_conflict` | Candidate-relative terminal dark-cap geometry/intensity check | Another upper/lower persistence veto risks duplicating existing behavior; no replay or threshold change is warranted |

Discovery covered relevant callers/measurement owners and repository-wide searches
for relative context/profile, remote return, strongest peak, material partition
and region connectivity. No new runtime owner is introduced. Foam membership,
preprocessing and artifact connected-component routines exist; their presence
does not supply Oil region identity. None is repurposed as Oil truth.

## What the representation adds, and what it cannot decide

For shared strip profile p and candidate source row c, a relative view is simply
q(d)=p(c+d), retaining exact support and finite bounds. This is a reindexing of
already supplied observations, not new pixels or independent evidence. Candidates
at different rows may have different relative patterns, but same-X candidates
still share the same scene curve. There is no implication that their class scores
must be equal, or that distance to any particular peak is physically meaningful.

| Possible rule | Assessment on the current evidence |
|---|---|
| Nearest/strongest remote edge identifies Oil | Rejected as an identity justification: the selected edge has no independent Oil identity; contrast/alignment and structural edges already collide. Can describe location relative to an edge only |
| Return means reflection; sustained step means Oil | Rejected as a categorical mapping: Oil plus reflection and bounded artifacts can share appearance; a broad structural step can match Oil. Crop/mask truncation prevents absence claims |
| Aggregate more strips or change scale/weighting | Does not restore horizontal layout or assign physical ownership; dependent samples are not independent votes. Existing locality/profile experiments constrain score-only revisions |
| Use reviewed Y, candidate source or rejected flag to choose the reference | Circular or case-specific. Human idx0/idx20 ambiguity and the idx10 historical judgment conflict remain unresolved |
| Preserve ordered context for diagnostic comparison | Supported: source geometry and coverage remain auditable and some finite-band information loss is demonstrable |

Windows examples concern extra context relative to selected candidates. Accum's
spike is remote from idx15 but overlaps idx10's existing bands. The source probe
also resolves the central band gap, but this is not proof the old local peak
fields lacked that feature. No packet-wide private novelty or classification
gain is inferred from these examples.

## Added executable controls and results

Extended the existing `tests/unit/test_s11_spatial_context_probe.py` rather than
creating another diagnostic implementation. Six parameterized cases use the real
O1 witness extractor, holding supplied masks/material/Canny channels and candidate
inventory fixed; they do not rerun production preprocessing or proposals.

1. Two candidates at rows100/110: a remote return at row175, in either polarity,
   leaves the **whole FrameInterfaceWitness** identical, including all candidates
   and observability. Candidate fixed scores also remain identical. Full-height
   strip profiles distinguish the return. This strengthens the former single-
   candidate information-loss control for this constructed inventory.
2. Two candidates at rows100/170: the same remote change still leaves candidate0
   unchanged but changes candidate1 and the whole O1 witness. The shared full-height
   curve sees it too. Novelty therefore depends on the entire sampled inventory.
3. A single-row central spike at row100, in either polarity, touches no band's
   pixels, yet existing O1 gradient peak fields detect it. Direct band raster
   equality is asserted; gray means allow only 1e-12 absolute floating roundoff
   from prefix-sum subtraction. This tolerance is test arithmetic, not a change
   to stored-data validation or a fitted detector threshold.

Existing controls still cover hidden returns under mask/glare, identical-image
physical aliases, horizontal-permutation collisions, raw-gray/source-coordinate
contracts and unchanged NOT_EVALUATED decisions. These ambiguity fixtures do
not attach invented field labels or quantify a real-world failure rate.

Verification:

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_target_aggregation_contract.py
```

**44 passed in 0.43 s** (25 spatial controls, 19 target/aggregation controls).
No source-adapter regression run is required: production and adapter code are
unchanged. Document links, detector governance and whitespace are checked with
this change. Passing controls justify the stated information boundaries only.

## Next design boundary

The remaining concrete representation loss is horizontal arrangement: two
different rasters can have equal row means. A future local feasibility task may
examine candidate-relative two-dimensional boundary/adjacent-region evidence
using existing gradient, mask and path owners, rather than further scalarizing
the same one-dimensional curve. This is a proposed investigation, not an
implemented, selected or proven classifier and not a Windows handoff.

Before new source collection or scoring, that proposal must demonstrate an
observable distinction on equal-row-mean controls with fixed geometry/support,
preserve ambiguity for identical pixels and for Oil-plus-reflection aliases,
handle masks without invented continuation, and explain the physical hypothesis
and differences from existing paths/material/terminal-cap evidence. Merely
distinguishing two synthetic images is insufficient for physical identity.
Do not claim a stationary/moving shortcut, universal direction/polarity, known-Y
reference or another score fusion as the missing observation. If these boundaries
cannot be met, keep the diagnostic and leave the identity question open.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: candidate-local information loss and horizontal averaging are demonstrated only in constructed measurements; the private physical identity failure cause remains unproven. Reindexing does not supply missing physical authority.
- Logic-map impact: NONE — only diagnostic controls and feasibility evidence change; runtime extraction, identity, selection and publication are unchanged.
- Failure-registry impact: NONE — no new field mechanism or repair is established; geometry/threshold/provenance shortcuts remain excluded.
