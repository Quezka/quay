"""Releases from GitHub, with a checksum check on every download.

The API allows 60 anonymous requests an hour; a check of the whole suite takes one per app.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from ..application.errors import QuayError
from ..application.ports import Release, ReleaseAsset

API = "https://api.github.com/repos/{repo}/releases/latest"
CHUNK = 256 * 1024


class GitHubFeed:
    def __init__(self, version: str, opener: Callable = urllib.request.urlopen,
                 folder: Path | None = None, timeout: float = 30):
        self._agent = f"Quay/{version}"
        self._open = opener
        self._folder = folder
        self._timeout = timeout

    def latest(self, repo: str) -> Release | None:
        request = urllib.request.Request(API.format(repo=repo), headers={
            "Accept": "application/vnd.github+json", "User-Agent": self._agent})
        try:
            with self._open(request, timeout=self._timeout) as response:
                data = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:  # no release yet, or the repository isn't public
                return None
            if e.code in (403, 429):
                raise QuayError("GitHub is limiting checks right now: try again in an hour.") from e
            raise QuayError(f"GitHub answered with an error ({e.code}).") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise QuayError("Can't reach GitHub. Check your internet connection.") from e
        except ValueError as e:
            raise QuayError("GitHub sent an answer Quay doesn't understand.") from e
        if data.get("draft") or data.get("prerelease"):
            return None
        assets = []
        for a in data.get("assets", []):
            digest = a.get("digest") or ""
            assets.append(ReleaseAsset(a["name"], a["browser_download_url"], int(a["size"]),
                                       digest.split(":", 1)[1] if digest.startswith("sha256:") else None))
        return Release(data["tag_name"].lstrip("v"), data.get("html_url", ""), tuple(assets))

    def download(self, asset: ReleaseAsset, progress: Callable[[int, int], None]) -> str:
        folder = self._folder or Path(tempfile.gettempdir()) / "quay-downloads"
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / Path(asset.name).name
        partial = target.with_name(target.name + ".part")
        request = urllib.request.Request(asset.url, headers={"User-Agent": self._agent})
        digest, done = hashlib.sha256(), 0
        try:
            with self._open(request, timeout=self._timeout) as response, open(partial, "wb") as out:
                while chunk := response.read(CHUNK):
                    out.write(chunk)
                    digest.update(chunk)
                    done += len(chunk)
                    progress(done, asset.size)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            partial.unlink(missing_ok=True)
            raise QuayError("The download didn't finish. Check your internet connection and try again.") from e
        if done != asset.size or (asset.sha256 and digest.hexdigest() != asset.sha256.lower()):
            partial.unlink(missing_ok=True)
            raise QuayError("The download was damaged (its checksum doesn't match), so it wasn't installed. "
                            "Try again.")
        partial.replace(target)
        return str(target)
