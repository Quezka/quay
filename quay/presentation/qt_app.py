"""Starts the Qt event loop around an already-wired service."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication
from quezka_ui.app import create_application as _create

from .. import APP_ID, APP_NAME
from .icons import APP_ICON  # noqa: F401  (the shared module; configured by create_application)

ICON = Path(__file__).resolve().parent.parent / "assets" / "icon.svg"


def create_application(argv: list[str]) -> QApplication:
    return _create(argv, name=APP_NAME, app_id=APP_ID, icon=ICON, locale_package="quay.presentation.locales")


def run(service, argv: list[str], quiet: bool = False) -> int:
    """`quiet` is how login starts it: no window unless an update is waiting."""
    from PySide6.QtCore import QSettings

    from .main_window import MainWindow

    app = create_application(argv)
    settings = QSettings()
    if service.autostart_supported() and not settings.value("autostart_asked", False, bool):
        settings.setValue("autostart_asked", True)  # the first run turns it on; the checkbox is the way out
        service.set_autostart(True)
    window = MainWindow(service, quiet=quiet)
    if not quiet:
        window.show()
    return app.exec()
