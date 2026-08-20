# S11-R13 Windows Identity and Component Diagnostic

## Root cause

R13 recovered coverage by converting local phase appearance into identity too
early. `DIRECT_INTERFACE` required no independent representation, while
`ORDERED_LOWER_INTERFACE` allowed non-scan sources to bypass the texture-clean
gate. The resulting anchors entered one adjacency graph whose edges checked
only frame adjacency and Y distance. Global path and continuation bounding then
treated contiguous Oil nodes as one run even when their physical component had
changed.

This is a responsibility failure, not a single threshold error:

1. templates both rejected candidates and enabled proposal generators;
2. local appearance and broad-mask ordering granted identity;
3. recurring-track opposition could demote a cleaner reviewed row;
4. trajectory had no component identifier; and
5. run bounds operated on `kind == oil`, not component ownership.

## Counterfactual interpretation

`material_texture_conflict >= 0.60 -> CANDIDATE_ONLY` is a necessary safety
gate for independent ordered-lower authority, but the full-pipeline result shows
it is insufficient. The tested direct-corroboration change reduced some wrong
Base rows but did not test the separate policy that a low-conflict direct row
should receive only a soft recurring penalty. The distance-based component
prototype is rejected: it reduced coverage by turning most paths UNKNOWN and
did not establish stable component identity.

## Replacement boundary

R14 replaces these paths rather than wrapping them:

- template-count-controlled proposal creation;
- generic local `DIRECT_INTERFACE` anchor authority;
- broad-mask-only ordered-lower identity;
- recurrence-only hard demotion of clean direct candidates; and
- component-free trajectory/run binding.

Stored Recipes and candidate feature dictionaries remain readable. No
Base/Accum coordinate or timestamp may enter production policy.
