from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..helpers.autostart import set_autostart
from ..helpers.text_data import load, pages
from ..styles.loader import load_qss
from .pages.academic_config_page import build_academic_config_page
from .pages.credits_page import build_credits_page
from .pages.links_page import build_links_page
from .pages.text_page import build_text_page
from .widgets import NavButton, divider, footer, qlabel

PAGES = pages()
UI = load("ui_strings")
_NAV = load("navigation")


NAV_LEFT = _NAV["nav_left"]
NAV_RIGHT = _NAV["nav_right"]


# Main Window


class UniOSWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(UI["window_title"])
        self.setMinimumSize(580, 500)
        self.setProperty("layout", "window")
        self.setStyleSheet(load_qss("widgets/layout.qss"))

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._page_indices = {}

        self._build_main()
        self._build_subpages()

    def _build_main(self):
        main_page = QWidget()
        main_page.setProperty("layout", "transparent")
        main_page.setStyleSheet(load_qss("widgets/layout.qss"))
        mp = QVBoxLayout(main_page)
        mp.setContentsMargins(0, 0, 0, 0)
        mp.setSpacing(0)

        # Hero
        hero = QWidget()
        hero.setProperty("layout", "hero")
        hero.setStyleSheet(load_qss("widgets/layout.qss"))
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(20, 20, 20, 16)
        hl.setSpacing(4)

        hero_title = qlabel(UI["hero_title"], role="title")
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_title)

        hero_sub = qlabel(UI["hero_subtitle"], role="body")
        hero_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_sub)

        mp.addWidget(hero)
        mp.addWidget(divider())

        # Nav columns
        nav_widget = QWidget()
        nav_widget.setProperty("layout", "transparent")
        nav_widget.setStyleSheet(load_qss("widgets/layout.qss"))
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(28, 24, 28, 24)
        nav_layout.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        for key in NAV_LEFT:
            btn = NavButton(key)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            left_col.addWidget(btn)
        left_col.addStretch()

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(28, 0, 28, 14)
        self._autostart_cb = QCheckBox(UI["autostart_checkbox"])
        self._autostart_cb.setChecked(True)
        self._autostart_cb.setProperty("control", "autostart")
        self._autostart_cb.setStyleSheet(load_qss("widgets/controls.qss"))

        self._autostart_cb.stateChanged.connect(self._toggle_autostart)
        cfg_btn = QPushButton(UI["configure_button"])
        cfg_btn.setFixedHeight(28)
        cfg_btn.setProperty("button", "configure")
        cfg_btn.setStyleSheet(load_qss("widgets/controls.qss"))
        cfg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_btn.clicked.connect(self._show_academic_config)

        bottom_row.addWidget(self._autostart_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(cfg_btn)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        for key in NAV_RIGHT:
            btn = NavButton(key)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            right_col.addWidget(btn)
        right_col.addStretch()

        nav_layout.addLayout(left_col)
        nav_layout.addLayout(right_col)
        mp.addWidget(nav_widget, stretch=1)
        mp.addLayout(bottom_row)

        mp.addWidget(divider())
        mp.addWidget(footer())
        self._stack.addWidget(main_page)  # index 0

    def _build_subpages(self):
        subpages = {
            **{key: build_text_page(key, self._show_main) for key in PAGES},
            UI["credits_page_title"]: build_credits_page(self._show_main),
            UI["links_page_title"]: build_links_page(self._show_main),
            UI["academic_config_page_title"]: build_academic_config_page(
                self._show_main
            ),
        }
        for key, widget in subpages.items():
            self._page_indices[key] = self._stack.addWidget(widget)

    def _toggle_autostart(self, state):
        set_autostart(self._autostart_cb.isChecked())

    def _show_page(self, key):
        self._stack.setCurrentIndex(self._page_indices[key])

    def _show_main(self):
        self._stack.setCurrentIndex(0)

    def _show_academic_config(self):
        self._stack.setCurrentIndex(self._page_indices[UI["academic_config_page_title"]])
