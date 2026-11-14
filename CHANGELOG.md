# Changelog

All notable changes to Quay. Versions follow [Semantic Versioning](https://semver.org).

## [0.5.0] - 2026-11-14

- The suite's new **Material 3 tonal** look: soft tonal background, white cards with big round corners, darker text, no glass.

## [0.4.2] - 2026-11-14

- **Started at login, Quay stays out of sight**: it checks for updates without a window and opens one only when there
  is something to install. It never starts filling the screen: the first window is smaller than a small screen.
- **Its own icon in the dock**, instead of an unknown app (the window now carries Quay's app id and icon).

## [0.4.1] - 2026-11-09

- The first release of the Rust Quay (0.4.0's Windows setup didn't build, so 0.4.0 was never published).

## [0.4.0] - 2026-11-09

### Changed
- **Rewritten in Rust** on the suite's new toolkit (egui + wgpu, real glass), like the coming versions of every
  app: one small program instead of a bundled Python and Qt. It starts faster and draws smoothly.
- **Each app shows its real icon**, the same one its own package installs, instead of a generic symbol.
- "What's new" is a link under the app's version, so the buttons line up.
- Downloads still have their size and checksum checked; installing still asks for your password once (Linux) or
  runs the app's own setup (Windows).

## [0.3.0] - 2026-11-04

### Added
- Stagno and Natter are in the list.
- Each app has its symbol; what needs an update comes first, with a "What's new" button, and the header says how many are waiting.
- Material 3, the Manrope typeface and Material icons, like the rest of the suite.

### Fixed
- "Update all" also installed every app you had never installed. It now updates only what you have, and says how far along it is. One that fails no longer hides the others: it's named at the end.
- Folio was described as a diagram editor.

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
