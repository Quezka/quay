"""Command-line entry point."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .bootstrap import build_service


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    parser = argparse.ArgumentParser(prog="quay", description="Installs and updates the Quezka suite.")
    parser.add_argument("--demo", action="store_true", help="try it on made-up releases (nothing is installed)")
    parser.add_argument("--autostart", action="store_true",
                        help="started at login: check quietly, and open only when an update is waiting")
    args, qt_args = parser.parse_known_args(argv[1:])
    service = build_service(demo=args.demo, version=__version__)
    from .presentation.qt_app import run  # imported late so --help needs no display

    return run(service, [argv[0], *qt_args], quiet=args.autostart)
