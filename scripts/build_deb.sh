#!/usr/bin/env bash
# Wraps the Rust Quay binary into a .deb.   scripts/build_deb.sh <quay binary> <version> <out dir>
#   /usr/bin/quay, the desktop entry, the metainfo, the icon (SVG + 256 px PNG) named io.github.quezka.Quay.
set -euo pipefail
bin=$1 version=$2 out=$3
here=$(cd "$(dirname "$0")/.." && pwd)
id=io.github.quezka.Quay
arch=$(dpkg --print-architecture)
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
install -Dm755 "$bin" "$stage/usr/bin/quay"
install -Dm644 "$here/packaging/$id.desktop" "$stage/usr/share/applications/$id.desktop"
install -Dm644 "$here/packaging/$id.metainfo.xml" "$stage/usr/share/metainfo/$id.metainfo.xml"
install -Dm644 "$here/packaging/icon.svg" "$stage/usr/share/icons/hicolor/scalable/apps/$id.svg"
mkdir -p "$stage/usr/share/icons/hicolor/256x256/apps"
"$bin" --write-icon "$stage/usr/share/icons/hicolor/256x256/apps/$id.png"
mkdir -p "$stage/usr/share/doc/quay"
cat > "$stage/usr/share/doc/quay/copyright" <<COPY
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Quay
Source: https://github.com/Quezka/quay

Files: *
Copyright: $(date +%Y) Quezka <arsdom15@gmail.com>
License: GPL-3.0-only
 On Debian systems, the full text of the GNU General Public License version 3
 can be found in /usr/share/common-licenses/GPL-3.
COPY
size=$(du -sk "$stage/usr" | cut -f1)
mkdir -p "$stage/DEBIAN"
cat > "$stage/DEBIAN/control" <<CONTROL
Package: quay
Version: $version
Architecture: $arch
Maintainer: Quezka <arsdom15@gmail.com>
Installed-Size: $size
Depends: libc6, curl, pkexec | policykit-1, libxkbcommon0, libwayland-client0, libvulkan1 | libegl1
Section: utils
Priority: optional
Homepage: https://github.com/Quezka/quay
Description: Installs and updates the Quezka suite of apps
 Quay lists the apps of the Quezka suite, installs the ones you pick
 and keeps them up to date from their GitHub releases.
CONTROL
mkdir -p "$out"
dpkg-deb --root-owner-group -Zxz --build "$stage" "$out/quay_${version}_${arch}.deb"
