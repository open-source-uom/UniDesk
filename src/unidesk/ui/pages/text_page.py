from PyQt6.QtCore import Qt

from ...helpers.text_data import pages
from ..widgets import qlabel, scroll_page

PAGES = pages()


def build_text_page(key, on_back):
    data = PAGES[key]
    widget, cl = scroll_page(on_back, key)

    body = qlabel(data["body"], role="body", wrap=True)
    body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    cl.addWidget(body)
    cl.addStretch()

    return widget
