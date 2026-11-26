"""@file ann_fetcher.py
@brief Fetches, parses and caches the UniDesk announcement."""

import json
import re
from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from .text_data import load

ANNOUNCEMENTS_URL = (
    "https://open-source-uom.github.io/unios-apps-data/unidesk/announcements.json"
)
SUPPORTED_SCHEMA_VERSION = 1
_TRANSFER_TIMEOUT_MS = 8000
_MAX_BODY_CHARS = 240
_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")


def cache_path():
    """@brief Returns the cached announcement path in the user's home directory.
    @return A Path under ~/.unios/unidesk/.
    """
    return Path.home() / ".unios" / "unidesk" / "announcements.json"


def _normalise(raw):  # pylint: disable=too-many-return-statements
    """@brief Validates one raw announcement and returns a clean copy.
    @param raw A candidate announcement object.
    @return A new dict with the four supported keys, or None if raw is invalid.
    """
    if not isinstance(raw, dict):
        return None

    title = raw.get("title")
    body = raw.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        return None
    title = title.strip()
    body = body.strip()
    if not title or not body:
        return None

    published_at = raw.get("published_at")
    if not isinstance(published_at, str) or not _DATE_PREFIX.match(published_at):
        return None
    try:
        date.fromisoformat(published_at[:10])
    except ValueError:
        return None

    schema_version = raw.get("schema_version")
    if not isinstance(schema_version, int):
        schema_version = 1
    elif schema_version > SUPPORTED_SCHEMA_VERSION:
        return None

    if len(body) > _MAX_BODY_CHARS:
        body = body[:_MAX_BODY_CHARS] + "…"

    return {
        "schema_version": schema_version,
        "published_at": published_at,
        "title": title,
        "body": body,
    }


def pick_latest(data):
    """@brief Picks the newest valid announcement from a supported payload shape.
    @param data A single object, a bare array or {"announcements": [...]}.
    @return The newest normalised announcement, or None when nothing is valid.
    """
    if isinstance(data, dict):
        if "announcements" in data:
            items = data.get("announcements")
            if not isinstance(items, list):
                return None
        else:
            items = [data]
    elif isinstance(data, list):
        items = data
    else:
        return None

    candidates = []
    for raw in items:
        item = _normalise(raw)
        if item is not None:
            candidates.append(item)
    if not candidates:
        return None

    return max(
        candidates,
        key=lambda item: date.fromisoformat(item["published_at"][:10]),
    )


def parse_payload(text):
    """@brief Parses fetched or cached announcement text.
    @param text Raw JSON text.
    @return The newest normalised announcement, or None on any parse failure.
    """
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return pick_latest(data)


def seed_announcement():
    """@brief Returns the bundled announcement shown when no cache exists.
    @return The normalised seed announcement, or None if the seed is invalid.
    """
    return pick_latest(load("announcements"))


def read_cached_announcement():
    """@brief Reads the cached announcement from the user's home directory.
    @return The newest normalised cached announcement, or None when unavailable.
    """
    try:
        text = cache_path().read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return None
    return parse_payload(text)


def current_announcement():
    """@brief Returns the cached announcement, falling back to the bundled seed.
    @return The current normalised announcement, or None when neither is available.
    """
    item = read_cached_announcement()
    if item is None:
        item = seed_announcement()
    return item


def save_cached_announcement(item):
    """@brief Writes the announcement cache, ignoring filesystem failures.
    @param item The announcement dict to cache.
    """
    try:
        path = cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(item, handle, indent=2)
    except OSError:
        pass


class AnnouncementFetcher(QObject):
    """@brief Fetches the remote announcement once and emits it when valid."""

    announcement_ready = pyqtSignal(dict)

    def __init__(self, parent=None):
        """@brief Creates a fetcher that does no work until start() is called.
        @param parent Optional Qt parent.
        """
        super().__init__(parent)
        self._reply = None
        self._manager = None

    def start(self):
        """@brief Issues one GET request, unless a reply is already in flight."""
        if self._reply is not None:
            return
        manager = QNetworkAccessManager()
        manager.setTransferTimeout(_TRANSFER_TIMEOUT_MS)
        request = QNetworkRequest(QUrl(ANNOUNCEMENTS_URL))
        self._manager = manager
        self._reply = manager.get(request)
        self._reply.finished.connect(self._on_finished)

    def _on_finished(self):
        """@brief Decodes the reply and emits the announcement when it is valid."""
        try:
            reply = self._reply
            if reply is None:
                return
            status = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute
            )
            if status != 200:
                return
            payload = reply.readAll()
            if isinstance(payload, str):
                text = payload
            else:
                text = bytes(payload).decode("utf-8")
            item = parse_payload(text)
            if item is not None:
                self.announcement_ready.emit(item)
        except Exception:  # pylint: disable=broad-except  # noqa: BLE001
            return
        finally:
            if self._reply is not None:
                self._reply.deleteLater()
                self._reply = None
