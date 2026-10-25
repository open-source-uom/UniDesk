"""@file credits_page.py
@brief Credits page listing the project contributors."""

from ...helpers.text_data import load
from ..widgets import card, qlabel, scroll_page

CREDITS = load("credits")["people"]
UI = load("ui_strings")


def build_credits_page(on_back):
    """@brief Creates the credits page, with one card per contributor from credits.json.
    @param on_back Callback run when Back is clicked.
    @return The page widget.
    """
    widget, cl = scroll_page(on_back, UI["credits_page_title"])

    for person in CREDITS:
        frame, fl = card(spacing=2)

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
