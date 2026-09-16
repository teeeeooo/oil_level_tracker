# R22-2 Windows Native Path Measurement

This is sequential diagnostic collection, not behavioral qualification. The
[architecture](../20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md)
keeps R22 decisions unchanged. Transfer the committed R22-2 source and record
its exact commit and any local modifications. An archive with modifications
needs a file-hash manifest; the base commit alone is insufficient identity.

Run the same video, recipe, window, sampling and initial-state confirmations as
R22-1. In the existing analysis-record options, enable **FULL debug trace**.
BASIC retains sparse capture; NONE does not collect these measurements. Do not
change thresholds. Verify runtime from the executed bundle/trace, not merely
the code currently open in the Windows folder.

Expected identities:

- detector: `opencv-phase-detector-r22-2-interface-path-diagnostics-v1`;
- resolver: `r22-oil-ownership-evidence-replacement-v1`;
- diagnostic schema: `r22-2-interface-path-diagnostics-v1`.

## First Windows-agent prompt

```text
R22-2 실행 번들에서 Accum source frame_index=16280,
source=material_path, canonical_y=217 후보 한 건만 확인해줘.
코드·설정·임계값 수정 없이 기존 번들만 읽어줘.

1. 번들의 실행 식별정보와 detector/resolver/diagnostic schema를 보고해줘.
   현재 폴더의 소스 버전만으로 기존 번들의 실행 버전을 단정하지 마.
   대상 record가 없으면 인접 프레임으로 대체하지 말고 없다고 보고해줘.
2. state.oil_interface_diagnostics.candidates에서 source/Y로 찾고,
   candidate_input_index 동명 필드로 최상위 record.candidates에 연결해줘.
   kind=oil_air, source, canonical_y, local_y가 일치하는지 확인해줘.
   거절/권한/선택 상태로 제외하지 마. 없거나 복수이면 임의 선택하지 마.
   과거 index=10을 재사용하거나 배열 위치·witness offset으로 연결하지 마.
3. diagnostic-level source_frame_index, crop_origin, crop_size, coordinate_space,
   band_width_px, edge_exclusion_px와 후보의 path_aligned 상태/사유를 보고해줘.
   unavailable이면 경로를 새로 만들거나 다른 후보 경로로 대체하지 마.
4. path_aligned의 geometry_source, sector_grid, generator_gray_channel,
   measurement_gray_channel, shared_derivation, generator_strength_formula,
   edge_exclusion_reference, classification, independent_support를 보고해줘.
5. 실제 존재하는 각 native sector에 대해 다음만 표로 정리해줘.
   - sector, source_x_range, path_local_y, path_source_y
   - generator_strength, generator_signed_contrast,
     generator_contrast_channel, generator_contrast_scale_px
   - 경로 기준 near/far signed contrast, near_minus_far_abs_contrast,
     peak_source_y, peak_offset_from_path_px, peak_signed_gradient
   - candidate_center_on_same_sector의 같은 측정값
     (이 안에서는 peak_offset_from_candidate_px)
   - 양쪽 측정의 네 band: local_y_range, available, reason,
     gray_mean, gray_std, material_mean, material_available,
     static_overlap, static_available, valid_fraction, valid_pixel_count

기존 candidates[].sectors와 native sectors는 X 구간이 다를 수 있어.
sector 번호만으로 같은 픽셀 영역이라고 가정하지 마.
누락 sector를 채우거나 peak에 맞춰 경로/중심을 이동하지 마.
MISSING은 키 없음, null은 명시된 null로 구분하고 false/0과 합치지 마.

사용자가 확인한 실제 Oil 경계는 이 프레임에서 source Y=213 부근이야.
Y=217 및 native path 각 점의 물리적 정답 여부는 이번에 판정하지 마.
폐기된 LVLM 판독 Y=137/123은 사용하지 마.
다른 후보·프레임 분석, 독립 지지 판정, 임계값 제안은 하지 마.
원본 이미지·영상·전체 trace·실제 파일명/경로/업무 식별정보는 보고서에서 제외해줘.
```

This request establishes whether native samples are available and whether their
bands actually exclude the selected generator row. It does not certify that
the row is the physical boundary. Compare BASE true/false native paths in later
separate requests, after reviewing this one result. Do not bundle those tasks
into the first request.

Separately compare complete R22-1/R22-2 tracking and events by source/Glass/frame/time
under the same recipe/runtime. Exclude only run identity. Investigate any changed
coordinate, validity, confidence, state, flag or event before claiming behavior
preservation. A successful diagnostic run does not change FIELD FAIL; formal
field acceptance still uses the [current qualification procedure](s11-current-windows-field-qualification.md)
and [reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).
