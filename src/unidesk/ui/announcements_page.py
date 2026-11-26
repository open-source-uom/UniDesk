"""@file announcements_page.py
@brief Announcements page showing the current announcement."""

from ..helpers import ann_fetcher
from ..helpers.text_data import load
from .widgets import card, qlabel, scroll_page

UI = load("ui_strings")


def build_announcements_page(on_back):
    """@brief Creates the announcements page with the current announcement.
    @param on_back Callback run when Back is clicked.
    @return The page widget.
    """
    widget, cl = scroll_page(on_back, UI["announcements_page_title"])

    item = ann_fetcher.current_announcement()
    if item is None:
        cl.addWidget(qlabel(UI["announcements_empty"], role="muted"))
    else:
        frame, fl = card(spacing=4)
        fl.addWidget(qlabel(item["title"], role="card-title"))
        fl.addWidget(qlabel(item["published_at"], role="muted"))
        fl.addWidget(qlabel(item["body"], role="body", wrap=True))
        cl.addWidget(frame)

    cl.addStretch()
    return widget
