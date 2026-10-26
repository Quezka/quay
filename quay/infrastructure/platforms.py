"""Installing and starting apps on Linux (.deb through pkexec apt) and Windows (the Inno setup)."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from ..application.errors import QuayError
from ..application.ports import ReleaseAsset
from ..domain.catalog import SuiteApp


def deb_architecture() -> str:
    machine = platform.machine().lower()
    return {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine, machine)


class DebPlatform:
    def __init__(self, runner: Callable = subprocess.run, launcher: Callable = subprocess.Popen,
                 which: Callable = shutil.which):
        self._run = runner
        self._launch = launcher
        self._which = which

    def installed_version(self, app: SuiteApp) -> str | None:
        try:
            result = self._run(["dpkg-query", "-W", "-f=${Status}|${Version}", app.package],
                               capture_output=True, text=True)
        except OSError:
            return None
        status, _, version = result.stdout.partition("|")
        if result.returncode != 0 or not status.endswith("installed") or "not-installed" in status:
            return None
        return version.strip() or None

    def pick(self, assets: tuple[ReleaseAsset, ...]) -> ReleaseAsset | None:
        suffix = f"_{deb_architecture()}.deb"
        return next((a for a in assets if a.name.endswith(suffix)), None)

    def install(self, app: SuiteApp, path: str) -> None:
        # pkexec shows the system's password dialog; apt checks the package and upgrades it.
        try:
            result = self._run(["pkexec", "apt-get", "install", "-y", "--allow-downgrades",
                                os.path.abspath(path)], capture_output=True, text=True)
        except OSError as e:
            raise QuayError("Can't ask for permission to install (pkexec is missing).") from e
        if result.returncode in (126, 127):
            raise QuayError("Installing was cancelled.")
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip().splitlines()[-1:]
            raise QuayError("Installing failed" + (f": {detail[0]}" if detail else "."))

    def launch(self, app: SuiteApp) -> None:
        command = self._which(app.command)
        if not command:
            raise QuayError("Can't find the program to start.")
        self._launch([command], start_new_session=True, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


class WindowsPlatform:
    """Windows lists what Inno Setup installed under `{AppId}_is1`, for this user or for everyone."""

    KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{{{guid}}}_is1"

    def __init__(self, registry=None, launcher: Callable = subprocess.Popen):
        self._registry = registry
        self._launch = launcher

    def _read(self, app: SuiteApp, name: str) -> str | None:
        reg = self._registry
        if reg is None:
            import winreg as reg  # only exists on Windows
        for hive in (reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE):
            try:
                with reg.OpenKey(hive, self.KEY.format(guid=app.windows_guid)) as key:
                    return str(reg.QueryValueEx(key, name)[0]) or None
            except OSError:
                continue
        return None

    def installed_version(self, app: SuiteApp) -> str | None:
        return self._read(app, "DisplayVersion")

    def pick(self, assets: tuple[ReleaseAsset, ...]) -> ReleaseAsset | None:
        return next((a for a in assets if a.name.endswith("-windows-x64-setup.exe")), None)

    def install(self, app: SuiteApp, path: str) -> None:
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        try:  # setup closes the app, upgrades it in place and starts it again
            self._launch([path, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"],
                         creationflags=flags, close_fds=True)
        except OSError as e:
            raise QuayError("Couldn't start the installer.") from e

    def launch(self, app: SuiteApp) -> None:
        folder = self._read(app, "InstallLocation")
        exe = Path(folder) / app.windows_exe if folder else None
        if not exe or not exe.exists():
            raise QuayError("Can't find the program to start.")
        try:
            self._launch([str(exe)], close_fds=True)
        except OSError as e:
            raise QuayError("Couldn't start the program.") from e


class NoPlatform:
    """macOS and the rest: nothing is installed by Quay."""

    def installed_version(self, app):
        return None

    def pick(self, assets):
        return None

    def install(self, app, path):
        raise QuayError("This computer isn't supported by Quay yet.")

    def launch(self, app):
        raise QuayError("This computer isn't supported by Quay yet.")


def platform_for_this_computer():
    if sys.platform == "win32":
        return WindowsPlatform()
    if sys.platform.startswith("linux"):
        return DebPlatform()
    return NoPlatform()
