import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from academic_config import load_academic_config, save_academic_config
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from text_data import load, pages

PAGES = pages()
CREDITS = load("credits")["people"]
LINKS = load("links")["links"]
UI = load("ui_strings")
UNIVERSITIES = load("academic_institutions")["universities"]
_NAV = load("navigation")

AUTOSTART_PATH = os.path.expanduser("~/.config/autostart/unidesk.desktop")


def _is_autostart_disabled():
    if not os.path.exists(AUTOSTART_PATH):
        return False
    with open(AUTOSTART_PATH) as f:
        return "Hidden=true" in f.read()


FOOTER_LINKS = _NAV["footer_links"]

NAV_LEFT = _NAV["nav_left"]
NAV_RIGHT = _NAV["nav_right"]


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

    btn = QPushButton(UI["back_button"])
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


def _footer(on_configure=None):
    footer = QWidget()
    footer.setFixedHeight(40)
    footer.setStyleSheet("background: #110d1a;")
    ft = QHBoxLayout(footer)
    ft.setContentsMargins(14, 0, 14, 0)
    ft.addWidget(_qlabel(UI["footer_copyright"], size=11, color="#585b70"))
    ft.addStretch()

    if on_configure is not None:
        cfg = QPushButton(UI["configure_button"])
        cfg.setStyleSheet(
            "background: transparent; border: none; color: #8b5897; font-size: 11px;"
        )
        cfg.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg.clicked.connect(lambda _: on_configure())
        ft.addWidget(cfg)

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
    widget, cl = _scroll_page(on_back, UI["credits_page_title"])

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
        name.setStyleSheet(
            name.styleSheet() + " background: transparent; border: none;"
        )
        fl.addWidget(name)

        role = _qlabel(person["role"], size=11, color="#a6adc8")
        role.setStyleSheet(
            role.styleSheet() + " background: transparent; border: none;"
        )
        fl.addWidget(role)

        if person.get("projects"):
            proj = _qlabel(
                UI["projects_prefix"] + ", ".join(person["projects"]),
                size=11,
                color="#8b5897",
            )
            proj.setStyleSheet(
                proj.styleSheet() + " background: transparent; border: none;"
            )
            fl.addWidget(proj)

        cl.addWidget(frame)

    cl.addStretch()
    return widget


def build_links_page(on_back):
    widget, cl = _scroll_page(on_back, UI["links_page_title"])

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
        name.setStyleSheet(
            name.styleSheet() + " background: transparent; border: none;"
        )
        fl.addWidget(name)

        btn = QPushButton(UI["open_link_button"])
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
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


def build_academic_config_page(on_back):
    widget, cl = _scroll_page(on_back, UI["academic_config_page_title"])

    intro = _qlabel(
        UI["academic_config_intro"],
        size=12,
        color="#a6adc8",
        wrap=True,
    )
    cl.addWidget(intro)

    combo_style = (
        "QComboBox { background-color: #2d1f3d; color: #cdd6f4; border: 1px solid #8b5897; "
        "border-radius: 4px; padding: 6px 8px; font-size: 12px; }"
        "QComboBox QAbstractItemView { background-color: #2d1f3d; color: #cdd6f4; "
        "selection-background-color: #3d2a52; }"
    )

    cl.addWidget(
        _qlabel(UI["academic_university_label"], size=12, color="#cdd6f4", bold=True)
    )
    university_combo = QComboBox()
    university_combo.setStyleSheet(combo_style)
    university_combo.setPlaceholderText(UI["academic_university_placeholder"])
    university_combo.addItems(list(UNIVERSITIES.keys()))
    university_combo.setCurrentIndex(-1)
    cl.addWidget(university_combo)

    cl.addWidget(
        _qlabel(UI["academic_department_label"], size=12, color="#cdd6f4", bold=True)
    )
    department_combo = QComboBox()
    department_combo.setStyleSheet(combo_style)
    department_combo.setPlaceholderText(UI["academic_department_placeholder"])
    department_combo.setCurrentIndex(-1)
    cl.addWidget(department_combo)

    status = _qlabel("", size=11, color="#a6adc8", wrap=True)

    def refresh_departments():
        university = university_combo.currentText()
        department_combo.clear()
        if university in UNIVERSITIES:
            department_combo.addItems(UNIVERSITIES[university])
        department_combo.setCurrentIndex(-1)

    university_combo.currentIndexChanged.connect(lambda _: refresh_departments())

    # Pre-fill from any existing config, but only if the saved values are still
    # known to us (UniBackpack may have entries we haven't mirrored yet).
    saved = load_academic_config()
    saved_university = saved["universityName"]
    saved_department = saved["departmentName"]
    if saved_university in UNIVERSITIES:
        university_combo.setCurrentText(saved_university)
        if saved_department in UNIVERSITIES[saved_university]:
            department_combo.setCurrentText(saved_department)

    save_btn = QPushButton(UI["academic_save_button"])
    save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    save_btn.setStyleSheet(
        "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; "
        "border: none; border-radius: 4px; padding: 6px 12px; font-size: 12px; }"
        "QPushButton:hover { background-color: #b4befe; }"
    )

    def on_save():
        university = university_combo.currentText()
        department = department_combo.currentText()
        if not university or not department:
            status.setText(UI["academic_error_incomplete"])
            status.setStyleSheet(status.styleSheet().replace("#a6adc8", "#f38ba8"))
            return
        save_academic_config(university, department)
        status.setText(
            UI["academic_saved_template"].format(
                university=university, department=department
            )
        )
        status.setStyleSheet(status.styleSheet().replace("#f38ba8", "#a6adc8"))

    save_btn.clicked.connect(lambda _: on_save())

    cl.addSpacing(6)
    cl.addWidget(save_btn)
    cl.addWidget(status)
    cl.addStretch()
    return widget


# Nav button


class NavButton(QPushButton):
    def __init__(self, label, align_right=False):
        super().__init__(label)
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
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
        self.setWindowTitle(UI["window_title"])
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

        hero_title = _qlabel(UI["hero_title"], size=26, color="#cba6f7", bold=True)
        hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(hero_title)

        hero_sub = _qlabel(
            UI["hero_subtitle"],
            size=12,
            color="#a6adc8",
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

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(28, 0, 28, 14)
        self._autostart_cb = QCheckBox(UI["autostart_checkbox"])
        self._autostart_cb.setChecked(True)
        _svg = b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><polyline points='3,8 6,12 13,4' fill='none' stroke='#cdd6f4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
        _f = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
        _f.write(_svg)
        _f.flush()
        _check_path = _f.name

        self._autostart_cb.setStyleSheet(
            """
            QCheckBox {
                color: #a6adc8;
                font-size: 12px;
                background: transparent;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #585b70;
                border-radius: 4px;
                background: transparent;
            }
            QCheckBox::indicator:hover {
                border-color: #a6adc8;
            }
            QCheckBox::indicator:checked {
                background-color: #8b5897;
                border-color: #cba6f7;
                image: url(%s);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #9b68a7;
            }
        """
            % _check_path
        )

        self._autostart_cb.stateChanged.connect(self._toggle_autostart)
        cfg_btn = QPushButton(UI["configure_button"])
        cfg_btn = QPushButton(UI["configure_button"])
        cfg_btn.setFixedHeight(28)
        cfg_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d1f3d;
                border: 1px solid #8b5897;
                border-radius: 5px;
                color: #cdd6f4;
                font-size: 11px;
                font-weight: bold;
                padding: 0 12px;
            }
        """)
        cfg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_btn.clicked.connect(self._show_academic_config)

        bottom_row.addWidget(self._autostart_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(cfg_btn)

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
        mp.addLayout(bottom_row)

        mp.addWidget(_divider())
        mp.addWidget(_footer())
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
        if self._autostart_cb.isChecked():
            if os.path.exists(AUTOSTART_PATH):
                os.remove(AUTOSTART_PATH)
        else:
            os.makedirs(os.path.dirname(AUTOSTART_PATH), exist_ok=True)
            with open(AUTOSTART_PATH, "w") as f:
                f.write(
                    "[Desktop Entry]\nType=Application\nName=UniDesk\n"
                    "Exec=unidesk\nIcon=unios\nTerminal=false\n"
                    "X-KDE-autostart-condition=false\nHidden=true\n"
                )

    def _show_page(self, key):
        self._stack.setCurrentIndex(self._page_indices[key])

    def _show_main(self):
        self._stack.setCurrentIndex(0)

    def _show_academic_config(self):
        self._stack.setCurrentIndex(self._page_indices[UI["academic_config_page_title"]])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")
    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
