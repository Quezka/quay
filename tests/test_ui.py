import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from quay.bootstrap import build_service


def test_window_lists_every_app_and_updates(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    from quay.presentation.qt_app import create_application
    from quay.presentation.main_window import MainWindow
    from PySide6.QtCore import QCoreApplication
    app = create_application(["quay"])
    window = MainWindow(build_service(demo=True))
    for _ in range(100):
        QCoreApplication.processEvents()
        if not window._threads:
            break
    assert set(window._cards) == {"quire", "gantry", "ligature", "folio", "bivouac", "facet", "missive", "quay"}
    assert window._cards["quire"].status.state.value == "update"
    assert window._cards["missive"].status.state.value == "unavailable"
    window.close()
    app.processEvents()


def test_update_button_installs_and_refreshes(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    from quay.presentation.qt_app import create_application
    from quay.presentation.main_window import MainWindow
    from PySide6.QtCore import QCoreApplication
    import time
    app = create_application(["quay"])
    service = build_service(demo=True)
    window = MainWindow(service)

    def settle():
        end = time.time() + 10
        while time.time() < end:
            QCoreApplication.processEvents()
            if not window._threads:
                return
            time.sleep(0.01)
    settle()
    window._cards["quire"].action.click()
    settle()
    assert service.statuses()[0].installed == "0.36.2"
    assert window._cards["quire"].status.state.value == "up_to_date"
    window.close()


def test_quiet_start_stays_hidden_without_updates(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    from quay.presentation.qt_app import create_application
    from quay.presentation.main_window import MainWindow
    from PySide6.QtCore import QCoreApplication
    import time
    app = create_application(["quay"])
    service = build_service(demo=True)  # quire and ligature have updates
    window = MainWindow(service, quiet=True)
    end = time.time() + 10
    while time.time() < end and window._quiet:
        QCoreApplication.processEvents()
        time.sleep(0.01)
    assert window.isVisible()  # something is waiting, so it opened
    window.close()
