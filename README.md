# Quay

Installs and updates the Quezka suite of apps (Quire, Gantry, Ligature, Folio, Bivouac, Facet, Missive) from their
GitHub releases. Linux (.deb, asks for your password once per install through the system dialog) and Windows (the
apps' setup, run silently).

    pip install -e .
    quay          # or: quay --demo, to try it on made-up releases

An app only appears installable once it has a release with a `.deb` / `-windows-x64-setup.exe`. Missive has none yet.
Quay's own entry updates Quay.

## Architecture

`domain` (the catalogue, version comparison) → `application` (`SuiteService`, ports) → `infrastructure` (GitHub feed,
Linux and Windows platforms) + `presentation` (Qt, the suite's shared `quezka-ui`); wired in `bootstrap.py`.
Tests: `pytest -q`.
