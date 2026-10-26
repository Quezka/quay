# Quay

Python 3.10+ / PySide6 launcher for the Quezka suite (Linux + Windows). Same layers, toolkit (`quezka-ui`) and release
process as Quire: `domain` → `application` → `infrastructure` + `presentation`, enforced by `tests/test_architecture.py`.

- Run: `.venv/bin/quay --demo`. Test: `.venv/bin/python -m pytest -q`.
- The catalogue is `domain/catalog.py`. A new app needs its repo, its deb/command name and its Inno `AppId`
  (the Windows uninstall key is `{AppId}_is1`); every AppId must be unique (a test checks).
- Network work (`SuiteService.fetch`/`prepare`) runs on a worker thread; installing runs back on the UI thread.
- Release asset names must stay `<name>_<v>_<arch>.deb` and `<Name>-<v>-windows-x64-setup.exe`.
- UI text goes through `_()` with Russian and Italian in `presentation/locales`.
- Commit as arsdom15@gmail.com; release by bumping `__version__`, CHANGELOG, metainfo, tag `vX.Y.Z`.
