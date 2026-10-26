# Changelog

All notable changes to Quay. Versions follow [Semantic Versioning](https://semver.org).

## [0.2.3] - 2026-10-27

Fixed: the compact text size now reaches labels, buttons, menus and lists too (the desktop theme was keeping them at the system's larger size), so the whole interface really is smaller.

## [0.2.2] - 2026-10-27

Fixed: the window froze while an app was being installed or updated (the install ran on the window's own thread). It now runs in the background and the card shows it is busy.

## [0.2.1] - 2026-10-27

The window opens wide enough for every app's card and header (and grows if an update makes a line longer), instead of a fixed width. Compact interface from the shared toolkit 0.5.0.

## [0.2.0] - 2026-10-27

Quay starts when you log in: it checks quietly and opens its window only when an update is waiting. "Start with the computer" turns it off (on by default the first time it runs).

## [0.1.0] - 2026-10-26

First release: a window with a card per app of the suite (Quire, Gantry, Ligature, Folio, Bivouac, Facet, Missive,
and Quay itself) showing what is installed and what is new, with Install, Update, Update all and Open. Downloads come
from each app's GitHub release and are checked against its checksum. Linux installs the .deb with `pkexec apt-get`;
Windows runs the Inno setup silently. `quay --demo` tries it on made-up releases.
