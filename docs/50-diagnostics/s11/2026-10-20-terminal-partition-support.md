# TPA-1 — terminal-partition cross-representation support

## Question and mechanism evidence

Base HEAD: `6757191`. Current authority: [Work Plan](../../00-project/work-plan.md).
This is the successor that [AAT-1](2026-10-20-anchor-authority-trace.md#findings)
points to.

Once Foam is present, every sample4 Oil candidate is ordered-lower, and its
`ORDERED_LOWER_INTERFACE` identity needs cross-representation support of at
least 0.12. `_cross_representation_support` drops every peer with
`material_texture_conflict >= 0.60`. Accepted Oil/Foam boundary candidates sit
under textured Foam and score 0.60–0.75, so they cannot support one another:
their support is 0.00. Lower-structure rows keep support and become anchors.
The existing `material_terminal_partition_support` ("terminal") is 1.00 on all 7
accepted controls and 0.00 on the 40/42/44 s opposed targets and the 51–52 s
Y862 structure. It is 1.00 on the 38 s lower opposed rows, whose conflict is
already below 0.60.

[R14](../../20-architecture/s11-r14-phase-component-replacement-architecture.md)
added the ordered-lower exception precisely because Foam texture can make the
physical Oil row's conflict high. The later peer exclusion made it unreachable.

## Hypothesis and intervention

**TPA-1:** when **both** the candidate and the peer are terminal partitions of
the textured layer (`terminal_support >= 0.55`), the peer's high texture conflict
does not exclude it from cross-representation support. Two observations of the
bottom edge of a textured layer can corroborate the same boundary. Rows inside
texture (non-terminal) are excluded exactly as before.

The diagnostic replaces `_cross_representation_support` with a copy that
differs only in that peer-exclusion condition. With the exemption disabled, the
copy must equal the original on every call of a full run. Nothing else changes:
- the artifact-signature and optics-opposition peer exclusions, family rules,
  tolerance and the support formula;
- every identity gate, including `texture_clean` for `DIRECT_INTERFACE` and the
  candidate's own conflict limits in other anchor rules;
- non-nearest ordered-lower demotion, assignment, phase, selection and every
  Foam owner.

The 0.55 terminal level reuses the existing `material_layer_terminal` constant.
There is no new threshold, stored baseline, donor value, or video/time/Y
exception.

## Scope and execution

**Stage 1, sample4.** Same frozen SOI population as CAF-1: baseline plus all 245
single-time withdrawals, saved raw/Recipe, 0–56 s at 2 Hz, all options OFF,
UNKNOWN_REVIEW. Run the ordinary policy and TPA-1 at the current HEAD. Ordinary
rows and events must reproduce the saved SOI records exactly. Verify every
provenance join and event link. Render CSV/graphs for every case whose public
output changes. Unlike CAF-1, the baseline itself is expected to change.

**Stage 2, descriptive.** `base_sample_1` 0–14.4 s and `sample2` 0–2 s,
ordinary versus TPA-1, through the ordinary analysis entry. These windows may
contain no Foam; zero effect would show neither benefit nor safety. Sample3
stays quarantined.

**Contract checks before stage 1.**
- Focused tests: with the exemption off, the copy equals the original. Two
  terminal high-conflict peers now support each other. A non-terminal
  candidate or peer is still excluded. Artifact/optics exclusions are
  unchanged.
- The existing resolver and phase unit tests under the wrapper, with the
  activation count reported.

## Pre-registered evaluation

Judge outcomes with the
[P0 local-residual bounds](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20)
(sample4 C1 band ±5.2 px) and the 13 frozen SOI controls:
- accepted: 38 s Y844, 40 s Y841, 42 s Y839, 42.5 s Y835, 44 s Y844, 52 s Y833,
  plus the 49.5 s practical approximation Y841;
- opposed: 38 s Y880/882/887, 40 s Y865.5, 42 s Y868, 44 s Y822;
- user-confirmed wrong (CAF-1): 51.0–52 s Y861.5–862.

**Baseline under TPA-1** (the primary result), against the ordinary baseline:
1. **Controls:** no reviewed opposed target or the 51–52 s Y862 structure is
   newly selected. An accepted control is not lost unless the replacement is
   within C1 of it.
2. **Replacements:** where the ordinary baseline selects a reviewed opposed
   target, a TPA-1 output within C1 of the accepted value counts as a recovered
   point. A different value is a targeted question if it changes a report
   extremum, direction or phase, and otherwise U.
3. **Report extrema:** a new supported report extremum is a targeted question,
   unless it lies within C1 of a reviewed positive. H3's 54.5 s +45 px maximum
   must not appear.
4. **Gaps:** gaps in reviewed-visible 38–56 s satisfy C3, or are no worse than
   the ordinary baseline.
5. **Foam:** any change to a Foam coordinate or episode is reported as F06
   coupling.

**Population (246 conditions):** activation count; every changed case
classified A/B/C/U against its ordinary counterpart and rendered. The CAF-1
counterexamples (51–52 s Y862) and H3's counterexample (54.5 s +45 px) are
checked in every condition.

**Stop rule.** Any of these closes TPA-1 without promotion:
- a new A-class result at a reviewed control (opposed or Y862 selected,
  reviewed positive replaced outside C1 with an extremum or direction change);
- a failed hard contract (provenance, copy equality, focused tests);
- a Foam episode created or erased.

No widening, terminal-level change or tuning follows the outputs.

**If it passes:** TPA-1 becomes a candidate for a default-OFF option and a
Windows comparison, with the Accum layered-Foam segments as the field target.
That needs the user's Windows run. S11 ACTIVE / O2 OPEN / FIELD FAIL is
unchanged by local results.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F10`.
- First harmful stage: AAT-1 places it at `OIL-AUTHORITY` cross-representation support: the texture-conflict peer exclusion zeroes support for the accepted boundary under Foam. Whether restoring support for terminal boundary pairs repairs context without new errors is the open question.
- Existing feature coverage: saved sample4 P5 NONE raw candidates and stored Recipe/session; UNKNOWN_REVIEW, margin 0.08, zero exclusions/templates, all experimental options OFF; existing material-texture and terminal-partition features from the saved acquisition; existing `material_layer_terminal` level 0.55. Stage 2 uses the stored base_sample_1/sample2 Recipes through the ordinary analysis entry.
- Execution scope: stage 1 runs the completed resolver, samples, events, report presentation and changed-case CSV/graphs on reused acquisition; stage 2 runs full extraction and completed analysis for two short windows. No GUI, private Windows replay, physical accuracy claim or independent report reading.
- Logic-map impact: NONE — diagnostic wrapper only; production source, defaults and runtime ownership are unchanged.
- Failure-registry impact: NONE — evidence is recorded here; any registry pointer follows the results.
