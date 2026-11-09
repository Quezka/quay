# Quay

Installs and updates the Quezka suite of apps (Quire, Gantry, Ligature, Folio, Bivouac, Facet, Missive, Stagno, Natter) from their
GitHub releases. Linux (.deb, asks for your password once per install through the system dialog) and Windows (the
apps' setup, run silently).

Written in Rust in [suite-rs](https://github.com/Quezka/suite-rs) (`crates/quay`):

    cargo run -p quay -- --demo     # made-up releases, nothing is installed

An app only appears installable once it has a release with a `.deb` / `-windows-x64-setup.exe`.
Quay's own entry updates Quay.

## Architecture

See `crates/quay` in suite-rs: `domain` (catalogue, versions) → `application` (`SuiteService`, ports) →
`infrastructure` (GitHub through curl, .deb / Windows setup, autostart, bundled icons) + `presentation` (egui on the
suite's kit). This repo builds and releases it (`suite-rs.ref`, `.github/workflows/build.yml`).
