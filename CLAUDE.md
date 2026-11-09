# Quay

The Quezka suite's launcher (Linux + Windows). Since 0.4.0 its code is Rust, in the suite-rs repository
(`crates/quay`, on the shared kit; see suite-rs's CLAUDE.md). This repo holds the packaging and releases.

- `suite-rs.ref` names the suite-rs commit CI builds. To release: change the crate there (bump `version` in
  `crates/quay/Cargo.toml`), push suite-rs, put its commit here, add a CHANGELOG section and a metainfo
  `<release>`, commit, tag `vX.Y.Z` (must equal the crate's version) and push.
- CI (`.github/workflows/build.yml`): tests and builds the crate, `scripts/build_deb.sh` makes the .deb,
  `packaging/quay.iss` the Windows setup (icon from `quay --write-icon`).
- Release asset names must stay `quay_<v>_<arch>.deb` and `Quay-<v>-windows-x64-setup.exe` (Quay updates itself).
- The Inno `AppId` never changes. Commit as arsdom15@gmail.com.
- The Python version (0.3.0 and older) is in git history.
