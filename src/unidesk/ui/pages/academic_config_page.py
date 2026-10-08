from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QPushButton

from ...helpers.academic_config import load_academic_config, save_academic_config
from ...helpers.text_data import load
from ...styles.loader import load_qss
from ..widgets import qlabel, scroll_page

UI = load("ui_strings")
UNIVERSITIES = load("academic_institutions")["universities"]


def build_academic_config_page(on_back):
    widget, cl = scroll_page(on_back, UI["academic_config_page_title"])

    intro = qlabel(UI["academic_config_intro"], role="body", wrap=True)
    cl.addWidget(intro)

    cl.addWidget(qlabel(UI["academic_university_label"], role="field-label"))
    university_combo = QComboBox()
    university_combo.setProperty("control", "academic")
    university_combo.setStyleSheet(load_qss("widgets/controls.qss"))
    university_combo.setPlaceholderText(UI["academic_university_placeholder"])
    university_combo.addItems(list(UNIVERSITIES.keys()))
    university_combo.setCurrentIndex(-1)
    cl.addWidget(university_combo)

    cl.addWidget(qlabel(UI["academic_department_label"], role="field-label"))
    department_combo = QComboBox()
    department_combo.setProperty("control", "academic")
    department_combo.setStyleSheet(load_qss("widgets/controls.qss"))
    department_combo.setPlaceholderText(UI["academic_department_placeholder"])
    department_combo.setCurrentIndex(-1)
    cl.addWidget(department_combo)

    status = qlabel("", role="muted", wrap=True)

    def set_status_error(error):
        status.setProperty("state", "error" if error else "")
        # Qt won't re-evaluate property selectors on a shown widget unless repolished.
        status.style().unpolish(status)
        status.style().polish(status)

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
    save_btn.setProperty("button", "save")
    save_btn.setStyleSheet(load_qss("widgets/controls.qss"))

    def on_save():
        university = university_combo.currentText()
        department = department_combo.currentText()
        if not university or not department:
            status.setText(UI["academic_error_incomplete"])
            set_status_error(True)
            return
        save_academic_config(university, department)
        status.setText(
            UI["academic_saved_template"].format(
                university=university, department=department
            )
        )
        set_status_error(False)

    save_btn.clicked.connect(lambda _: on_save())

    cl.addSpacing(6)
    cl.addWidget(save_btn)
    cl.addWidget(status)
    cl.addStretch()
    return widget
