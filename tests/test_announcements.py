"""Tests for the announcement parser, cache, fetcher, row and page."""

import copy
import json

import pytest
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QNetworkReply
from PyQt6.QtWidgets import QApplication, QLabel, QScrollArea

from unidesk.helpers import ann_fetcher, text_data
from unidesk.ui.widgets import NavButton

KEYS = {"schema_version", "published_at", "title", "body"}
UI = text_data.load("ui_strings")


def _item(title="Title", body="Body", published_at="2026-11-19", schema_version=1):
    return {
        "schema_version": schema_version,
        "published_at": published_at,
        "title": title,
        "body": body,
    }


def _json(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class FakeReply(QObject):
    finished = pyqtSignal()

    def __init__(self, body=b"", status=200, error=None):
        super().__init__()
        self._body = body
        self._status = status
        self._error = (
            QNetworkReply.NetworkError.NoError if error is None else error
        )
        self.deleted = False

    def readAll(self):
        return self._body

    def error(self):
        return self._error

    def attribute(self, _attribute):
        return self._status

    def deleteLater(self):
        self.deleted = True


class FakeManager(QObject):
    def __init__(self, reply, parent=None):
        super().__init__(parent)
        self.reply = reply
        self.requests = []
        self.timeout = None

    def setTransferTimeout(self, timeout):
        self.timeout = timeout

    def get(self, request):
        self.requests.append(request)
        return self.reply


class FakeNetwork:
    def __init__(self):
        self.reply = FakeReply()
        self.managers = []

    def __call__(self, parent=None):
        manager = FakeManager(self.reply, parent)
        self.managers.append(manager)
        return manager


@pytest.fixture
def net(monkeypatch):
    fake = FakeNetwork()
    monkeypatch.setattr(ann_fetcher, "QNetworkAccessManager", fake)
    return fake


@pytest.fixture
def windows(qapp):
    created = []

    def make():
        from unidesk.ui.main_window import UniOSWelcome

        window = UniOSWelcome()
        created.append(window)
        return window

    yield make
    for window in created:
        window.close()
        window.deleteLater()


def _fetch(net, **reply_args):
    net.reply = FakeReply(**reply_args)
    fetcher = ann_fetcher.AnnouncementFetcher()
    received = []
    fetcher.announcement_ready.connect(received.append)
    fetcher.start()
    net.reply.finished.emit()
    return received


# Seed


def test_seed_has_exactly_four_valid_keys():
    item = ann_fetcher.seed_announcement()
    assert set(item) == KEYS
    assert isinstance(item["schema_version"], int)
    for key in ("published_at", "title", "body"):
        assert isinstance(item[key], str)
        assert item[key].strip()
    assert len(item["body"]) <= ann_fetcher._MAX_BODY_CHARS


# pick_latest


def test_pick_latest_single_object():
    item = _item(title="Only")
    assert ann_fetcher.pick_latest(item) == item


def test_pick_latest_bare_array_uses_newest_date():
    older = _item(title="Older", published_at="2026-01-01")
    newer = _item(title="Newer", published_at="2026-12-31")
    assert ann_fetcher.pick_latest([newer, older])["title"] == "Newer"


def test_pick_latest_wrapped_form_matches_bare_array():
    older = _item(title="Older", published_at="2026-01-01")
    newer = _item(title="Newer", published_at="2026-12-31")
    wrapped = {"announcements": [older, newer]}
    assert ann_fetcher.pick_latest(wrapped)["title"] == "Newer"


@pytest.mark.parametrize(
    "data",
    [[], {"announcements": []}, "text", 42, None, {}],
)
def test_pick_latest_returns_none_for_empty_or_wrong_types(data):
    assert ann_fetcher.pick_latest(data) is None


def test_pick_latest_skips_invalid_newer_item():
    invalid = _item(title="Invalid", body="   ", published_at="2026-12-31")
    valid = _item(title="Valid", published_at="2026-01-01")
    assert ann_fetcher.pick_latest([invalid, valid])["title"] == "Valid"


def test_pick_latest_does_not_mutate_input():
    data = {"announcements": [_item(title="One"), _item(title="Two")]}
    snapshot = copy.deepcopy(data)
    ann_fetcher.pick_latest(data)
    assert data == snapshot


# _normalise


def test_normalise_rejects_slash_date():
    assert ann_fetcher._normalise(_item(published_at="19/11/2026")) is None


def test_normalise_rejects_newer_schema_version():
    assert ann_fetcher._normalise(_item(schema_version=2)) is None


def test_normalise_truncates_long_body():
    raw = _item(body="a" * 300)
    item = ann_fetcher._normalise(raw)
    assert item is not raw
    assert item["body"] == ("a" * ann_fetcher._MAX_BODY_CHARS) + "…"
    assert len(item["body"]) == ann_fetcher._MAX_BODY_CHARS + 1


# Cache path


def test_cache_path_is_under_the_current_home(isolated_home):
    expected = isolated_home / ".unios" / "unidesk" / "announcements.json"
    assert ann_fetcher.cache_path() == expected


def test_cache_path_resolves_home_on_each_call(isolated_home, tmp_path, monkeypatch):
    first = ann_fetcher.cache_path()
    other_home = tmp_path / "other-home"
    other_home.mkdir()
    monkeypatch.setenv("HOME", str(other_home))
    second = ann_fetcher.cache_path()
    assert first != second
    assert second == other_home / ".unios" / "unidesk" / "announcements.json"


# Cache read/write


def test_cache_roundtrip_preserves_four_keys(isolated_home):
    item = _item(title="Cached", body="Cached body")
    ann_fetcher.save_cached_announcement(item)
    assert ann_fetcher.read_cached_announcement() == item
    raw = json.loads(ann_fetcher.cache_path().read_text(encoding="utf-8"))
    assert set(raw) == KEYS


def test_missing_cache_returns_none(isolated_home):
    assert ann_fetcher.read_cached_announcement() is None


@pytest.mark.parametrize("text", ["", "{not json", "[]", "null"])
def test_corrupt_cache_returns_none(isolated_home, text):
    path = ann_fetcher.cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    assert ann_fetcher.read_cached_announcement() is None


def test_cache_write_failure_is_silent(isolated_home, monkeypatch):
    blocker = isolated_home / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(
        ann_fetcher, "cache_path", lambda: blocker / "announcements.json"
    )
    ann_fetcher.save_cached_announcement(_item())


# Fetcher


def test_start_issues_exactly_one_request_to_the_constant_url(qapp, net):
    fetcher = ann_fetcher.AnnouncementFetcher()
    fetcher.start()
    fetcher.start()
    assert len(net.managers) == 1
    manager = net.managers[0]
    assert len(manager.requests) == 1
    assert manager.requests[0].url().toString() == ann_fetcher.ANNOUNCEMENTS_URL
    assert manager.timeout == ann_fetcher._TRANSFER_TIMEOUT_MS


def test_200_wrapped_payload_emits_newest_once(qapp, net):
    older = _item(title="Older", published_at="2026-01-01")
    newer = _item(title="Newer", published_at="2026-12-31")
    received = _fetch(net, body=_json({"announcements": [older, newer]}))
    assert received == [newer]
    assert net.reply.deleted is True


@pytest.mark.parametrize(
    "reply_args",
    [
        {"body": b"not found", "status": 404},
        {"status": None, "error": QNetworkReply.NetworkError.TimeoutError},
        {
            "status": None,
            "error": QNetworkReply.NetworkError.ConnectionRefusedError,
        },
        {"body": b"{not json"},
        {"body": b""},
        {
            "body": _json(
                [
                    {"title": "", "body": ""},
                    {"title": "x", "published_at": "bad", "body": "y"},
                ]
            )
        },
    ],
)
def test_fetch_failures_are_silent(qapp, net, reply_args):
    assert _fetch(net, **reply_args) == []
    assert net.reply.deleted is True


# Main window row


def test_announcements_row_sits_below_nav_grid_and_above_bottom_row(
    windows, monkeypatch
):
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: _item())
    window = windows()

    main_page = window._stack.widget(0)
    layout = main_page.layout()
    items = [layout.itemAt(i) for i in range(layout.count())]
    widgets = [item.widget() for item in items]

    nav_widget = next(
        w for w in widgets if w is not None and len(w.findChildren(NavButton)) == 8
    )
    row_button = next(
        b
        for b in window.findChildren(NavButton)
        if b.text() == UI["announcements_label"]
    )
    row_widget = row_button.parentWidget()
    bottom_index = next(i for i, item in enumerate(items) if item.layout() is not None)

    nav_index = widgets.index(nav_widget)
    row_index = widgets.index(row_widget)
    assert row_index == nav_index + 1
    assert bottom_index == row_index + 1


def test_announcements_row_matches_nav_button_style(windows, monkeypatch):
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: _item())
    window = windows()

    button = next(
        b
        for b in window.findChildren(NavButton)
        if b.text() == UI["announcements_label"]
    )
    assert button.text() == "Announcements"
    assert button.property("button") == "nav"
    assert button.height() == 38


def test_announcements_row_opens_its_page(windows, monkeypatch):
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: _item())
    window = windows()

    button = next(
        b
        for b in window.findChildren(NavButton)
        if b.text() == UI["announcements_label"]
    )
    button.click()
    assert window._stack.currentIndex() == window._page_indices[
        UI["announcements_page_title"]
    ]


# Announcements page


def test_announcements_page_renders_title_date_and_body(windows, monkeypatch):
    item = _item(
        title="Page title",
        published_at="2026-11-19",
        body="Page body",
    )
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: item)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: None)
    window = windows()

    page = window._stack.widget(window._page_indices[UI["announcements_page_title"]])
    texts = [label.text() for label in page.findChildren(QLabel)]
    assert item["title"] in texts
    assert item["published_at"] in texts
    assert item["body"] in texts
    assert page.findChildren(QScrollArea)


def test_announcements_page_prefers_cached_announcement(windows, monkeypatch):
    cached = _item(title="Cached title")
    seed = _item(title="Seed title")
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: cached)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: seed)
    window = windows()

    page = window._stack.widget(window._page_indices[UI["announcements_page_title"]])
    texts = [label.text() for label in page.findChildren(QLabel)]
    assert cached["title"] in texts
    assert seed["title"] not in texts


def test_announcements_page_shows_empty_line_when_nothing_is_available(
    windows, monkeypatch
):
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: None)
    window = windows()

    page = window._stack.widget(window._page_indices[UI["announcements_page_title"]])
    empty = next(
        label
        for label in page.findChildren(QLabel)
        if label.text() == UI["announcements_empty"]
    )
    assert empty.property("role") == "muted"


# Cache updates


def test_same_fetched_item_is_saved_only_once(windows, monkeypatch):
    saved = []
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "save_cached_announcement", saved.append)
    window = windows()
    item = _item(title="Fetched")
    window._on_announcement_fetched(item)
    window._on_announcement_fetched(item)
    assert saved == [item]


def test_fetched_item_equal_to_rendered_seed_is_not_saved(windows, monkeypatch):
    saved = []
    seed = _item(title="Seed title")
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: seed)
    monkeypatch.setattr(ann_fetcher, "save_cached_announcement", saved.append)
    window = windows()
    window._on_announcement_fetched(seed)
    assert saved == []


def test_window_starts_no_fetch_until_asked(windows, net, monkeypatch):
    monkeypatch.setattr(ann_fetcher, "read_cached_announcement", lambda: None)
    monkeypatch.setattr(ann_fetcher, "seed_announcement", lambda: _item())
    window = windows()
    assert net.managers == []
    window.start_announcements()
    assert len(net.managers) == 1
    assert len(net.managers[0].requests) == 1
