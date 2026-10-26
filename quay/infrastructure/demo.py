"""Made-up releases and installs for `quay --demo` and the tests: nothing is downloaded or installed."""
from __future__ import annotations

import time

from ..application.ports import Release, ReleaseAsset
from ..domain.catalog import SuiteApp

LATEST = {"quire": "0.36.2", "gantry": "0.6.2", "ligature": "0.10.2", "folio": "0.3.3", "bivouac": "0.7.2",
          "facet": "0.1.10", "quay": "0.1.0"}  # missive has no release yet
INSTALLED = {"quire": "0.36.1", "gantry": "0.6.2", "ligature": "0.10.0", "quay": "0.1.0"}


class DemoFeed:
    def latest(self, repo: str) -> Release | None:
        key = repo.split("/")[-1]
        version = LATEST.get(key)
        if version is None:
            return None
        name = f"{key}_{version}_amd64.deb"
        return Release(version, f"https://github.com/{repo}/releases/tag/v{version}",
                       (ReleaseAsset(name, "demo://" + name, 1000),
                        ReleaseAsset(f"{key.title()}-{version}-windows-x64-setup.exe", "demo://setup", 1000)))

    def download(self, asset, progress) -> str:
        for done in range(0, asset.size + 1, 250):
            progress(done, asset.size)
            time.sleep(0.05)
        return "/nonexistent/" + asset.name


class DemoPlatform:
    def __init__(self):
        self.installed = dict(INSTALLED)

    def installed_version(self, app: SuiteApp):
        return self.installed.get(app.key)

    def pick(self, assets):
        return assets[0] if assets else None

    def install(self, app: SuiteApp, path: str):
        self.installed[app.key] = LATEST[app.key]

    def launch(self, app: SuiteApp):
        pass
