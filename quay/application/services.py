"""The launcher's use cases: what is installed, what is new, install or update one app."""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable

from ..domain.catalog import CATALOG, SuiteApp, by_key
from ..domain.versions import is_newer
from .errors import QuayError
from .ports import Platform, Release, ReleaseFeed


class State(enum.Enum):
    NOT_INSTALLED = "not_installed"
    UP_TO_DATE = "up_to_date"
    UPDATE = "update"
    UNAVAILABLE = "unavailable"  # nothing to install yet (no release for this computer)


@dataclass(frozen=True)
class AppStatus:
    app: SuiteApp
    installed: str | None
    latest: str | None
    state: State
    page_url: str = ""


class SuiteService:
    def __init__(self, feed: ReleaseFeed, platform: Platform, catalog: tuple[SuiteApp, ...] = CATALOG):
        self._feed = feed
        self._platform = platform
        self._catalog = catalog
        self._releases: dict[str, Release | None] = {}

    def apps(self) -> tuple[SuiteApp, ...]:
        return self._catalog

    def installed(self) -> dict[str, str | None]:
        """What is installed right now (local only, quick)."""
        return {a.key: self._platform.installed_version(a) for a in self._catalog}

    def fetch(self) -> dict[str, Release | None]:
        """Ask the releases feed about every app. Network only: safe to run on a worker thread."""
        found: dict[str, Release | None] = {}
        for app in self._catalog:
            found[app.key] = self._feed.latest(app.repo)
        return found

    def remember(self, releases: dict[str, Release | None]):
        self._releases = dict(releases)

    def statuses(self) -> list[AppStatus]:
        out = []
        for app in self._catalog:
            installed = self._platform.installed_version(app)
            release = self._releases.get(app.key)
            usable = release is not None and self._platform.pick(release.assets) is not None
            latest = release.version if release else None
            if installed is None:
                state = State.NOT_INSTALLED if usable else State.UNAVAILABLE
            elif usable and is_newer(latest, installed):
                state = State.UPDATE
            else:
                state = State.UP_TO_DATE
            out.append(AppStatus(app, installed, latest, state, release.page_url if release else ""))
        return out

    def prepare(self, key: str, progress: Callable[[int, int], None]) -> str:
        """Download the installer for an app. Network only: safe to run on a worker thread."""
        release = self._releases.get(key)
        asset = self._platform.pick(release.assets) if release else None
        if asset is None:
            raise QuayError("There is no installer for this app on this computer yet.")
        return self._feed.download(asset, progress)

    def install(self, key: str, path: str):
        self._platform.install(by_key(key), path)

    def launch(self, key: str):
        self._platform.launch(by_key(key))
