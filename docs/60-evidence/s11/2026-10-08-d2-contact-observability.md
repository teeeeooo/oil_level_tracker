# D2 non-learned contact-cue preflight — 2026-10-08

Base: `912f3bdc0124ed30aa645146ea2555378a1f42e3`. The user excluded machine
learning as excessive for the purpose and authorized continued staged work, with
a stop for user judgment or Windows work. This records completed source/input
checks and a prepared local review, followed by the attributed human reply below.
It is **not a classifier experiment or a rewrite of the frozen truth snapshot**.

## Distinct question and reuse

The proposed observation is the local relationship between a candidate boundary
and surrounding bubble/texture contours: do those contours end or join at the
boundary, or continue through the candidate reference? This is a qualitative
feasibility question about a potentially conditional, non-learned mechanism.
No edge threshold, junction detector, operating point or decision rule is chosen.

The previous region-exchange model compares plane/step/ribbon residuals; the
patch matcher compares displacement; the connectivity oracle counts connected
regions. None establishes the physical meaning of a local contour contact.
Such a contact, even if visible, is not automatically Oil, the uppermost target,
or a usable scalar: structures, internal interfaces and optical superposition
remain opposing explanations. This is not permission to retune closed models.

Source discovery found existing spatial gradients, Canny preprocessing, material
sector paths and witness geometry. Targeted searches followed by a repository
search found no dedicated contour-contact/termination decision owner. The current
task needs no new one: reuse the stored A2 raster receipt, W3 `load_frozen`, target
mapping and exact native/center geometry for a display-only check. If a later
proposal is justified, it must first supply a bounded measurement/abstention rule
and opposing controls at the existing offline evaluation boundary.

## Completed checks and displayed scope

Before pixel inspection, local preflight
`20c907ea4569d6889acf4f0c4de8107547f90d38efc3b70e2de8c8475f1d08ba`
fixed the question, existing regression inputs and stop rule. All 21 stored
rasters' five PNG channels (105 files), their receipt, packet and snapshot were
hash-checked. The original packet/snapshot also match the prior region-exchange
receipt and pass the existing frozen-reader binding check. No video was decoded.

The assistant viewed the seven existing anchor BGR crops and f1319/f1321. These
are 104×104 crops at source origin `[543,798]`. Visible appearance is machine
inspection, not a new human contact annotation. The unchanged physical snapshot
contains 153 candidates and **zero candidate `path_reviews` records**. Its
existing A/B interpretation identifies bubbly fluid above and less-bubbly liquid
below in the two reviewed scenes; it does not establish exact contour contacts.

All three previously bound same-frame target/wrong-target contrasts were rendered
without ranking or choosing a new convenient negative:

| Frame | Target reference | Wrong-target reference | Display purpose |
|---|---|---|---|
| f1320 / 44 s | idx9 native sectors Y842/844/844/844/844 | idx21 center Y822 | Main question: central X566–625; target vicinity versus a reference within the upper texture |
| f1200 / 40 s | idx4 center Y841 | idx10 native sectors 1–4 Y866/867/865/860 | Existing lower wrong-target contrast, optional context |
| f1260 / 42 s | idx4 center Y839 | idx15 center Y868 | Existing lower wrong-target contrast, optional context |

Each figure pairs original stored pixels with the same pixels plus measurement
references. Enlargement uses nearest-neighbour display, without enhancement.
Native segments remain separate; missing native sector 0 at f1200 is not filled.
The references are not traced contours, scalar truth or predictions. Wrong-target
physical identity remains uncertain; it is not silently relabeled as an artifact.
All source hashes match before and after rendering. The three rendered figures
were visually checked for source axes, reference placement and readable labels.

## User judgment checkpoint

At f1320 central X566–625, is there a physical relation in which the upper
bubble/texture contours terminate or join at the target vicinity, while the
wrong-target reference crosses their interior? Or is that relation shared,
superimposed, or unclear at this resolution? The earlier target identities and
A/B material answers are **not being asked again**. No exact pixel annotation or
judgment for every sector is requested.

This interpretation cannot be filled by copying the candidate label or treating
the assistant's image reading as human truth. A distinguishable relation would
justify defining a conditional measurement and testing its opposition, not
automatic classifier/production acceptance. A shared or unclear relation closes
this bounded cue check without a threshold sweep or automatic next image request.

Preparation status was `AWAITING_USER_CONTACT_INTERPRETATION`; the reply below
closes that checkpoint. There is no new Windows task.
No classifier, detector rerun, learned method, prediction, label edit or field
promotion occurred. O2/D3 remain unmet and `FIELD FAIL` is unchanged. The
[Work Plan](../../00-project/work-plan.md) owns resumption after the reply.

The [compact receipt](2026-10-08-d2-contact-observability.json) binds the display
and question. Preflight, reproducible rendering script, full input pins and PNGs
remain locally under `sample/output/s11-d2-contact-observability-20261008-001/`.
These retained review artifacts must not be removed as disposable scratch.

## Contact interpretation received — 2026-10-08

The user's direct reply to the f1320 comparison was:

> 주황선 부근에서는 위쪽 기포·무늬가 실제로 닿아 끝나고, 분홍선은 허공을 가로지름.
> 내 생각에 분홍선은 glass 특유의 무늬 (원형 무늬가 일정 간격으로 놓여있는것과, 저픽셀 영상 특유의 색상 경계)를 인식하고있는듯. 너도 실제 이미지를 한번 봐봐

**Confirmed qualitative relation:** near the orange target reference the upper
bubble/texture features physically meet and terminate; the pink reference crosses
no actual boundary in the user's interpretation. This supersedes the proposed
wording that pink necessarily crosses the interior of a material texture. The
word "허공" is not imported as a new gas-region, EMPTY-state or species label.
The earlier A/B material interpretation and candidate target bindings remain.
**Tentative cause:** glass-associated repeated circular patterns and low-resolution
color boundaries. The user explicitly framed this explanation as a hypothesis.
Periodicity, optical origin and acquisition/processing contributions are not
separately demonstrated by the reply.

The assistant directly inspected the unchanged f1320 raw crop, its reference
figure and f1319/f1321 raw crops. At orange, the visible upper curved features
end near a common lower boundary; at pink, curved patterns and local color changes
do not form a comparable continuous horizontal boundary. This visual assessment
is consistent with the user's relation, but is not independent human truth or a
measurement proving the tentative optical cause. The three adjacent stills do
not establish glass-fixed persistence or a physical contact event over time.

### Existing source and saved measurements explain the pink proposal

The unchanged packet binds idx9 to `material_path` with native geometry and idx21
to `phase_transition_scan`, Y822, with **candidate-center geometry only**. The pink
line is a displayed sampling height, not a captured continuous contour.
`generate_phase_transition_candidates` and `_phase_transition_profile` in
`src/oil_tracker/adapters/vision/oil_supplemental_path.py` pool upper/lower band
means at three radii, take median absolute sector contrast, and choose a proposal
height. They do not trace a contour-contact relationship.

Existing A1 lineage for idx21 records:

| Radius | Available pooled sectors | Clipped median absolute contrast / 48 | Availability coverage |
|---|---|---:|---:|
| 3 | 0, 1, 2, 3, 4 | 0.38194450 | 1.0 |
| 6 | 1, 2, 3, 4 | 0.65699402 | 0.8 |
| 10 | 1, 2, 3 | 1.0 | 0.6 |

At the strongest radius 10, signed pooled deltas are `+49.151138`, `+48.628571`,
`−35.747620`. The absolute-value operation allows a strong response despite
opposite signs. Stored `narrow_horizontal_coverage≈0.6` means three available
pooled sectors out of five, **not 60% traced boundary or physical support**.
These are normalized-image values; they do not isolate sensor resolution,
compression, glass optics or preprocessing effects. This explains the recorded
proposal construction, not the causal reason for final completed-window selection.
Neither a polarity veto nor a blanket phase-scan rejection follows.

The arithmetic above uses already saved records, without replaying any generator.
Source capture `sample/output/s11-a1-lineage-20261007-001/frames-final/f1320.json`
has SHA-256 `a1b2a9ae3ad6b6764ba5d9b97f4553ba5ec258171ca8dc6327b343fc90b9d933`,
matching the prior region-exchange receipt. All 108 preflight inputs and three
display figures remain hash-identical. The preparation JSON and local receipts
retain their historical pending status/bytes; this reply and the Work Plan own
the resolved checkpoint.

**Disposition: HUMAN_CONTACT_RELATION_RECEIVED.** This supplies one qualitative
positive/opposing relation for bounded non-learned measurement design. It does
not assign pixel/sector/scalar truth, prove generalization, or satisfy D2/O2
algorithm entry. No additional human or Windows request is needed for this reply.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: final-selection first cause remains unestablished here. Saved phase-scan aggregation explains proposal construction; the user supplies a local contact contrast, not a calibrated discriminator.
- Logic-map impact: NONE — existing readers and saved geometry render a review only; no detector owner or execution route changes.
- Failure-registry impact: NONE — the new qualitative contact interpretation and saved aggregation arithmetic reinforce existing geometry/provenance limits; no new field cause or successful mechanism is asserted.
