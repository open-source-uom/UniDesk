"""Validate the bundled JSON so a bad edit fails CI instead of crashing at startup."""

import re
from importlib.resources import files
from pathlib import Path

import pytest

from unidesk.helpers import text_data, translate

JSON_NAMES = sorted(
    p.name.removesuffix(".json")
    for p in files("unidesk.assets.text_data").iterdir()
    if p.name.endswith(".json")
)
SRC = Path(text_data.__file__).resolve().parents[1]


@pytest.mark.parametrize("name", JSON_NAMES)
def test_json_parses(name):
    assert text_data.load(name)


def test_every_nav_entry_has_a_page():
    nav = text_data.load("navigation")
    known = set(text_data.pages()) | {"Credits", "Links"}
    missing = [k for k in nav["nav_left"] + nav["nav_right"] if k not in known]
    assert not missing, f"nav entries without a page: {missing}"


def test_pages_resolve_to_non_empty_bodies():
    for key, page in text_data.pages().items():
        assert page["body"].strip(), key


def test_faq_body_format():
    entries = text_data.load("faq")["entries"]
    body = text_data.faq_body()
    ui = text_data.load("ui_strings")
    assert body.count(ui["faq_question_prefix"]) == len(entries)
    assert body.count(ui["faq_answer_prefix"]) == len(entries)


def test_ui_string_keys_used_in_code_exist():
    ui = text_data.load("ui_strings")
    used = set()
    for py in SRC.rglob("*.py"):
        used |= set(re.findall(r'UI\["([^"]+)"\]', py.read_text(encoding="utf-8")))
    missing = sorted(used - set(ui))
    assert not missing, f"ui_strings.json is missing: {missing}"


def test_saved_template_placeholders():
    tpl = text_data.load("ui_strings")["academic_saved_template"]
    assert tpl.format(university="U", department="D")


def _urls():
    nav = text_data.load("navigation")["footer_links"]
    links = text_data.load("links")["links"]
    return [(e["label"], e["url"]) for e in nav + links]


@pytest.mark.parametrize("label, url", _urls())
def test_links_are_https(label, url):
    assert label.strip()
    assert url.startswith("https://"), url


def test_credits_shape():
    for person in text_data.load("credits")["people"]:
        assert person["name"].strip()
        assert person["role"].strip()
        assert isinstance(person.get("projects", []), list)


def test_academic_institutions_shape():
    unis = text_data.load("academic_institutions")["universities"]
    assert unis
    for uni, departments in unis.items():
        assert uni.strip()
        assert departments, f"{uni} has no departments"
        assert len(departments) == len(set(departments)), f"duplicate dept in {uni}"


# --- translations -----------------------------------------------------------

LANGS = text_data.SUPPORTED


def _walk(node, path=""):
    """Yield (path, node) for every dict and list in a raw JSON tree."""
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


@pytest.mark.parametrize("name", JSON_NAMES)
def test_translation_entries_are_complete(name):
    """Every {"en": ...} entry must carry every supported language."""
    for path, node in _walk(text_data.load_raw(name)):
        if isinstance(node, dict) and "en" in node:
            assert set(node) == set(LANGS), f"{name}{path}: has {sorted(node)}"
            for lang, value in node.items():
                assert isinstance(value, str) and value.strip(), f"{name}{path}[{lang}]"


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("name", JSON_NAMES)
def test_resolved_data_has_no_language_dicts(name, lang):
    for path, node in _walk(text_data.load(name, lang)):
        assert not text_data.is_translation(node), f"{name}{path} was not resolved"


@pytest.mark.parametrize("lang", LANGS)
def test_every_nav_entry_has_a_title(lang):
    nav = text_data.load("navigation", lang)
    for key in nav["nav_left"] + nav["nav_right"]:
        assert text_data.page_title(key, lang).strip(), key


@pytest.mark.parametrize("lang", LANGS)
def test_pages_and_faq_resolve_in_every_language(lang):
    for key, page in text_data.pages(lang).items():
        assert page["body"].strip(), (lang, key)
    entries = text_data.load("faq", lang)["entries"]
    assert text_data.faq_body(lang).count("\n\n") == len(entries) - 1


@pytest.mark.parametrize("lang", LANGS)
def test_saved_template_placeholders_in_every_language(lang):
    tpl = text_data.load("ui_strings", lang)["academic_saved_template"]
    assert tpl.format(university="U", department="D")


def test_greek_actually_differs_from_english():
    en = text_data.load("ui_strings", "en")
    el = text_data.load("ui_strings", "el")
    assert el["hero_title"] != en["hero_title"]
    assert text_data.pages("el")["Introduction"] != text_data.pages("en")["Introduction"]


def test_missing_translation_falls_back_to_english():
    assert text_data._resolve({"en": "Hello"}, "el") == "Hello"
    assert text_data._resolve({"en": "Hello", "el": ""}, "el") == "Hello"


def test_plain_two_letter_keys_are_not_mistaken_for_translations():
    assert text_data._resolve({"en": "x", "id": "y"}, "el") == {"en": "x", "id": "y"}


def test_academic_institutions_are_not_translated():
    """Saved values must stay stable and in sync with UniBackpack."""
    raw = text_data.load_raw("academic_institutions")
    for path, node in _walk(raw):
        assert not text_data.is_translation(node), path


@pytest.mark.parametrize(
    "env, expected",
    [
        ({"UNIDESK_LANG": "el"}, "el"),
        ({"UNIDESK_LANG": "xx"}, "en"),
        ({"LANG": "el_GR.UTF-8"}, "el"),
        ({"LANG": "en_US.UTF-8"}, "en"),
        ({"LANG": "C.UTF-8"}, "en"),
        ({"LANG": "de_DE.UTF-8"}, "en"),
        ({"LANGUAGE": "el:en", "LANG": "en_US.UTF-8"}, "el"),
        ({"LC_ALL": "el_GR.UTF-8", "LANG": "en_US.UTF-8"}, "el"),
        ({}, "en"),
    ],
)
def test_detect_language(monkeypatch, env, expected):
    for var in ("UNIDESK_LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    assert text_data.detect_language() == expected


def _clear_language_env(monkeypatch):
    for var in ("UNIDESK_LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)


def test_saved_language_beats_system_language(monkeypatch):
    _clear_language_env(monkeypatch)
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    translate.save_language("el")
    assert text_data.detect_language() == "el"


def test_env_override_beats_saved_language(monkeypatch):
    _clear_language_env(monkeypatch)
    translate.save_language("el")
    monkeypatch.setenv("UNIDESK_LANG", "en")
    assert text_data.detect_language() == "en"


def test_unsupported_saved_language_is_ignored(monkeypatch):
    _clear_language_env(monkeypatch)
    monkeypatch.setenv("LANG", "el_GR.UTF-8")
    translate.save_language("xx")
    assert text_data.detect_language() == "el"


def test_next_language_cycles():
    assert text_data.next_language("en") == "el"
    assert text_data.next_language("el") == "en"
    assert text_data.next_language("xx") in text_data.SUPPORTED


def test_every_supported_language_has_a_button_name():
    for lang in text_data.SUPPORTED:
        assert text_data.LANGUAGE_NAMES[lang].strip(), lang
