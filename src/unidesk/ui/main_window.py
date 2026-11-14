"""@file main_window.py
@brief UniDesk main window."""

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
from ..helpers.settings import save_language
from ..helpers.text_data import (
    LANGUAGE_NAMES,
    get_language,
    load,
    next_language,
    page_title,
    pages,
    set_language,
)
from ..styles.loader import load_qss
from .pages.academic_config_page import build_academic_config_page
from .pages.credits_page import build_credits_page
from .pages.links_page import build_links_page
from .pages.text_page import build_text_page
from .widgets import NavButton, divider, footer, qlabel

# Stable ids for the subpages that aren't defined in pages.json. Titles are
# translated, so they can't be used as lookup keys.
CREDITS_KEY = "Credits"
LINKS_KEY = "Links"
ACADEMIC_CONFIG_KEY = "academic_config"


# Main Window


class UniOSWelcome(QMainWindow):
    """@brief Main window with a hero, the nav buttons and a stack of subpages.

    Index 0 of the stack is the main page and every subpage is looked up by its id.
    The language button in the top left corner rebuilds everything in the other language.
    """

    def __init__(self):
        """@brief Builds the main page and all subpages."""
        super().__init__()
        self.setMinimumSize(580, 500)
        self.setProperty("layout", "window")
        self.setStyleSheet(load_qss("widgets/layout.qss"))

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._page_indices = {}

        self._build_ui()

    def _build_ui(self):
        """@brief Builds every page in the active language. Also used to rebuild after a switch."""
        self.setWindowTitle(load("ui_strings")["window_title"])
        self._page_indices = {}
        self._build_main()
        self._build_subpages()

    def _build_main(self):
        nav = load("navigation")
        main_page = QWidget()
        main_page.setProperty("layout", "transparent")
        main_page.setStyleSheet(load_qss("widgets/layout.qss"))
        mp = QVBoxLayout(main_page)
        mp.setContentsMargins(0, 0, 0, 0)
        mp.setSpacing(0)

        mp.addWidget(self._build_hero())
        mp.addWidget(divider())

        # Nav columns
        nav_widget = QWidget()
        nav_widget.setProperty("layout", "transparent")
        nav_widget.setStyleSheet(load_qss("widgets/layout.qss"))
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(28, 24, 28, 24)
        nav_layout.setSpacing(20)

        left_col = self._build_nav_column(nav["nav_left"])
        bottom_row, self._autostart_cb = self._build_bottom_row()
        right_col = self._build_nav_column(nav["nav_right"])

        nav_layout.addLayout(left_col)
        nav_layout.addLayout(right_col)
        mp.addWidget(nav_widget, stretch=1)
        mp.addLayout(bottom_row)

        mp.addWidget(divider())
        mp.addWidget(footer())
        self._stack.addWidget(main_page)  # index 0

    def _build_hero(self):
        UI = load("ui_strings")
        hero = QWidget()
        hero.setProperty("layout", "hero")
        hero.setStyleSheet(load_qss("widgets/layout.qss"))
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(12, 10, 12, 16)
        hl.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.addWidget(self._build_language_button())
        top_row.addStretch()
        hl.addLayout(top_row)

        hero_title = qlabel(UI["hero_title"], role="title")
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_title)

        hero_sub = qlabel(UI["hero_subtitle"], role="body")
        hero_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_sub)
        return hero

    def _build_language_button(self):
        """@brief Creates the top left button. It shows the language it will switch to."""
        target = next_language(get_language())
        btn = QPushButton(LANGUAGE_NAMES[target])
        btn.setFixedHeight(28)
        btn.setProperty("button", "configure")
        btn.setStyleSheet(load_qss("widgets/controls.qss"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda _: self._switch_language(target))
        self._language_btn = btn
        return btn

    def _build_nav_column(self, keys):
        col = QVBoxLayout()
        col.setSpacing(10)
        for key in keys:
            btn = NavButton(page_title(key))
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            col.addWidget(btn)
        col.addStretch()
        return col

    def _build_bottom_row(self):
        UI = load("ui_strings")
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(28, 0, 28, 14)
        autostart_cb = QCheckBox(UI["autostart_checkbox"])
        autostart_cb.setChecked(True)
        autostart_cb.setProperty("control", "autostart")
        autostart_cb.setStyleSheet(load_qss("widgets/controls.qss"))

        autostart_cb.stateChanged.connect(self._toggle_autostart)
        cfg_btn = QPushButton(UI["configure_button"])
        cfg_btn.setFixedHeight(28)
        cfg_btn.setProperty("button", "configure")
        cfg_btn.setStyleSheet(load_qss("widgets/controls.qss"))
        cfg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_btn.clicked.connect(self._show_academic_config)

        bottom_row.addWidget(autostart_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(cfg_btn)
        return bottom_row, autostart_cb

    def _build_subpages(self):
        subpages = {
            **{key: build_text_page(key, self._show_main) for key in pages()},
            CREDITS_KEY: build_credits_page(self._show_main),
            LINKS_KEY: build_links_page(self._show_main),
            ACADEMIC_CONFIG_KEY: build_academic_config_page(self._show_main),
        }
        for key, widget in subpages.items():
            self._page_indices[key] = self._stack.addWidget(widget)

    def _switch_language(self, lang):
        """@brief Switches the UI language, remembers it, and rebuilds every page.

        The autostart checkbox keeps its state without writing the autostart file again.
        @param lang Language code to switch to.
        """
        set_language(lang)
        save_language(lang)

        autostart_checked = self._autostart_cb.isChecked()
        while self._stack.count():
            page = self._stack.widget(0)
            self._stack.removeWidget(page)
            page.deleteLater()

        self._build_ui()

        self._autostart_cb.blockSignals(True)
        self._autostart_cb.setChecked(autostart_checked)
        self._autostart_cb.blockSignals(False)
        self._stack.setCurrentIndex(0)

    def _toggle_autostart(self, _state):
        set_autostart(self._autostart_cb.isChecked())

    def _show_page(self, key):
        self._stack.setCurrentIndex(self._page_indices[key])

    def _show_main(self):
        self._stack.setCurrentIndex(0)

    def _show_academic_config(self):
        self._stack.setCurrentIndex(self._page_indices[ACADEMIC_CONFIG_KEY])
