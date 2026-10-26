"""One window: a card per app of the suite with Install, Update or Open."""
from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)
from quezka_ui import fit

from ..application.errors import QuayError
from ..application.services import AppStatus, State
from .i18n import _
from .widgets import Card, Page, button, label, primary_button, scrolling


class Worker(QObject):
    """Runs one network job off the UI thread. Writing to the machine happens back on it."""

    progress = Signal(int, int)
    finished = Signal(object, str)  # result, error text ("" when it worked)

    def __init__(self, job):
        super().__init__()
        self._job = job

    def run(self):
        try:
            self.finished.emit(self._job(self.progress.emit), "")
        except QuayError as e:
            self.finished.emit(None, str(e))
        except Exception as e:  # noqa: BLE001  (never let a thread die silently)
            self.finished.emit(None, f"{type(e).__name__}: {e}")


class AppCard(Card):
    def __init__(self, status: AppStatus, window: "MainWindow"):
        super().__init__(padding=14)
        self.status = status
        self._window = window
        row = QHBoxLayout()
        row.setSpacing(12)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.addWidget(QLabel(status.app.name, objectName="cardTitle"))
        texts.addWidget(label(_(status.app.tagline)))
        self.detail = label(self._detail(status), "faint")
        texts.addWidget(self.detail)
        row.addLayout(texts, 1)
        self.progress = QProgressBar()
        self.progress.setFixedWidth(120)
        self.progress.setTextVisible(False)
        self.progress.hide()
        row.addWidget(self.progress, 0, Qt.AlignVCenter)
        self.action = self._action(status)
        row.addWidget(self.action, 0, Qt.AlignVCenter)
        self.open_button = None
        if status.installed:
            self.open_button = button(_("Open"))
            self.open_button.clicked.connect(lambda: window.open_app(status.app.key))
            row.addWidget(self.open_button, 0, Qt.AlignVCenter)
        self.body.addLayout(row)

    @staticmethod
    def _detail(s: AppStatus) -> str:
        if s.state is State.UNAVAILABLE:
            return _("No download for this computer yet")
        if s.state is State.NOT_INSTALLED:
            return _("Not installed · latest {latest}").format(latest=s.latest)
        if s.state is State.UPDATE:
            return _("Installed {installed} · {latest} is available").format(installed=s.installed, latest=s.latest)
        return _("Installed {installed} · up to date").format(installed=s.installed)

    def _action(self, s: AppStatus) -> QPushButton:
        if s.state is State.NOT_INSTALLED:
            b = primary_button(_("Install"), "download")
        elif s.state is State.UPDATE:
            b = primary_button(_("Update"), "refresh")
        else:
            b = button(_("Up to date") if s.installed else _("Unavailable"))
            b.setEnabled(False)
            if s.state is State.UNAVAILABLE and s.page_url:
                b.setText(_("Releases page"))
                b.setEnabled(True)
                b.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(s.page_url)))
                return b
        if b.isEnabled():
            b.clicked.connect(lambda: self._window.install(s.app.key, self))
        return b

    def busy(self, on: bool):
        self.action.setEnabled(not on)
        self.progress.setVisible(on)
        if on:
            self.progress.setRange(0, 0)

    def set_installing(self):
        self.progress.setRange(0, 0)  # no percentage while apt works: just "busy"
        self.progress.show()

    def set_progress(self, done: int, total: int):
        self.progress.setRange(0, max(total, 1))
        self.progress.setValue(done)


class MainWindow(QWidget):
    def __init__(self, service, quiet: bool = False):
        super().__init__()
        self._service = service
        self._quiet = quiet
        self._threads: list[tuple[QThread, Worker, object]] = []
        self._cards: dict[str, AppCard] = {}
        self.setWindowTitle("Quay")
        self.page = Page()
        self.page.title.setText(_("The suite"))
        self.page.subtitle.setText(_("Install and update the apps"))
        self.refresh_button = button(_("Check for updates"), "refresh")
        self.refresh_button.clicked.connect(self.check)
        self.update_all = primary_button(_("Update all"), "download")
        self.update_all.clicked.connect(self.install_all)
        self.page.add_actions(self.refresh_button, self.update_all)
        self.message = label("", "muted")
        self.page.root.addWidget(self.message)
        self.list = QVBoxLayout()
        self.list.setSpacing(10)
        self.page.root.addWidget(scrolling(self.list), 1)
        self.autostart = QCheckBox(_("Start with the computer"))
        self.autostart.setVisible(service.autostart_supported())
        self.autostart.setChecked(service.autostart_enabled())
        self.autostart.toggled.connect(service.set_autostart)
        self.page.root.addWidget(self.autostart)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.page)
        self._show(self._service.statuses())
        fit.clamp_window(self, 640, 720, 460, 420)
        self._fit_width(exact=True)  # opens at the width the cards need, not a guess
        self.check()

    # --- showing --------------------------------------------------------------------------
    def _show(self, statuses: list[AppStatus]):
        while self.list.count():
            item = self.list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards = {}
        for status in statuses:
            card = AppCard(status, self)
            self._cards[status.app.key] = card
            self.list.addWidget(card)
        self.list.addStretch()
        self.update_all.setEnabled(any(s.state in (State.UPDATE, State.NOT_INSTALLED) for s in statuses))
        self._fit_width()

    def _fit_width(self, exact: bool = False):
        """Wide enough for the widest card and the header, with the page's margins and the scroll bar.
        Only ever grows the window: a width the user chose is kept."""
        margins = self.page.root.contentsMargins()
        cards = max((c.sizeHint().width() for c in self._cards.values()), default=0)
        header = self.page.header.sizeHint().width()
        scrollbar = 18
        needed = max(cards + scrollbar, header) + margins.left() + margins.right()
        self.setMinimumWidth(needed)
        if exact or self.width() < needed:
            self.resize(needed, self.height())

    # --- jobs -----------------------------------------------------------------------------
    def _run(self, job, done):
        thread, worker = QThread(self), Worker(job)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        # A bound method of this window, so the answer is delivered on the UI thread (a lambda
        # would run on the worker's).
        worker.finished.connect(self._on_finished)
        self._threads.append((thread, worker, done))
        thread.start()
        return worker

    @Slot(object, str)
    def _on_finished(self, result, error):
        worker = self.sender()
        entry = next(t for t in self._threads if t[1] is worker)
        thread, _worker, done = entry
        thread.quit()
        thread.wait()
        self._threads.remove(entry)
        done(result, error)

    def check(self):
        self.refresh_button.setEnabled(False)
        self.message.setText(_("Checking…"))
        self._run(lambda progress: self._service.fetch(), self._checked)

    def _checked(self, releases, error):
        self.refresh_button.setEnabled(True)
        if error:
            self.message.setText(_(error))
            self._after_quiet_check_failed()
            return
        self.message.setText("")
        self._service.remember(releases)
        self._show(self._service.statuses())
        self._after_quiet_check()

    def _after_quiet_check_failed(self):
        if self._quiet:  # offline at login: nothing to say
            QApplication.quit()

    def _after_quiet_check(self):
        """Started at login: stay out of the way unless something is waiting."""
        if not self._quiet:
            return
        self._quiet = False
        if self._service.has_updates():
            self.show()
        else:
            QApplication.quit()

    def install(self, key: str, card: AppCard | None = None, then=None):
        card = card or self._cards.get(key)
        if card:
            card.busy(True)
        worker = self._run(lambda progress: self._download(key, progress),
                           lambda path, error: self._downloaded(key, card, path, error, then))
        if card:
            worker.progress.connect(card.set_progress)

    def _download(self, key, progress):
        return self._service.prepare(key, progress)

    def _downloaded(self, key, card, path, error, then):
        if error:
            return self._installed(key, card, None, error, then)
        # The install itself (apt, the password dialog, the setup) can take a minute: off the UI thread too.
        if card:
            card.set_installing()
        self.message.setText(_("Installing…"))
        self._run(lambda progress: self._service.install(key, path),
                  lambda result, err: self._installed(key, card, result, err, then))

    def _installed(self, key, card, _result, error, then):
        if card:
            card.busy(False)
        if error:
            self.message.setText(_(error))
        else:
            name = self._cards[key].status.app.name if key in self._cards else ""
            self.message.setText(_("{name} is installed.").format(name=name))
            self._show(self._service.statuses())
        if then:
            then()

    def install_all(self):
        pending = [s.app.key for s in self._service.statuses()
                   if s.state in (State.UPDATE, State.NOT_INSTALLED)]

        def step():
            if pending:
                self.install(pending.pop(0), then=step)
        step()

    def open_app(self, key: str):
        try:
            self._service.launch(key)
        except QuayError as e:
            QMessageBox.warning(self, "Quay", _(str(e)))
