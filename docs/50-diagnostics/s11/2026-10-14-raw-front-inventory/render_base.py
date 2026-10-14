"""Render the sole prior-window native row and inspect it with the existing qualifier."""
import argparse
from pathlib import Path
import sys
import json

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/"src")]
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from tests.diagnostics import s11_native_role_qualification as native
from tests.diagnostics import s11_existing_material_reuse as reuse

o2,g0=native.o2,native.g0
FOLDER=Path(__file__).resolve().parent


def render(work):
    def pin(path):return dict(path=str(path.relative_to(ROOT)),sha256=o2.sha256_file(path))
    def publish(name,value=None):
        assert not (FOLDER/name).exists(),"refuse overwrite"
        if value is not None:o2.write_new(work/name,value)
        (work/name).rename(FOLDER/name)
        return pin(FOLDER/name)
    plan=o2.read_json(FOLDER/"base-plan.json")
    baseline=o2.read_json(FOLDER/"base-g0-readout.json")
    manifest=o2.read_json(FOLDER/"base-g0-manifest.json")
    saved=o2.read_json(FOLDER/"base-native-readout.json")
    packet=reuse.native_packet(ROOT,manifest,baseline,plan["case_id"])
    assert packet==saved["native_review_packets"][0]
    low,high=saved["prior_scalar_context"]["original_agent_proposal"]["oil_source_y_range"]
    rows=[r for r in baseline["contexts"][0]["rows"] if low<=r["source_xy"][1]<=high]
    assert len(rows)==1,"review scope changes if prior broad window has zero or multiple rows"
    row=rows[0]
    chosen=[f for f in packet["fragments"] if row["source_xy"][1] in f["fixed_column_source_ys"]]
    assert len(chosen)==1 and chosen[0]["fragment_id"]==150
    subject=chosen[0]
    original=Image.open(g0.pinned_path(ROOT,plan["inputs"]["image"])).convert("RGB")
    ox,oy=packet["geometry"]["origin"];h,w=packet["geometry"]["shape"]
    rgb=np.array(original)[oy:oy+h,ox:ox+w]
    with np.load(FOLDER/"base-raster.npz",allow_pickle=False) as capture:
        assert np.array_equal(rgb,capture["original_roi"][:,:,::-1])
        for x,y in subject["source_path_xy"]:
            assert capture["canny"][y-oy,x-ox]>0 and capture["effective_mask"][y-oy,x-ox]>0
            assert capture["glare_mask"][y-oy,x-ox]==0
    marked=rgb.copy()
    for x,y in subject["source_path_xy"]:marked[y-oy,x-ox]=[255,0,255]
    plain2=np.repeat(np.repeat(rgb,2,axis=0),2,axis=1)
    marked2=np.repeat(np.repeat(marked,2,axis=0),2,axis=1)
    sheet=Image.new("RGB",(1240,990),"white");draw=ImageDraw.Draw(sheet)
    fontpath="/System/Library/Fonts/AppleSDGothicNeo.ttc"
    font=ImageFont.truetype(fontpath,23);title=ImageFont.truetype(fontpath,29)
    draw.text((20,12),"기존 로컬 영상 base_sample_1 | f144 / 4.8048초",font=title,fill="black")
    draw.text((20,53),"원본 (2배 확대)",font=font,fill="black")
    draw.text((640,53),"보라색: 실제 경로 150",font=font,fill="black")
    sheet.paste(Image.fromarray(plain2),(20,90));sheet.paste(Image.fromarray(marked2),(640,90))
    overview=original.resize((384,216),Image.Resampling.NEAREST)
    pen=ImageDraw.Draw(overview);pen.rectangle((ox*.3,oy*.3,(ox+w)*.3,(oy+h)*.3),outline="cyan",width=2)
    sheet.paste(overview,(20,730))
    draw.text((20,690),"전체 영상에서의 위치",font=font,fill="black")
    for yy,text in [(740,"보라색 선은 어떤 경계인가요?"),
                    (790,"액체–빈공간 / 거품–액체 / 거품–빈공간"),
                    (830,"구조물 / 다른 경계 / 판독 불가"),
                    (895,"Windows 영상의 BASE 영역과는 다른 로컬 자료입니다.")]:
        draw.text((440,yy),text,font=font,fill="black")
    draw.text((20,955),"과거 승인값 Y386은 근사값입니다. 이 그림은 중심열 Y393을 지나는 실제 픽셀 경로를 보여줍니다.",font=font,fill="black")
    sheet.save(work/"base-review.png")
    display=publish("base-review.png")
    pixels=np.array(sheet)
    assert np.array_equal(pixels[90:90+2*h,20:20+2*w],plain2)
    assert np.array_equal(pixels[90:90+2*h,640:640+2*w],marked2)
    review_plan=dict(schema=native.PREPARATION_SCHEMA,reuse_manifest=pin(FOLDER/"base-reuse-manifest.json"),
        reuse_readout=pin(FOLDER/"base-native-readout.json"),case_id=plan["case_id"],
        fixed_column_source_y=row["source_xy"][1],display=display,
        view=dict(id="base-f144-native",source=plan["inputs"]["image"],image_origin_xy=[0,0],
                  display_xyxy=[ox,oy,ox+w,oy+h]),
        question="보라색 150 경로는 액체–빈공간, 거품–액체, 거품–빈공간, 구조물 중 어느 경계인가요? 다른 경계이거나 판독이 어려우면 그대로 알려주세요.",
        selection_reason="Only existing Canny center row inside prior uncertain 378–394 display window; all incident paths retained. No scalar-to-path truth or length ranking.",
        exposure="Existing local legacy recording, new path correspondence; no untouched holdout",no_training=True)
    publish("base-review-plan.json",review_plan)
    proposal=native.prepare_proposal(ROOT,review_plan)
    proposal_pin=publish("base-review-proposal.json",proposal)
    inspection=native.qualify(ROOT,dict(schema=native.INSPECTION_SCHEMA,proposal=proposal_pin,display=display))
    publish("base-review-inspection.json",inspection)
    publish("base-review-verification.json",dict(schema="s11-native-source-review-verification-v1",status="PASS",
        source_image=plan["inputs"]["image"],raster=pin(FOLDER/"base-raster.npz"),display=display,
        complete_packet_equal=True,original_rgb_roi_equal=True,plain_pixels_equal=True,marked_pixels_equal=True,
        every_drawn_pixel_is_visible_saved_canny=True,path_sha256=o2.fingerprint_json(subject["source_path_xy"]),
        subject_sha256=o2.fingerprint_json(proposal["subjects"][0]),vertices=len(subject["source_path_xy"]),
        qualified_units=inspection["qualified_units"],display_scope="Whole original ROI and full-frame locator; no interpolated contour"))
    print(json.dumps(dict(status=inspection["status"],qualified=inspection["qualified_units"],
        subject=proposal["subjects"][0],display=display)))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--work",type=Path,required=True)
    render(parser.parse_args().work)
