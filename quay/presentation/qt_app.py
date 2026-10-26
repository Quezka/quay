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


def run(service, argv: list[str]) -> int:
    from .main_window import MainWindow

    app = create_application(argv)
    window = MainWindow(service)
    window.show()
    return app.exec()
