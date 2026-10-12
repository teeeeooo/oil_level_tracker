# Public compressor source intake — 2026-10-12

The user identifies the bright horizontal layer's upper boundary near **50 s**
in [미소냉동's public video](https://www.youtube.com/watch?v=mHOS1-1ck60&t=50s)
as a Foam upper, and subsequently confirms its lower boundary as an Oil upper.
This is a new regional principle-check input. It does not supply exact pixel
truth, a continuous benchmark or a detector success. The
[Work Plan](../../00-project/work-plan.md) owns further work.

## Source and exposure

The [source-screen preflight](2026-10-12-public-compressor-source/screen-preflight.json)
was written before source viewing, bounded to at most two located public videos.
Only the first was inspected; the second was not acquired or evaluated. Browser
views near 25/50/75 s and a native view near 50 s preceded the separate
[12-view native review plan](2026-10-12-public-compressor-source/native-review-plan.json).
This is exposed development intake, never a reserved or blind holdout. It is
separate from the already closed S3 experiment and does not replace its inputs.

The [curated provenance](2026-10-12-public-compressor-source/provenance.json) records:

| Property | Retained value |
|---|---|
| Public source | `mHOS1-1ck60`, 미소냉동, published 2020-03-10 |
| Title | 압축기 오일포밍(Oil Foaming)현상과 대책_냉동기초 실무 |
| Local original | `sample/public_miso_mHOS1-1ck60.mp4`, ignored by the existing media rule |
| Size / SHA-256 | 13,480,200 bytes / `68ead21680534b7bbc06de9b556f5d3a2c4576dd7eaa85c6d50b90534daecc15` |
| Download | Public unauthenticated format 136; original video-only MP4, no audio or re-encode |
| Decoded metadata | 1280 × 720; 7,496 frames; OpenCV FPS 29.97002997002997; calculated duration 250.116533 s |

The publisher metadata rounds FPS to 30 and duration to 250 s; actual decoder
timestamps are recorded separately. The download used yt-dlp 2026.8.19 installed
only in a temporary directory and the existing macOS CA file for verified TLS.
No project dependency or authentication was added. The original download was
moved once into the ignored media location. No full video or transient signed
download URL is committed.

The full-file identity differs from the four retained original local sources.
The viewed hardware/framing also differs from the inspected sample4 first frame
and sample3's already-retained review image. This limited check is not proof of
whole-source or scene independence. No new sample3 decode or mining was performed,
and its retirement remains unchanged. The new source has no numbered sample alias,
Recipe or automatic corpus registration.

## What the views establish

The [renderer](2026-10-12-public-compressor-source/render.py) reuses the application
`OpenCvVideoReader` and existing diagnostic corpus-access guard. It does not call
a detector, invent a reader, create a Recipe or score physical accuracy. The
[native readout](2026-10-12-public-compressor-source/native-review.json) records all
12 requested/actual times, decoded indices and native BGR hashes.

The [lossless main frame](2026-10-12-public-compressor-source/native-at-50.png)
is frame **1499 at 50.016633333 s**, returned by a 50 s timestamp seek. It is a
near-time native reference, not a claim to capture the browser decoder's exact
frame at reported currentTime 50.023306 s. No exact frame annotation is inferred
from the user's regional browser judgment.

The [context sheet](2026-10-12-public-compressor-source/source-contact-sheet.jpg)
shows the fixed requests at 25, 40, 45, 48, 49, 50, 51, 52, 55, 60, 65 and 70 s.
Tiles are half-size context views, not measurement rasters. Inspection finds:

- At 25 s the hardware appears at a different size/angle and the glass is dark.
  The subtitle describes an Oil context; it is publisher context, not a new
  human-qualified Oil label.
- The bright layer is visible in the 40–55 s sampled views. The camera moves,
  changing the glass center; by the 55 s view it is substantially closer. These
  isolated views do not certify an uninterrupted physical event or stable Recipe.
- At 60/65/70 s the selected frames are explanation slides. The full recording
  must not be treated as a continuous measurement scene.
- Near 50 s both the broad bright layer and fine marks around/in the glass are
  visible. Their individual identity as bubbles, droplets, reflection or glass
  texture remains unqualified. Larger visible geometry alone is not accuracy.

The source therefore adds regional Foam/Oil **principle** context and a same-scene
role contrast: the layer's upper and lower boundaries have different target roles.
It does not yet add a numerically labeled **failure-response** benchmark, a
temporal **workflow** benchmark, a calibrated tolerance, or a replacement for the
existing qualified water/sample4 controls. The frozen seven-source P0 roster
remains an unchanged baseline; this intake is separately routed.

## Closed upper and lower judgments

The [verbatim upper-role reply](2026-10-12-public-compressor-source/upper-role-reply.json)
records **“밝은 층의 윗 경계가 Foam 상단으로 보인다”**. That question is CLOSED.
No exact X/Y, neighbouring-frame truth, timing or detector approval follows.

The [lower-role reply](2026-10-12-public-compressor-source/lower-role-review.json)
records **“아랫경계는 oil 상단 맞음”**. That question is also CLOSED. The bright
layer's lower boundary against the dark region beneath it is a regional Oil
upper, supporting an Oil/Foam role comparison within this scene. Neither answer
labels exact pixels or neighbouring frames; no exact pixel specification has
been requested. Do not repeat either physical-role question.

## Current-frame baseline and resolution preflight

The [four-call preflight](2026-10-12-public-compressor-source/current-frame-preflight.json)
freezes one source-prepared inner-glass ellipse and unchanged detector defaults.
It reuses `OpenCvPhaseDetector.detect` through the existing diagnostic Recorder,
with fresh state for native NONE/FULL and half-resolution NONE/FULL. All candidates,
diagnostic images/state and source-coordinate projections are retained. The
half-size input uses area resampling and explicit pixel-center coordinate mapping;
rounding remains with the existing geometry owners. No alternate Recipe or
parameter search follows a result.

This measures current-frame representation and local resolution sensitivity.
Both NONE/FULL pairs must agree before causal interpretation. It does not execute
a completed session, confirm an episode, evaluate continuity, test a new physical
selector, or reopen S3. Regional role judgments are evaluation context only; no
numeric precision/recall or universal minimum-resolution requirement follows.

## Verification and reproduction

[Artifact verification](2026-10-12-public-compressor-source/artifact-verification.json)
checks the source bytes/hash, seven implementation/input pins, all 12 request-time
joins within one source frame, lossless PNG equality with the decoded BGR array,
and the sheet's saved hash/shape. It is integrity evidence, not independent
physical or continuous-story validation. Production behavior is unchanged.

With the pinned local original present, reproduce into a new directory:

```bash
.venv/bin/python docs/50-diagnostics/s11/2026-10-12-public-compressor-source/render.py --root . --output /tmp/s11-public-source-review
```

The renderer refuses to overwrite an existing output directory. A future download
is not assumed to reproduce the same platform encoding; verify the pinned SHA-256
before decoding. The full downloader metadata remains temporary and untracked.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `OIL-CANDIDATE`
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: NOT_EVALUATED — no detector execution; the intake separates regional physical meaning from exact pixels, temporal scope and changing image geometry before any model comparison.
- Logic-map impact: NONE — reuses the existing video reader for bounded evidence preparation; no production route, geometry policy or selection change.
- Failure-registry impact: NONE — source/role uncertainty and non-transfer of reviewed truth are already covered; no new field failure or repair is asserted.
