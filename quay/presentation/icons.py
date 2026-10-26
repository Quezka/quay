"""The suite's icons (quezka_ui.icons), pointed at this app's own icon."""
from pathlib import Path

from quezka_ui import icons as _shared

APP_ICON = Path(__file__).resolve().parent.parent / "assets" / "icon.svg"
_shared.configure(APP_ICON, "quay")


def __getattr__(name):
    return getattr(_shared, name)
