"""API tests against a running local server (bootstrap wiring, real adapters)."""

import hashlib
import http.client
import json
import threading
import time

import cv2
import numpy as np
import pytest

from oil_tracker import bootstrap


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "sample.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (320, 240))
    for index in range(20):
        writer.write(np.full((240, 320, 3), 10 * index, np.uint8))
    writer.release()
    return path


@pytest.fixture
def app(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_text("<!doctype html><title>t</title>", encoding="utf-8")
    (web / "app.js").write_text("export {};", encoding="utf-8")
    running = bootstrap.start(data_folder=tmp_path / "data", web_folder=web)
    yield running, tmp_path
    running.close()


def call(running, method, path, body=None, token=True, host=None):
    port = running.server.server_address[1]
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-OLT-Token"] = running.token
    if host:
        headers["Host"] = host
    payload = None if body is None else json.dumps(body).encode()
    connection.request(method, path, payload, headers)
    response = connection.getresponse()
    data = response.read()
    connection.close()
    kind = response.getheader("Content-Type", "")
    return response.status, (json.loads(data) if kind.startswith("application/json") else data), response


def glass_json(**changes):
    glass = {
        "id": "g1",
        "name": "BASE",
        "ellipse": {"center_x": 160, "center_y": 120, "radius_x": 40, "radius_y": 100},
        "zero_line_y": 130,
        "judgment_rule": {
            "mode": "RECOVERY",
            "recovery_limit_sec": 120,
            "stable_hold_sec": 5,
            "minimum_valid_coverage_ratio": 0.7,
            "allowed_sec": 5,
            "allowed_px": 0,
        },
    }
    glass.update(changes)
    return glass


def test_static_files_and_url(app):
    running, _ = app
    assert running.url.startswith("http://127.0.0.1:") and "token=" in running.url
    status, body, response = call(running, "GET", "/", token=False)
    assert status == 200 and body.startswith(b"<!doctype html>")
    assert response.getheader("Content-Type").startswith("text/html")
    assert call(running, "GET", "/web/app.js", token=False)[0] == 200
    assert call(running, "GET", "/web/../../etc/passwd", token=False)[0] == 404


def test_a_burst_of_connections_is_served(app):
    # A page load opens its modules at once; a short listen queue reset some and left the page blank.
    running, _ = app
    start = threading.Barrier(60)
    statuses = []

    def fetch():
        start.wait()
        try:
            statuses.append(call(running, "GET", "/web/app.js", token=False)[0])
        except OSError as failure:
            statuses.append(type(failure).__name__)

    threads = [threading.Thread(target=fetch) for _ in range(60)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert statuses == [200] * 60


def test_api_needs_the_token_and_a_local_host(app):
    running, _ = app
    assert call(running, "GET", "/api/recipes", token=False)[0] == 403
    port = running.server.server_address[1]
    assert call(running, "GET", "/api/recipes", host=f"evil.example:{port}")[0] == 403
    assert call(running, "GET", "/api/recipes", host=f"localhost:{port}")[0] == 200


def test_recipe_round_trip_through_the_api(app, video):
    running, tmp_path = app
    status, listing, _ = call(running, "GET", "/api/recipes")
    assert status == 200
    assert listing == {"folder": str(tmp_path / "data" / "Recipes"), "recipes": [], "unreadable": []}

    status, opened, _ = call(running, "POST", "/api/videos", {"path": str(video)})
    assert status == 200
    assert (opened["width"], opened["height"], opened["frame_count"]) == (320, 240, 20)

    status, jpeg, response = call(running, "GET", f"/api/videos/{opened['id']}/frame?t=0.7")
    assert status == 200 and jpeg[:2] == b"\xff\xd8"
    assert response.getheader("X-Frame-Index") == "7"

    body = {"id": None, "name": "2호기", "glasses": [glass_json()], "reference": {"video_id": opened["id"], "time_sec": 0.7}}
    status, saved, _ = call(running, "POST", "/api/recipes", body)
    assert status == 200, saved
    assert saved["reference_frame"] == {"width": 320, "height": 240, "source_name": "sample.avi", "time_sec": 0.7}
    assert (tmp_path / "data" / "Recipes" / "2호기.recipe.json").is_file()

    status, listing, _ = call(running, "GET", "/api/recipes")
    assert [r["name"] for r in listing["recipes"]] == ["2호기"]
    assert listing["recipes"][0]["glass_names"] == ["BASE"]

    status, detail, _ = call(running, "GET", f"/api/recipes/{saved['id']}")
    assert detail == saved
    status, reference, _ = call(running, "GET", f"/api/recipes/{saved['id']}/reference.jpg")
    assert status == 200 and reference[:2] == b"\xff\xd8"

    assert call(running, "DELETE", f"/api/videos/{opened['id']}")[0] == 200
    assert call(running, "GET", f"/api/videos/{opened['id']}/frame?t=0")[0] == 404


def test_problems_come_back_as_422(app, video):
    running, _ = app
    _, opened, _ = call(running, "POST", "/api/videos", {"path": str(video)})
    body = {"id": None, "name": "", "glasses": [glass_json(zero_line_y=500)], "reference": {"video_id": opened["id"], "time_sec": 0}}
    status, result, _ = call(running, "POST", "/api/recipes", body)
    assert status == 422
    assert sorted((p["field"], p["glass_id"]) for p in result["problems"]) == [("name", None), ("zero_line_y", "g1")]


def test_bad_requests(app, tmp_path):
    running, _ = app
    assert call(running, "POST", "/api/recipes", {"id": None})[0] == 400
    assert call(running, "POST", "/api/recipes", {"id": None, "name": "x", "glasses": [glass_json(zero_line_y="1")]})[0] == 400
    not_video = tmp_path / "x.mp4"
    not_video.write_bytes(b"nope")
    assert call(running, "POST", "/api/videos", {"path": str(not_video)})[0] == 422
    assert call(running, "GET", "/api/recipes/missing")[0] == 404
    assert call(running, "GET", "/api/nothing")[0] == 404


def test_file_dialog_needs_a_window(app):
    running, _ = app
    assert call(running, "POST", "/api/videos/pick", {})[0] == 501


def test_check_and_defaults(app, video):
    running, tmp_path = app
    _, opened, _ = call(running, "POST", "/api/videos", {"path": str(video)})
    body = {"id": None, "name": "x", "glasses": [glass_json(zero_line_y=500)], "reference": {"video_id": opened["id"], "time_sec": 0}}
    status, result, _ = call(running, "POST", "/api/recipes/check", body)
    assert status == 200 and [p["field"] for p in result["problems"]] == ["zero_line_y"]
    assert not (tmp_path / "data" / "Recipes").exists()
    status, defaults, _ = call(running, "GET", "/api/defaults")
    assert defaults["judgment_rule"] == glass_json()["judgment_rule"]


def wait_for_job(running, job_id):
    for _ in range(500):
        job = call(running, "GET", f"/api/jobs/{job_id}")[1]
        if job["state"] != "running":
            return job
        time.sleep(0.02)
    raise AssertionError("the analysis did not end")


def saved_recipe(running, video):
    _, opened, _ = call(running, "POST", "/api/videos", {"path": str(video)})
    body = {"id": None, "name": "2호기", "glasses": [glass_json()], "reference": {"video_id": opened["id"], "time_sec": 0}}
    return opened, call(running, "POST", "/api/recipes", body)[1]


def setup_json(opened, recipe, compressor=0.5):
    glass = glass_json()
    return {
        "inspection_id": None,
        "video_id": opened["id"],
        "recipe_id": recipe["id"],
        "glasses": [{"id": glass["id"], "ellipse": glass["ellipse"], "zero_line_y": glass["zero_line_y"]}],
        "settings": {"start_sec": 0, "end_sec": 1.9, "compressor_start_sec": compressor},
    }


def test_an_inspection_from_its_video_to_the_analysis(app, video):
    running, tmp_path = app
    opened, recipe = saved_recipe(running, video)
    status, listing, _ = call(running, "GET", "/api/inspections")
    assert status == 200
    assert listing == {"folder": str(tmp_path / "data" / "Inspections"), "inspections": [], "unreadable": [], "job": None}

    status, choices, _ = call(running, "GET", f"/api/inspections/recipe-choices?video_id={opened['id']}")
    assert [(r["id"], r["problem"], r["needs_compressor_start"]) for r in choices["recipes"]] == [(recipe["id"], None, True)]

    setup = setup_json(opened, recipe, compressor=None)
    status, checked, _ = call(running, "POST", "/api/inspections/check", setup)
    assert status == 200 and [p["field"] for p in checked["problems"]] == ["compressor_start_sec"]
    status, refused, _ = call(running, "POST", "/api/inspections/start", setup)
    assert status == 422 and [p["field"] for p in refused["problems"]] == ["compressor_start_sec"]
    assert not (tmp_path / "data" / "Inspections").exists()  # nothing is written before the analysis starts

    setup = setup_json(opened, recipe)
    status, started, _ = call(running, "POST", "/api/inspections/start", setup)
    assert status == 200, started
    inspection_id = started["inspection"]["id"]
    assert started["inspection"]["state"] == "NOT_ANALYSED" and started["job"]["inspection_id"] == inspection_id
    assert wait_for_job(running, started["job"]["id"])["state"] == "finished"

    status, detail, _ = call(running, "GET", f"/api/inspections/{inspection_id}")
    assert (detail["state"], detail["failure"]) == ("ANALYSED", None)
    assert detail["video"]["sha256"] == hashlib.sha256(video.read_bytes()).hexdigest()
    assert detail["settings"] == {"start_sec": 0.0, "end_sec": 1.9, "compressor_start_sec": 0.5, "sample_count": 4}
    assert detail["recipe"]["glasses"][0]["ellipse"] == {"center_x": 160, "center_y": 120, "radius_x": 40, "radius_y": 100}

    status, analysis, _ = call(running, "GET", f"/api/inspections/{inspection_id}/analysis")
    assert status == 200 and analysis["times"] == [0.0, 0.5, 1.0, 1.5]
    glass = analysis["glasses"][0]
    assert (glass["glass_id"], glass["y0"], glass["rows"], glass["pieces"]) == ("g1", 20, 200, 1)
    assert len(glass["oil"]["ys"]) == 4 and set(glass["oil"]["origins"]) == {"DRAFT"}

    status, png, response = call(running, "GET", f"/api/inspections/{inspection_id}/images/g1/context-0.png")
    assert status == 200 and png[:8] == b"\x89PNG\r\n\x1a\n" and response.getheader("Content-Type") == "image/png"
    assert call(running, "GET", f"/api/inspections/{inspection_id}/images/g1/background-0.png")[0] == 200
    assert call(running, "GET", f"/api/inspections/{inspection_id}/images/g1/context-1.png")[0] == 404

    entry = call(running, "GET", "/api/inspections")[1]["inspections"][0]
    assert (entry["id"], entry["video_name"], entry["recipe_name"], entry["state"]) == (inspection_id, "sample.avi", "2호기", "ANALYSED")

    status, reopened, _ = call(running, "POST", f"/api/inspections/{inspection_id}/video")
    assert status == 200 and reopened["name"] == "sample.avi"
    setup["inspection_id"] = inspection_id
    assert call(running, "POST", "/api/inspections/start", setup)[0] == 409  # an analysed inspection keeps its setup


def test_inspection_errors(app, video):
    running, _ = app
    opened, recipe = saved_recipe(running, video)
    assert call(running, "GET", "/api/inspections/missing")[0] == 404
    assert call(running, "GET", "/api/inspections/recipe-choices")[0] == 400
    assert call(running, "GET", "/api/inspections/recipe-choices?video_id=nope")[0] == 404
    assert call(running, "POST", "/api/inspections/start", {"video_id": opened["id"]})[0] == 400
    bad = setup_json(opened, recipe)
    bad["glasses"] = []
    assert call(running, "POST", "/api/inspections/check", bad)[0] == 400
    assert call(running, "GET", "/api/jobs/nope")[0] == 404
