"""@file text_page.py
@brief Plain text subpages defined in pages.json."""

from PyQt6.QtCore import Qt

from ...helpers.text_data import pages
from ..widgets import qlabel, scroll_page

PAGES = pages()


def build_text_page(key, on_back):
    """@brief Creates the scrollable text page for one pages.json entry.
    @param key Title of the page in pages.json, also shown in the back bar.
    @param on_back Callback run when Back is clicked.
    @return The page widget.
    """
    data = PAGES[key]
    widget, cl = scroll_page(on_back, key)

    body = qlabel(data["body"], role="body", wrap=True)
    body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    cl.addWidget(body)
    cl.addStretch()

    return widget
