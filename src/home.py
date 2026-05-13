import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QStackedWidget, QScrollArea,
    QApplication, QMainWindow
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from pages import PAGES
from credits import CREDITS
from links import LINKS


FOOTER_LINKS = [
    {"label": "Discord", "url": "https://discord.gg/FJbv84uT"},
    {"label": "GitHub",  "url": "https://github.com/"},
    {"label": "Website", "url": "https://opensource.uom.gr"},
]

NAV_LEFT  = ["Introduction", "Features", "Links", "FAQ"]
NAV_RIGHT = ["Community", "Source Code", "Contribute", "Credits"]


# Helpers

def _qlabel(text, size=12, color="#cdd6f4", bold=False, wrap=False):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"background: transparent; border: none; color: {color}; "
        f"font-size: {size}px; font-weight: {'bold' if bold else 'normal'};"
    )
    if wrap:
        lbl.setWordWrap(True)
    return lbl


def _divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: #2d1f3d; border: none;")
    return line


def _back_bar(title, on_back):
    bar = QWidget()
    bar.setFixedHeight(40)
    bar.setStyleSheet("background: #110d1a;")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(12, 0, 12, 0)

    btn = QPushButton("← Back")
    btn.setFixedWidth(70)
    btn.setStyleSheet(
        "background: transparent; border: none; color: #a6adc8; "
        "font-size: 12px; text-align: left;"
    )
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.clicked.connect(on_back)
    layout.addWidget(btn)

    lbl = QLabel(title)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        "background: transparent; border: none; color: #cdd6f4; "
        "font-size: 13px; font-weight: bold;"
    )
    layout.addWidget(lbl, stretch=1)
    layout.addSpacing(70)
    return bar


def _scroll_page(on_back, title):
    """Returns (outer_widget, content_layout) with back bar already added."""
    widget = QWidget()
    outer = QVBoxLayout(widget)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    outer.addWidget(_back_bar(title, on_back))
    outer.addWidget(_divider())

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setStyleSheet("background: #1a1226;")
    outer.addWidget(scroll)

    content = QWidget()
    content.setStyleSheet("background: transparent;")
    scroll.setWidget(content)

    cl = QVBoxLayout(content)
    cl.setContentsMargins(24, 20, 24, 20)
    cl.setSpacing(10)

    outer.addWidget(_divider())
    outer.addWidget(_footer())

    return widget, cl


def _footer():
    footer = QWidget()
    footer.setFixedHeight(40)
    footer.setStyleSheet("background: #110d1a;")
    ft = QHBoxLayout(footer)
    ft.setContentsMargins(14, 0, 14, 0)
    ft.addWidget(_qlabel("Open Source UoM · 2026", size=11, color="#585b70"))
    ft.addStretch()
    for link in FOOTER_LINKS:
        b = QPushButton(link["label"])
        b.setStyleSheet(
            "background: transparent; border: none; color: #8b5897; font-size: 11px;"
        )
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda _, u=link["url"]: QDesktopServices.openUrl(QUrl(u)))
        ft.addWidget(b)
    return footer


# Page Builders

def build_text_page(key, on_back):
    data = PAGES[key]
    widget, cl = _scroll_page(on_back, key)

    body = _qlabel(data["body"], size=12, color="#a6adc8", wrap=True)
    body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    cl.addWidget(body)
    cl.addStretch()

    return widget


def build_credits_page(on_back):
    widget, cl = _scroll_page(on_back, "Credits")

    for person in CREDITS:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background-color: #2d1f3d; border: 1px solid #8b5897; border-radius: 5px; }"
        )
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(14, 10, 14, 10)
        fl.setSpacing(2)

        name = _qlabel(person["name"], size=13, color="#cdd6f4", bold=True)
        name.setStyleSheet(name.styleSheet() + " background: transparent; border: none;")
        fl.addWidget(name)

        role = _qlabel(person["role"], size=11, color="#a6adc8")
        role.setStyleSheet(role.styleSheet() + " background: transparent; border: none;")
        fl.addWidget(role)

        if person.get("projects"):
            proj = _qlabel("Projects: " + ", ".join(person["projects"]), size=11, color="#8b5897")
            proj.setStyleSheet(proj.styleSheet() + " background: transparent; border: none;")
            fl.addWidget(proj)

        cl.addWidget(frame)

    cl.addStretch()
    return widget


def build_links_page(on_back):
    widget, cl = _scroll_page(on_back, "Links")
    
    for link in LINKS:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background-color: #2d1f3d; border: 1px solid #8b5897; border-radius: 5px; }"
        )
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(14, 10, 14, 10)
        fl.setSpacing(6)

        name = _qlabel(link["label"], size=13, color="#cdd6f4", bold=True)
        name.setStyleSheet(name.styleSheet() + " background: transparent; border: none;")
        fl.addWidget(name)

        btn = QPushButton("Open Link")
        btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; "
            "border: none; border-radius: 4px; padding: 5px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: #b4befe; }"
        )
        btn.clicked.connect(lambda _, u=link["url"]: QDesktopServices.openUrl(QUrl(u)))
        fl.addWidget(btn)

        cl.addWidget(frame)

    cl.addStretch()
    return widget


# Nav button

class NavButton(QPushButton):
    def __init__(self, label, align_right=False):
        super().__init__(label)
        self.setFixedHeight(38)
        align = "right" if align_right else "left"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #2d1f3d;
                border: 1px solid #8b5897;
                border-radius: 5px;
                color: #cdd6f4;
                font-size: 12px;
                font-weight: bold;
                padding: 0 14px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #3d2a52;
                border-color: #cba6f7;
                color: #cba6f7;
            }}
            QPushButton:pressed {{
                background-color: #211a2c;
            }}
        """)


# Main Window

class UniOSWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniDesk")
        self.setMinimumSize(580, 500)
        self.setStyleSheet("background-color: #1a1226;")

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._page_indices = {}

        self._build_main()
        self._build_subpages()

    def _build_main(self):
        main_page = QWidget()
        main_page.setStyleSheet("background: transparent;")
        mp = QVBoxLayout(main_page)
        mp.setContentsMargins(0, 0, 0, 0)
        mp.setSpacing(0)

        # Hero
        hero = QWidget()
        hero.setStyleSheet("background: #211a2c;")
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(20, 20, 20, 16)
        hl.setSpacing(4)

        hero_title = _qlabel("Welcome to UniOS", size=26, color="#cba6f7", bold=True)
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_title)

        hero_sub = _qlabel(
            "A custom Linux distribution for the modern Greek university",
            size=12, color="#a6adc8"
        )
        hero_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_sub)

        mp.addWidget(hero)
        mp.addWidget(_divider())

        # Nav columns
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(28, 24, 28, 24)
        nav_layout.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        for key in NAV_LEFT:
            btn = NavButton(key, align_right=False)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            left_col.addWidget(btn)
        left_col.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        for key in NAV_RIGHT:
            btn = NavButton(key, align_right=True)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            right_col.addWidget(btn)
        right_col.addStretch()

        nav_layout.addLayout(left_col)
        nav_layout.addLayout(right_col)
        mp.addWidget(nav_widget, stretch=1)

        mp.addWidget(_divider())
        mp.addWidget(_footer())

        self._stack.addWidget(main_page)  # index 0

    def _build_subpages(self):
        subpages = {
            **{key: build_text_page(key, self._show_main) for key in PAGES},
            "Credits": build_credits_page(self._show_main),
            "Links":   build_links_page(self._show_main),
        }
        for key, widget in subpages.items():
            self._page_indices[key] = self._stack.addWidget(widget)

    def _show_page(self, key):
        self._stack.setCurrentIndex(self._page_indices[key])

    def _show_main(self):
        self._stack.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")
    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
