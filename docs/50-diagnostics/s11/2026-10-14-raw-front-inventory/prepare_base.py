"""One retained legacy PNG through baseline preprocessing and existing G0 owners."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/"src")]
import cv2
import numpy as np
from tests.diagnostics import s11_overlay_mask_comparison as comparison
from tests.diagnostics import s11_existing_material_reuse as reuse

o2,g0=reuse.o2,reuse.g0
arrays=comparison.rgb.native


def prepare(plan,work):
    for pin in plan["sources"]+list(plan["inputs"].values()):g0.pinned_path(ROOT,pin)
    inputs=plan["inputs"]
    capture=reuse.read_pin(ROOT,inputs["capture"])
    report,=[r for r in capture["reports"] if r["stem"]=="base_sample_1"]
    frame_info,=[r for r in report["frames"] if r["frame_index"]==plan["frame"]]
    prior,=[r for r in report["reviewed"] if r["frame_index"]==plan["frame"]]
    assert frame_info["sha256"]==inputs["image"]["sha256"]
    frame=cv2.imread(str(g0.pinned_path(ROOT,inputs["image"])))
    assert arrays.array_hash(frame)==frame_info["bgr_sha256"]
    recipe=comparison.InspectionRecipe.from_dict(reuse.read_pin(ROOT,inputs["recipe"]))
    glass=recipe.glasses[0]
    bundle=comparison.build_mask_bundle(frame,glass)
    pre=comparison.baseline(reuse.read_pin(ROOT,inputs["comparison_plan"])).preprocess(
        bundle.crop,bundle.effective_mask,glass.detector_settings)
    visible=(bundle.effective_mask>0)&(pre.glare_mask==0)
    ox,oy=bundle.crop_origin
    column=int(glass.geometry.ellipse.center_x-ox)
    rows,graph=g0.edge_bindings(pre.canny>0,visible,column,True)
    for r in rows:r["source_xy"]=[column+ox,r["row"]+oy]
    dest=ROOT/plan["destination"]
    names=["base-raster.npz","base-source-preflight.json","base-g0-manifest.json",
           "base-g0-readout.json","base-reuse-manifest.json","base-native-readout.json"]
    o2.require(all(not (dest/n).exists() for n in names),"refuse overwrite")
    def publish(name,data=None):
        if data is not None:o2.write_new(work/name,data)
        (work/name).rename(dest/name)
        return dict(path=str((dest/name).relative_to(ROOT)),sha256=o2.sha256_file(dest/name))
    np.savez_compressed(work/"base-raster.npz",original_roi=bundle.crop,
        effective_mask=bundle.effective_mask,glare_mask=pre.glare_mask,canny=pre.canny)
    raster=publish("base-raster.npz")
    geometry=dict(origin=[ox,oy],shape=list(pre.gray.shape),scale_xy=[1,1],column=column)
    case=dict(id=plan["case_id"],kind="public_compressor",frame=plan["frame"],**geometry,
              raster=raster["path"],rows=[r["row"] for r in rows])
    preflight=publish("base-source-preflight.json",dict(schema="s11-native-source-capture-v1",
        cases=[case],pins={raster["path"]:raster["sha256"]},source_plan_sha256=o2.fingerprint_json(plan),
        original_image=inputs["image"],source_recording=inputs["recording"],
        original_full_bgr_sha256=frame_info["bgr_sha256"],rgb_roi_sha256=arrays.array_hash(bundle.crop[:,:,::-1]),
        visible_sha256=arrays.array_hash(visible),video_decodes=0,production_changed=False))
    manifest=dict(schema="s11-native-source-g0-binding-v1",inputs=dict(foam_preflight=preflight),
                  source_plan_sha256=o2.fingerprint_json(plan),scope="New one-frame G0 geometry, not the old corpus audit")
    manifest_pin=publish("base-g0-manifest.json",manifest)
    context=dict(id=case["id"],original_case_ref=dict(input="foam_preflight",index=0),
        frame=case["frame"],time_sec=frame_info["decoded_timestamp_sec"],time_kind="RECORDED",
        source_recording=inputs["recording"],geometry=geometry,geometry_sha256=o2.fingerprint_json(geometry),
        rows=rows,graph=graph)
    readout=dict(schema=g0.SCHEMA,manifest_sha256=o2.fingerprint_json(manifest),contexts=[context],
        counts=dict(contexts=1,edges=len(rows),new_physical_labels=0,
                    fixed_column_fragments=len({f["fragment_id"] for r in rows for f in r["incident_fragments"]})),
        weak_constraints=[],scope="One newly reconstructed source; complete fixed-column population, zero roles")
    readout_pin=publish("base-g0-readout.json",readout)
    reuse_manifest=dict(schema="s11-native-review-source-reuse-v1",case_id=case["id"],
        inputs=dict(g0_manifest=manifest_pin,g0_readout=readout_pin))
    reuse_pin=publish("base-reuse-manifest.json",reuse_manifest)
    packet=reuse.native_packet(ROOT,manifest,readout,case["id"])
    result=dict(schema="s11-native-source-review-readout-v1",manifest_sha256=o2.fingerprint_json(reuse_manifest),
        native_review_packets=[packet],source_capture=inputs["capture"],prior_scalar_context=prior,
        physical_role="UNREVIEWED",qualified_paths=0,model_calls=0,training_executed=False,
        selection="First pre-overlay S1-01 frame chosen before new edge results; no neighbor/score search")
    final=publish("base-native-readout.json",result)
    print(json.dumps(dict(readout=final,graph=graph,
        center_rows=[r["source_xy"][1] for r in rows],fragments=len(packet["fragments"]),
        prior_display_window=prior["original_agent_proposal"]["oil_source_y_range"],
        native_context_available=sum(f["context_support"]["status"]=="AVAILABLE_PARTIAL_CONTEXT" for f in packet["fragments"]))))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--work",type=Path,required=True)
    args=parser.parse_args()
    prepare(o2.read_json(args.plan),args.work)
