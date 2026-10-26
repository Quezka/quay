"""What the application needs from the outside world."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from ..domain.catalog import SuiteApp


@dataclass(frozen=True)
class ReleaseAsset:
    name: str
    url: str
    size: int
    sha256: str | None = None


@dataclass(frozen=True)
class Release:
    version: str
    page_url: str
    assets: tuple[ReleaseAsset, ...]


class ReleaseFeed(Protocol):
    """Where releases are published. Network only."""

    def latest(self, repo: str) -> Release | None:
        """The newest published release, or None when there is none (or the repository is private)."""
        ...

    def download(self, asset: ReleaseAsset, progress: Callable[[int, int], None]) -> str:
        """Fetch the file, check its size and checksum, and return its local path."""
        ...


class Platform(Protocol):
    """How this computer installs, finds and starts apps."""

    def installed_version(self, app: SuiteApp) -> str | None: ...

    def pick(self, assets: tuple[ReleaseAsset, ...]) -> ReleaseAsset | None:
        """The installer in a release that fits this computer."""
        ...

    def install(self, app: SuiteApp, path: str) -> None: ...

    def launch(self, app: SuiteApp) -> None: ...
