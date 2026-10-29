"""The only wiring point: builds the adapters and hands them to the use cases."""

from __future__ import annotations

import secrets
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from oil_tracker.adapters.desktop import SystemDesktop
from oil_tracker.adapters.http.api import ApiContext, make_handler
from oil_tracker.adapters.http.jobs import Jobs
from oil_tracker.adapters.http.server import LocalServer, start_server
from oil_tracker.adapters.storage import locations
from oil_tracker.adapters.storage.files import sha256_of
from oil_tracker.adapters.storage.inspection_files import InspectionFolders
from oil_tracker.adapters.storage.recipe_files import RecipeFolder
from oil_tracker.adapters.video.analysis import OpenCvAnalyser
from oil_tracker.adapters.video.frames import open_video
from oil_tracker.application.inspections import Inspections
from oil_tracker.application.recipes import Recipes
from oil_tracker.application.videos import VideoSessions

WEB_FOLDER = Path(__file__).resolve().parent / "web"
CLOSE_WAIT_SEC = 5.0  # for a running analysis to stop as the app closes


@dataclass
class Running:
    server: LocalServer
    videos: VideoSessions
    jobs: Jobs
    token: str

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/?token={self.token}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.jobs.stop_all(CLOSE_WAIT_SEC)
        self.videos.close_all()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id() -> str:
    return str(uuid.uuid4())


def start(
    *,
    data_folder: Path | None = None,
    port: int = 0,
    pick_video: Callable[[], Path | None] | None = None,
    web_folder: Path = WEB_FOLDER,
) -> Running:
    data_folder = data_folder or locations.default_data_folder()
    videos = VideoSessions(open_video, new_id)
    desktop = SystemDesktop(pick_video)
    recipe_store = RecipeFolder(data_folder / locations.RECIPES)
    recipes = Recipes(recipe_store, videos, desktop, utc_now, new_id)
    inspections = Inspections(
        InspectionFolders(data_folder / locations.INSPECTIONS),
        recipe_store,
        videos,
        OpenCvAnalyser(),
        sha256_of,
        desktop,
        utc_now,
        new_id,
    )
    jobs = Jobs(new_id)
    token = secrets.token_urlsafe(24)
    server = start_server(make_handler(ApiContext(recipes, inspections, videos, jobs, web_folder, token)), port)
    return Running(server, videos, jobs, token)
