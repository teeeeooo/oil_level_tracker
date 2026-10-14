# Retained Commitments

This file owns **affirmatively retained work that is not the current executable engineering gate**. It is neither a second roadmap nor a current work plan. Current milestone order and the exact active gate remain owned by [`roadmap.md`](roadmap.md) and [`work-plan.md`](work-plan.md).

## Autosave / abnormal-exit recovery

- **Responsibility:** recover unsaved user work after abnormal process termination without weakening the accepted explicit-save and close-guard semantics.
- **Classification:** `DEFERRED`
- **Authoritative source / rationale:** S9 established explicit Profile dirty/save/close ownership; autosave and crash recovery were deliberately excluded from that release gate.
- **Activation condition:** product priority is explicitly raised after the current detector gate, with a bounded persistence/recovery contract and failure semantics.
- **Routing owner:** future product/workflow slice selected by the project roadmap.
- **Current-gate boundary:** this work remains deferred and is **not the current gate**.

## Windows analysis throughput after detector improvement

- **Responsibility:** reduce analysis and result-generation time for practical
  Windows use while preserving detector outputs and validation requirements.
- **Classification / priority:** `DEFERRED`; the user explicitly prioritizes
  detector effectiveness and retains performance work for afterward
  (2026-10-14).
- **User-reported workload:** a 1 h 8 min 24 s MP4, 1920 × 1080 at 23.976 fps;
  analysis from 480–780 s at 2 samples/s with two analysis regions. Reported
  video-analysis time is about 20 minutes, followed by about 5 minutes of
  postprocessing.
- **User-reported host:** AMD Ryzen Threadripper PRO 7945EX, 12 cores (model
  designation as supplied); NVIDIA RTX 4000 Ada Generation; 128 GB RAM;
  Windows 11 Enterprise 25H2; source code and video on SSD.
- **Correction / evidence limit:** the user confirms that analysis was also
  slow with FULL disabled / NONE selected. FULL-versus-NONE is therefore not
  the explanation for the underlying usability problem or its accepted fix.
  A separate NONE timing, producing source version, ROI geometry and per-stage
  measurements have not been supplied here; the approximate 20 + 5 minutes
  must not be presented as a measured timing for both modes. Root cause is
  unconfirmed; this is a user report, not a reproduced benchmark.
- **Activation / next work:** after the current detector-effectiveness work,
  reuse the existing profiling approach to separate video seek/decode,
  per-region detection, diagnostic work, completed-window resolution and
  bundle/report generation on the isolated Windows ZIP installation. Preserve
  source/runtime/input identity and compare outputs when optimizing measured
  bottlenecks. Do not assume trace settings, GPU availability or hardware
  replacement solve the issue.
- **Current-gate boundary:** no performance rerun or optimization is requested
  now. The active detector and Windows diagnostic comparison remain owned by
  [Work Plan](work-plan.md); this deferred item does not change their order.

## Explicitly superseded recurring dependency

Repeated replay of the private Windows field video during every S11 source iteration is **SUPERSEDED as a normal development dependency**. The private video may remain diagnostic corroboration when deliberately available, but iterative S11 source work must not depend on repeated private-field replay. This superseded practice is not a retained commitment.

## Unresolved S11 field behavior surfaces

- **Responsibility:** preserve field-only uncertainty that the current generic
  local detector controls cannot prove without a deliberate Windows replay.
- **Classification:** `RETAINED / EVIDENCE-GATED`
- **Retained surfaces:** canonical Windows verification of Base release and
  rapid-refill/full closure; Accum initial entry; Accum fill
  continuity/layered/post-Foam ownership; and strict Accum drain
  continuation/re-entry.
- **Current local disposition:** R21 supplies bounded generic Base controls for
  R20-scale slow drain and rapid-refill phase closure, plus behavior-neutral
  decision witnesses. Those controls retire the former *unimplemented Base*
  commitment but do not establish that the private Windows failure had the same
  cause or is repaired. Accum field gaps remain evidence-gated rather than
  guessed from synthetic rows.
- **Activation condition:** deliberate Windows qualification or a separately
  approved behavior design backed by reviewed physical candidate identity,
  source coordinates/phase evidence, bounded transitions and two-sided local
  controls. No global threshold, private timestamp/coordinate, interpolation,
  identity conflation or telemetry-only substitution qualifies.
- **Current-gate boundary:** R21 decision-witness implementation is no longer a
  retained/design-only package; it is part of the current local candidate.
  Field `FAIL` remains authoritative until the canonical Windows procedure is
  deliberately rerun and passes.
