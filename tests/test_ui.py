"""Smoke tests for the Qt UI (run offscreen)."""

import json

import pytest
from PyQt6.QtWidgets import QComboBox, QPushButton

from unidesk.helpers import academic_config, autostart, settings, text_data

UI = text_data.load("ui_strings")
UNIS = text_data.load("academic_institutions")["universities"]


@pytest.fixture
def window(qtbot):
    from unidesk.ui.main_window import UniOSWelcome

    w = UniOSWelcome()
    qtbot.addWidget(w)
    return w


def test_window_builds(window):
    assert window.windowTitle() == UI["window_title"]
    assert window._stack.currentIndex() == 0


def test_every_nav_button_opens_its_page(window):
    nav = text_data.load("navigation")
    for key in nav["nav_left"] + nav["nav_right"]:
        window._show_page(key)
        assert window._stack.currentIndex() == window._page_indices[key]
        window._show_main()
        assert window._stack.currentIndex() == 0


def test_autostart_checkbox_writes_override(window):
    window._autostart_cb.setChecked(False)
    assert autostart.is_autostart_disabled()
    window._autostart_cb.setChecked(True)
    assert not autostart.is_autostart_disabled()


@pytest.mark.xfail(strict=True, reason="checkbox is always initialised to checked")
def test_autostart_checkbox_reflects_saved_state(qtbot):
    autostart.set_autostart(False)
    from unidesk.ui.main_window import UniOSWelcome

    w = UniOSWelcome()
    qtbot.addWidget(w)
    assert not w._autostart_cb.isChecked()


@pytest.fixture
def config_page(qtbot):
    """Return a factory; the page is kept alive until the test ends."""
    from unidesk.ui.pages.academic_config_page import build_academic_config_page

    pages = []

    def build():
        page = build_academic_config_page(lambda: None)
        qtbot.addWidget(page)
        pages.append(page)
        uni, dept = page.findChildren(QComboBox)
        save = next(b for b in page.findChildren(QPushButton)
                    if b.text() == UI["academic_save_button"])
        return uni, dept, save

    return build


def test_config_page_saves_selection(config_page):
    uni, dept, save = config_page()
    name = next(iter(UNIS))
    uni.setCurrentText(name)
    assert [dept.itemText(i) for i in range(dept.count())] == UNIS[name]
    dept.setCurrentText(UNIS[name][0])
    save.click()
    with open(academic_config.CONFIG_PATH, encoding="utf-8") as f:
        assert json.load(f) == {"universityName": name, "departmentName": UNIS[name][0]}


def test_config_page_refuses_incomplete(config_page):
    _, _, save = config_page()
    save.click()
    assert academic_config.load_academic_config()["universityName"] == ""


def test_config_page_prefills_saved_values(config_page):
    name = next(iter(UNIS))
    academic_config.save_academic_config(name, UNIS[name][-1])
    uni, dept, _ = config_page()
    assert uni.currentText() == name
    assert dept.currentText() == UNIS[name][-1]


def test_config_page_ignores_unknown_saved_university(config_page):
    academic_config.save_academic_config("Unknown University", "X")
    uni, dept, _ = config_page()
    assert uni.currentIndex() == -1
    assert dept.count() == 0


def test_nav_buttons_show_translated_titles(window):
    nav = text_data.load("navigation")
    labels = {b.text() for b in window.findChildren(QPushButton)}
    for key in nav["nav_left"] + nav["nav_right"]:
        assert text_data.page_title(key) in labels


@pytest.mark.parametrize("lang", text_data.SUPPORTED)
def test_window_builds_in_every_language(qtbot, lang):
    from unidesk.ui.main_window import UniOSWelcome

    text_data.set_language(lang)
    w = UniOSWelcome()
    qtbot.addWidget(w)
    assert w.windowTitle() == text_data.load("ui_strings", lang)["window_title"]


def test_language_button_shows_the_other_language(window):
    assert window._language_btn.text() == text_data.LANGUAGE_NAMES["el"]


def test_language_button_switches_and_saves(window):
    window._language_btn.click()
    assert text_data.get_language() == "el"
    assert settings.load_language() == "el"
    assert window._language_btn.text() == text_data.LANGUAGE_NAMES["en"]

    window._language_btn.click()
    assert text_data.get_language() == "en"
    assert settings.load_language() == "en"
    assert window._language_btn.text() == text_data.LANGUAGE_NAMES["el"]


def test_language_switch_rebuilds_pages_in_the_new_language(window):
    pages_before = window._stack.count()
    window._language_btn.click()
    assert window._stack.count() == pages_before

    labels = {b.text() for b in window.findChildren(QPushButton)}
    nav = text_data.load("navigation", "el")
    for key in nav["nav_left"] + nav["nav_right"]:
        assert text_data.page_title(key, "el") in labels
        window._show_page(key)
        assert window._stack.currentIndex() == window._page_indices[key]


def test_language_switch_returns_to_main_page(window):
    window._show_page("FAQ")
    window._language_btn.click()
    assert window._stack.currentIndex() == 0


def test_language_switch_keeps_autostart_state(window):
    window._autostart_cb.setChecked(False)
    assert autostart.is_autostart_disabled()
    window._language_btn.click()
    assert not window._autostart_cb.isChecked()
    assert autostart.is_autostart_disabled()


def test_greek_labels_are_shown_after_switching(window):
    window._language_btn.click()
    labels = {b.text() for b in window.findChildren(QPushButton)}
    assert text_data.load("ui_strings", "el")["configure_button"] in labels
    assert text_data.page_title("Introduction", "el") in labels
    assert text_data.page_title("Introduction", "el") != "Introduction"
