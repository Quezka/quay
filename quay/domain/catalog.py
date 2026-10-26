"""The apps of the suite: where each is released and how each platform knows it.

`package` is the .deb name (its command is the same); `windows_guid` is the Inno Setup AppId, which
is also the name of its entry in Windows' list of installed programs (`{guid}_is1`).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SuiteApp:
    key: str
    name: str
    tagline: str
    repo: str  # "owner/name" on GitHub
    windows_guid: str
    windows_exe: str

    @property
    def package(self) -> str:
        return self.key

    @property
    def command(self) -> str:
        return self.key


CATALOG: tuple[SuiteApp, ...] = (
    SuiteApp("quire", "Quire", "Notes, day planner and school timetable",
             "Quezka/quire", "A8A67700-9677-45B8-8C82-78A07D4DFD71", "Quire.exe"),
    SuiteApp("gantry", "Gantry", "Gantt charts that open and save GanttProject files",
             "Quezka/gantry", "76971ED7-094F-4440-AF21-DE3524CFAEB4", "Gantry.exe"),
    SuiteApp("ligature", "Ligature", "ER and UML class diagrams, with SQL generation",
             "Quezka/ligature", "3C1E7B52-6A0D-4F2B-9E4A-8D5F21C7A9B6", "Ligature.exe"),
    SuiteApp("folio", "Folio", "ER and UML class diagrams in a comfortable look",
             "Quezka/folio", "5E0B7A44-2C1D-4F6A-8B93-71D2E4A06C58", "Folio.exe"),
    SuiteApp("bivouac", "Bivouac", "Base camp for CTF study: flashcards, drills and cheatsheets",
             "Quezka/bivouac", "8F4A2C61-3B7E-4D95-A0C8-5E1B9D7F24A3", "Bivouac.exe"),
    SuiteApp("facet", "Facet", "A light 3D model viewer with precise measuring",
             "Quezka/facet", "8B4D2F61-1E7A-4C93-A5D0-6F3B9E21C8A7", "Facet.exe"),
    SuiteApp("missive", "Missive", "A calm, private, read-only mail client",
             "Quezka/missive", "B7C3D9E2-4A15-4E68-9F20-3D8A6C1E5B74", "Missive.exe"),
    SuiteApp("quay", "Quay", "This launcher: installs and updates the suite",
             "Quezka/quay", "C2F81A6D-93B4-4D07-A5E1-7B3C0D94F2A8", "Quay.exe"),
)


def by_key(key: str) -> SuiteApp:
    return next(app for app in CATALOG if app.key == key)
