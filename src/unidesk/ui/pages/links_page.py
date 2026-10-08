from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from ...helpers.text_data import load
from ...styles.loader import load_qss
from ..widgets import qlabel, scroll_page

LINKS = load("links")["links"]
UI = load("ui_strings")


def build_links_page(on_back):
    widget, cl = scroll_page(on_back, UI["links_page_title"])

    for link in LINKS:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setProperty("layout", "card")
        frame.setStyleSheet(load_qss("widgets/layout.qss"))
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(14, 10, 14, 10)
        fl.setSpacing(6)

        name = qlabel(link["label"], role="card-title")
        fl.addWidget(name)

        btn = QPushButton(UI["open_link_button"])
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("button", "link")
        btn.setStyleSheet(load_qss("widgets/controls.qss"))
        btn.clicked.connect(lambda _, u=link["url"]: QDesktopServices.openUrl(QUrl(u)))
        fl.addWidget(btn)

        cl.addWidget(frame)

    cl.addStretch()
    return widget
