from quay.application.errors import QuayError
from quay.application.ports import Release, ReleaseAsset
from quay.application.services import State, SuiteService
from quay.domain import versions
from quay.domain.catalog import CATALOG
from quay.infrastructure.platforms import DebPlatform, WindowsPlatform
import pytest


def test_versions_compare_like_people_read_them():
    assert versions.is_newer("0.36.2", "0.36.1") and versions.is_newer("0.10.0", "0.9.9")
    assert not versions.is_newer("0.36.1", "0.36.1") and not versions.is_newer("0.36", "0.36.0")
    assert versions.parse("v1.2.3-1ubuntu1") == (1, 2, 3)
    assert not versions.is_newer("garbage", "1.0") and not versions.is_newer("1.0", None)


def test_catalog_guids_are_unique():
    guids = [a.windows_guid for a in CATALOG]
    assert len(set(guids)) == len(guids)


class Feed:
    def __init__(self, versions):
        self.versions = versions
        self.downloaded = []

    def latest(self, repo):
        v = self.versions.get(repo.split("/")[-1])
        if v is None:
            return None
        return Release(v, "page", (ReleaseAsset(f"x_{v}_amd64.deb", "u", 1),))

    def download(self, asset, progress):
        progress(1, 1)
        self.downloaded.append(asset.name)
        return "/tmp/" + asset.name


class Platform:
    def __init__(self, installed):
        self.installed, self.installs, self.launched = installed, [], []

    def installed_version(self, app):
        return self.installed.get(app.key)

    def pick(self, assets):
        return assets[0] if assets else None

    def install(self, app, path):
        self.installs.append((app.key, path))
        self.installed[app.key] = "9.9.9"

    def launch(self, app):
        self.launched.append(app.key)


def service(installed, latest):
    s = SuiteService(Feed(latest), Platform(installed))
    s.remember(s.fetch())
    return s


def test_states():
    s = service({"quire": "0.36.1", "gantry": "0.6.2"}, {"quire": "0.36.2", "gantry": "0.6.2", "folio": "0.3.3"})
    state = {x.app.key: x.state for x in s.statuses()}
    assert state["quire"] is State.UPDATE and state["gantry"] is State.UP_TO_DATE
    assert state["folio"] is State.NOT_INSTALLED and state["missive"] is State.UNAVAILABLE


def test_install_downloads_then_installs():
    s = service({}, {"folio": "0.3.3"})
    path = s.prepare("folio", lambda a, b: None)
    s.install("folio", path)
    assert s._platform.installs == [("folio", path)]
    assert {x.app.key: x.state for x in s.statuses()}["folio"] is State.UP_TO_DATE


def test_nothing_to_download_is_an_error():
    s = service({}, {})
    with pytest.raises(QuayError):
        s.prepare("missive", lambda a, b: None)


class Result:
    def __init__(self, code=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = code, out, err


def test_deb_platform_reads_dpkg_and_installs_with_pkexec():
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        if cmd[0] == "dpkg-query":
            return Result(0, "install ok installed|0.36.1")
        return Result(0)
    p = DebPlatform(runner=run)
    app = CATALOG[0]
    assert p.installed_version(app) == "0.36.1"
    p.install(app, "x.deb")
    assert calls[-1][:3] == ["pkexec", "apt-get", "install"]


def test_deb_platform_knows_a_removed_package():
    p = DebPlatform(runner=lambda cmd, **kw: Result(0, "deinstall ok config-files|0.1"))
    assert p.installed_version(CATALOG[0]) is None
    p = DebPlatform(runner=lambda cmd, **kw: Result(1))
    assert p.installed_version(CATALOG[0]) is None


def test_cancelled_install_is_reported():
    p = DebPlatform(runner=lambda cmd, **kw: Result(126))
    with pytest.raises(QuayError):
        p.install(CATALOG[0], "x.deb")


class FakeRegistry:
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE = "user", "machine"

    def __init__(self, values):
        self.values = values

    class _Key:
        def __init__(self, v):
            self.v = v

        def __enter__(self):
            return self.v

        def __exit__(self, *a):
            return False

    def OpenKey(self, hive, path):
        if (hive, path) not in self.values:
            raise OSError
        return self._Key(self.values[(hive, path)])

    def QueryValueEx(self, key, name):
        return (key[name], 1)


def test_windows_platform_reads_the_uninstall_entry():
    app = CATALOG[0]
    path = WindowsPlatform.KEY.format(guid=app.windows_guid)
    reg = FakeRegistry({("machine", path): {"DisplayVersion": "0.36.1", "InstallLocation": "C:\\Quire"}})
    p = WindowsPlatform(registry=reg)
    assert p.installed_version(app) == "0.36.1"
    assert p.installed_version(CATALOG[1]) is None
