# S6 Domain-Owner Review and Field-Priority Addendum

**Milestone:** `S6 — Real-video and Windows validation gate` remains `ACTIVE`
**Related frozen evidence:** [S6-C provisional comparison](s6-provisional-truth-comparison.md)
**Purpose:** Preserve post-freeze domain-owner interpretation and field-priority input without rewriting the blind provisional evidence
**Accuracy status:** Official user-confirmed product `.oiltruth` and category-balanced detector-accuracy acceptance remain pending

This addendum records the test/domain owner's direct review after the S6-C blind annotation freeze. It does not modify the four `*.provisional-truth.json` artifacts or reinterpret them as having been user-confirmed at freeze time.

## Evidence authority and immutability

- The existing provisional annotations remain immutable historical blind evidence created before detector output inspection.
- The post-freeze user review is a separate domain-owner interpretation with higher physical-domain authority than the provisional interpretation.
- This review is not yet bundle-bound product `.oiltruth`; no product truth file is created or modified by this addendum.
- It does not directly establish official MAE, precision, recall, false-positive/negative rate or detector physical-accuracy PASS.
- Future product `.oiltruth` work should use this review as correction input while preserving the original provisional files and their provenance.
- The annotated screenshot supplied in conversation was supporting review context only and is not added as a repository artifact.

Frozen provisional identities remain:

| Artifact | Frozen SHA-256 |
|---|---|
| `sample/base_sample_1.provisional-truth.json` | `1bade0423365be7dcda710364607433c36a8fb809c925784c52e9ddf6a940dce` |
| `sample/sample2.provisional-truth.json` | `193a6c97b318b7d2f24ba8558be2429193a30b8dcab3be533e919eea87961a61` |
| `sample/sample3.provisional-truth.json` | `adb2f0cff086ec521ca11df9a1a0c4b68373436f974a1c631b01fccc6781e781` |
| `sample/sample4.provisional-truth.json` | `4d64c35b6b80b63fd928a8d9ada9a06dd5cb4dcc8e371f63e510596517213c26` |

## sample3 domain-owner review

### Approximately `0:30`

Foam rises first. Oil then enters and the actual oil level rises with it. The lower region of the Glass contains Oil and the upper region contains Foam. This is a compound Oil-plus-Foam state, not a single oil-air interface.

### Approximately `0:34–0:35`

Oil and Foam are mixed in the same view. The lower boundary is the Oil–Foam interface and represents the actual Oil level. The upper boundary is the Foam–Gas interface and represents the Foam upper front. Oil level and Foam upper front therefore coexist as separate physical boundaries in one frame.

### Approximately `1:30`, `1:35` and `1:40`

A real oil level is visible. Oil continues to enter, the level oscillates, and its approximate mean position is near the middle of the Glass. The camera repeatedly fails to maintain focus, so the image quality is very poor.

### Approximately `1:45`

Oil inflow stops, the actual oil level begins to fall, and the drain transition starts.

### Diagnostic interpretation

- The late sample3 oil-null result remains a conservative-coverage suspicion for a low-quality, dynamically moving real level.
- Severe focus loss and camera quality are not representative of the intended field capture, where the Glass is recorded more cleanly and stably.
- This low-quality segment must not become the primary threshold-tuning target or a core acceptance failure.
- Artifact rejection must not be weakened merely to make sample3 pass.
- sample3 remains useful as an Oil/Foam compound-state reference and a lower-priority robustness challenge.

## sample4 domain-owner review

Across the sequence, the real boundary gradually moves upward and strong Oil inflow produces substantial level oscillation.

| Time | Domain-owner interpretation |
|---|---|
| `0:00` | A real Oil level is present with a thin Foam layer above it. |
| `0:15` | A real Oil level remains present with thin Foam above. |
| `0:30` | A real Oil level remains present with thin Foam above. |
| `0:34` | A real Oil level remains present with thin Foam above. |
| `0:40` | A real Oil level remains present with thin Foam above. |
| `0:49` | The Foam region broadens and Oil/Foam mixing increases. |
| `0:56` | Foam occupies most of the upper region; the actual Oil level remains near the lower one-fifth of the Glass height. |

### Diagnostic interpretation

- The provisional early `foam_hint=absent` interpretation does not agree with the later domain-owner review.
- Detector Foam publication must not be classified as a simple false positive merely because it conflicts with that provisional hint.
- The central diagnosis is failure suspicion in preserving and tracking the actual Oil level beneath existing Foam as a separate channel.
- Recommended description: `Foam-dominant scene에서 Oil-under-Foam boundary separation failure suspicion`.
- sample4's detector `FAIL` does not prove a physical recovery failure.
- sample4 is the primary diagnostic case for Oil-under-Foam dual-boundary separation, but official accuracy conclusions still require product `.oiltruth`.

## Field detector validation and repair priorities

The intended field setup records the Glass relatively cleanly and stably. Future S6-D evidence design and any separately authorized detector repair should use this priority order:

1. **Separate dual boundaries when Oil and Foam coexist.** Treat the Oil–Foam interface as the actual Oil level and the Foam–Gas interface as the Foam upper front. Foam presence must not automatically force Oil level to `null`.
2. **Suppress light reflection and glare.** Cover fluorescent reflection, local glare and moving or static bright bands without promoting reflection to a real level.
3. **Suppress Glass rim and structural horizontal lines.** Cover the circular rim, fixed structure and paired lines while preserving a real level near those structures as a competing physical explanation.
4. **Suppress fixed surface defects and residue.** Cover scratches, oil stains, fogging and temporally fixed surface artifacts.
5. **Track an oscillating real level temporally.** Preserve actual direction and mean position rather than selecting only the instantaneous strongest edge; retain bounded tracking through fill, drain and oscillation.
6. **Keep severe low quality, focus loss and camera motion as a separate robustness category.** Give it lower priority than field-representative accuracy and do not aggressively weaken artifact rejection to fit it.

This ordering is authoritative domain-owner input for future category-balanced evidence planning. It does not change the global metric or acceptance architecture in the [real-world validation plan](../../30-validation/real-world-validation-plan.md).

## Sample roles

- **sample1:** strong explanatory horizontal-overlay rejection.
- **sample2:** fluorescent reflection and bubbly-texture rejection.
- **sample3:** Oil/Foam compound-state reference and low-quality robustness challenge.
- **sample4:** primary Oil-under-Foam dual-boundary separation diagnostic case.

## Required follow-on

S6-D remains pending: create bundle-bound, user-confirmed product `.oiltruth` and category-balanced official accuracy evidence before calculating formal metrics or declaring detector accuracy PASS. This addendum should be used as correction and category-design input, not as a substitute for that product workflow.

The currently executable operational gate is `S6-E Bounded Runtime Soak and Resource-Leak Screening`. S6-E is diagnostic-only and does not replace S6-D or the later controlled-idle representative-duration performance and official long-duration CPU/memory acceptance. Because the current Mac has other workload, precise CPU-throughput acceptance is intentionally deferred.