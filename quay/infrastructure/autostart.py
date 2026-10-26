"""Starting Quay at login: a desktop entry on Linux, the Run key on Windows."""
from __future__ import annotations

import os
import sys
from pathlib import Path

LINUX_ENTRY = """[Desktop Entry]
Type=Application
Name=Quay
Comment=Checks for updates to the Quezka suite
Exec=quay --autostart
Icon=io.github.quezka.Quay
Terminal=false
X-GNOME-Autostart-enabled=true
"""


class LinuxAutostart:
    def __init__(self, folder: Path | None = None):
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        self._file = (folder or base / "autostart") / "io.github.quezka.Quay.desktop"

    def enabled(self) -> bool:
        return self._file.exists()

    def set(self, enabled: bool) -> None:
        if enabled:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            self._file.write_text(LINUX_ENTRY, encoding="utf-8")
        else:
            self._file.unlink(missing_ok=True)


class WindowsAutostart:
    KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    NAME = "Quay"

    def __init__(self, registry=None, command: str | None = None):
        self._registry = registry
        self._command = command or f'"{sys.executable}" --autostart'

    def _reg(self):
        if self._registry is not None:
            return self._registry
        import winreg  # only exists on Windows
        return winreg

    def enabled(self) -> bool:
        reg = self._reg()
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, self.KEY) as key:
                reg.QueryValueEx(key, self.NAME)
            return True
        except OSError:
            return False

    def set(self, enabled: bool) -> None:
        reg = self._reg()
        with reg.OpenKey(reg.HKEY_CURRENT_USER, self.KEY, 0, reg.KEY_SET_VALUE) as key:
            if enabled:
                reg.SetValueEx(key, self.NAME, 0, reg.REG_SZ, self._command)
            else:
                try:
                    reg.DeleteValue(key, self.NAME)
                except OSError:
                    pass


def autostart_for_this_computer():
    if sys.platform == "win32":
        return WindowsAutostart()
    if sys.platform.startswith("linux"):
        return LinuxAutostart()
    return None
