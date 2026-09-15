# R22-1 Windows Interface Measurement

This is a bounded diagnostic collection, not R23 behavioral qualification.
R22 decisions are expected to remain unchanged. The
[R22-1 architecture](../20-architecture/s11-r22-1-interface-diagnostics-architecture.md)
defines the fields. Record the exact transferred source identity and runtime;
do not identify an uncommitted source archive solely by its base Git SHA.

Use the same video, recipe, analysis window, sampling and initial-state
confirmations as the R22 comparison. Enable **FULL debug trace** when the
required frame must be guaranteed to appear. BASIC records the new fields but
retains sparse capture and can omit the desired frame. Trace NONE records no
new measurements. Do not change detection thresholds during collection.

Expected identities:

- detector: `opencv-phase-detector-r22-1-interface-diagnostics-v1`;
- resolver: `r22-oil-ownership-evidence-replacement-v1` (intentional);
- `state.oil_interface_diagnostics.schema_version`:
  `r22-1-interface-raster-diagnostics-v1`.

## First bounded Windows-agent request

```text
R22-1 실행 번들에서 BASE source frame_index=14386 한 프레임만 확인해줘.
코드나 임계값은 수정하지 말고 기존 번들을 읽어줘.

1. 실행 detector 버전, resolver 버전, 새 diagnostic schema를 확인해줘.
   record가 없으면 인접 프레임으로 대체하지 말고 없다고 보고해줘.
2. record.state.oil_interface_diagnostics에서 source=material_path이고
   canonical_y=411.5인 후보를 찾아줘. 없거나 복수이면 그 사실만 보고하고
   다른 후보를 임의로 선택하지 마.
3. candidate_input_index로 최상위 record.candidates의 동명 필드와 연결하고
   source, canonical_y, local_y, source_frame_index, crop_origin을 확인해줘.
   candidate_input_index는 배열 위치나 sequence witness offset이 아니야.
4. 해당 후보의 다섯 sector에 대해 아래 값만 표로 보고해줘:
   source_x_range, near_signed_contrast, far_signed_contrast,
   near_minus_far_abs_contrast, peak_source_y, peak_offset_from_candidate_px,
   네 band의 available/reason, gray_mean, gray_std, material_mean,
   material_available, static_overlap, static_available, valid_fraction.

검출 성공/실패 원인을 새로 추정하거나 다른 구간까지 분석하지 마.
사용자 확인 실제 경계는 이 프레임에서 Y=411.5 부근이지만, 측정값이
그 자체로 경계를 증명한다고 해석하지 마. MISSING/null/false/0을 구분해줘.
원본 이미지·영상·전체 trace와 실제 파일명·경로는 보고서에 넣지 마.
```

This first request only verifies that the transferred raster evidence is usable
at a previously reviewed true boundary. A subsequent separate request can
compare the false predecessor and then the Accum boundary. Do not combine all
three into the initial operator task. Exact physical interpretation follows
direct human review, not an LVLM estimate.

Compare final tracking rows with the R22 bundle separately using matching
source/frame/time and matching recipe/runtime. Exclude only run identity fields
from equality; Oil/Foam coordinates, validity, state and events should not change.
Any difference requires investigation before calling the run behavior-preserving.
