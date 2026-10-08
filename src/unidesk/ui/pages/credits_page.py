from PyQt6.QtWidgets import QFrame, QVBoxLayout

from ...helpers.text_data import load
from ...styles.loader import load_qss
from ..widgets import qlabel, scroll_page

CREDITS = load("credits")["people"]
UI = load("ui_strings")


def build_credits_page(on_back):
    widget, cl = scroll_page(on_back, UI["credits_page_title"])

    for person in CREDITS:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setProperty("layout", "card")
        frame.setStyleSheet(load_qss("widgets/layout.qss"))
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(14, 10, 14, 10)
        fl.setSpacing(2)

        name = qlabel(person["name"], role="card-title")
        fl.addWidget(name)

        role = qlabel(person["role"], role="muted")
        fl.addWidget(role)

        if person.get("projects"):
            proj = qlabel(
                UI["projects_prefix"] + ", ".join(person["projects"]),
                role="accent",
            )
            fl.addWidget(proj)

        cl.addWidget(frame)

    cl.addStretch()
    return widget
