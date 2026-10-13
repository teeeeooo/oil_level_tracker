# Additional public compressor input screen — 2026-10-13

**SOURCE SCREEN COMPLETE / regional-role judgment PENDING.** This is a WP03
input-availability step after the [sample4 B reply](2026-10-13-cr1-competitor-role.md).
It runs no detector, encoder, threshold fitting or physical scorer. The
[Work Plan](../../00-project/work-plan.md) owns current progression.

## Source and frozen scope

Reuse the second entry of the October 12
[source-screen list](2026-10-12-public-compressor-source/screen-preflight.json),
which was then located but not acquired or viewed. The publisher's
[Froid117 video](https://www.youtube.com/watch?v=nKfQ1J97_QE),
“Froid117-L'huile du compresseur qui mousse au voyant d'huile”, is attributed by
its public metadata to e-genieclimatique, uploaded 2012-10-01. The title supplies
context, not physical labels.

Before acquisition/viewing, managed run `source-screen-20261013-001` fixed one
public, unauthenticated video-only MP4, at most 100 MB / 1280×720, four views at
0/25/50/75% of decoded duration, and zero model/detector calls. Sources were the
existing `OpenCvVideoReader` and corpus-access guard; no decoder or runtime owner
was added. The prior source renderer is fixed to its original video, so a bounded
read-only invocation used that same reader directly rather than changing it.

| Property | Recorded result |
|---|---|
| Local original | `sample/public_egenie_nKfQ1J97_QE.mp4`, ignored media, one copy |
| Original bytes / SHA-256 | 21,841,275 / `ea522b841deba1b792720f191f5df4c5d65177bb7fa5e4f2b50ccceb1598c744` |
| Format | Public format 136, original video-only MP4, no re-encode |
| Decode | 1280×720, 25 fps, 2,293 frames, 91.72 s; publisher rounds to 92 s |
| Actual fixed views | f0/0 s, f573/22.92 s, f1147/45.88 s, f1720/68.8 s |
| Existing-source identity check | Different bytes from all eight earlier local MP4s; no new sample3 decode |
| Execution | Four source-frame requests; encoder 0, detector 0; no Recipe or corpus registration |

The [source readout](2026-10-13-public-compressor-input/source-review.json) pins
source bytes, reader/guard, decoded timestamps, raw BGR hashes and PNG hashes,
all prior source-file comparisons, runtime and the question. Different bytes are
not sufficient proof of independent physical episodes or absence of reused footage.
The new source is an exposed screen candidate, not an untouched holdout or an
assigned calibration source. Original 164 CR1 rows and P0/Windows groups are unchanged.

## Observed input limitations and targeted question

These are assistant-observed image facts, not user truth:

- At 0 s the title and pointing hand obscure the glass.
- At 22.92 and 45.88 s the glass is small, the publisher watermark covers its
  lower portion, and the framing differs.
- At 68.8 s the sampled view is of pressure gauges, not the compressor glass.
- The predeclared midpoint has a narrow bright horizontal band in the visible
  glass. Its physical role is not established by the title or appearance alone.

The [native midpoint](2026-10-13-public-compressor-input/native-f1147.png) and
[phone-sized source-coordinate view](2026-10-13-public-compressor-input/review.png)
preserve original pixels. The plotted crop X800–925/Y565–685 uses nearest-neighbor
display; it is not a detector ROI or a label rectangle. No candidate line is drawn.

The new question is whether the visible bright band around Y627–632 is an actual
Oil surface boundary, a Foam layer requiring separate upper/lower roles, or
unassessable from this still. This is a regional role question, not an exact-Y or
per-pixel request. An unassessable answer is retained without forcing a label.
No reply has yet been received. None of the earlier sample4 or public-miso source
judgments is reopened.

A positive reply could support a separately frozen principle or failure-response
input. It would not establish a full calibration set, native localization, a
continuous usable episode, CR1 geometry/bank transfer or Windows effectiveness.
Do not turn watermark/crop regions into true negative labels or selectively erase
them to manufacture a successful test. This bounded four-view screen does not
prove that every other part of the recording is usable or unusable.

## Retention and verification

Keep the original once outside Git for pending qualification, this readout, one
lossless midpoint and its phone plot. The other three PNGs and all temporary
download metadata, package files and rendering cache are discarded at closeout.
The original plus fixed actual timestamps/BGR hashes can reproduce those context
views without a duplicate video or full frame archive. Signed media URLs and
authentication data are not retained.

Retaining the midpoint preserves the exact visible evidence and caption overlap
behind the pending judgment. Reconsider the source/derived image retention when
that judgment and source eligibility are closed or an accepted input replaces it.
The original hash is unchanged after decoding. Source bytes, four frame identities,
midpoint linkage and corpus guard were checked; no inference or efficacy claim follows.
The source was fetched with temporary yt-dlp 2026.8.19 using verified system CA;
an initial unsupported CA option failed before access and was corrected to the
CA environment variables. No project or CR1 environment dependency changed.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: source role, occlusion and geometry are not yet qualified; no detector stage has been executed on this source.
- Logic-map impact: NONE — source acquisition/quality inspection only; existing reader, preprocessing, candidate generation, authority and publication are unchanged.
- Failure-registry impact: NONE — existing provenance and exposed-data guards apply; no new classifier mechanism or field improvement is claimed.
