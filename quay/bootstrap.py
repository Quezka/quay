"""Wires the layers together."""
from __future__ import annotations

from .application.services import SuiteService
from .infrastructure.autostart import autostart_for_this_computer
from .infrastructure.demo import DemoFeed, DemoPlatform
from .infrastructure.github import GitHubFeed
from .infrastructure.platforms import platform_for_this_computer


def build_service(demo: bool = False, version: str = "0") -> SuiteService:
    if demo:
        return SuiteService(DemoFeed(), DemoPlatform())
    return SuiteService(GitHubFeed(version), platform_for_this_computer(),
                        autostart=autostart_for_this_computer())
