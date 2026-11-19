"""@file text_data.py
@brief Loads UniDesk's user-facing text from the bundled JSON files.

Translatable strings are stored inline as {"en": "...", "el": "..."}. They are
collapsed to a plain string for the active language when a file is loaded, so
callers never see the language dicts. A missing translation falls back to English.
"""

import json
import os
from functools import cache
from importlib.resources import files

from . import settings

_TEXT_DATA_PACKAGE = "unidesk.assets.text_data"

DEFAULT_LANG = "en"
SUPPORTED = ("en", "el")

# Each language written in itself. Never translated: the language button shows
# the name of the language it will switch to.
LANGUAGE_NAMES = {"en": "English", "el": "Ελληνικά"}

_current_lang = None


def detect_language():
    """@brief Picks the UI language from the environment.

    UNIDESK_LANG wins, then the language saved by the language button, then
    LANGUAGE, LC_ALL, LC_MESSAGES and LANG in that order.
    @return A code from SUPPORTED, or DEFAULT_LANG when nothing matches.
    """
    override = os.environ.get("UNIDESK_LANG")
    if override:
        return override if override in SUPPORTED else DEFAULT_LANG

    saved = settings.load_language()
    if saved in SUPPORTED:
        return saved

    candidates = []
    if os.environ.get("LANGUAGE"):
        candidates += os.environ["LANGUAGE"].split(":")  # e.g. "el:en"
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(var):
            candidates.append(os.environ[var])
            break

    for value in candidates:
        code = value.split(".")[0].split("_")[0].lower()
        if code in SUPPORTED:
            return code
    return DEFAULT_LANG


def get_language():
    """@brief Returns the active UI language, detecting it on first use.
    @return A code from SUPPORTED.
    """
    global _current_lang
    if _current_lang is None:
        _current_lang = detect_language()
    return _current_lang


def set_language(lang):
    """@brief Sets the active UI language. Unknown codes fall back to English.

    Pages that were already built keep their old text; this only affects later loads.
    @param lang A code from SUPPORTED.
    """
    global _current_lang
    _current_lang = lang if lang in SUPPORTED else DEFAULT_LANG


def next_language(lang):
    """@brief Returns the language after lang in SUPPORTED, wrapping around.
    @param lang A code from SUPPORTED.
    @return The next code, which is what the language button switches to.
    """
    index = SUPPORTED.index(lang) if lang in SUPPORTED else 0
    return SUPPORTED[(index + 1) % len(SUPPORTED)]


def is_translation(node):
    """@brief Tells whether a JSON node is an inline {"en": ..., "el": ...} entry.
    @param node Any parsed JSON value.
    @return True if it is a non-empty dict whose keys are all language codes.
    """
    return isinstance(node, dict) and bool(node) and all(k in SUPPORTED for k in node)


def _resolve(node, lang):
    """@brief Replaces every inline translation entry in node with a plain string."""
    if is_translation(node):
        return node.get(lang) or node.get(DEFAULT_LANG, "")
    if isinstance(node, dict):
        return {k: _resolve(v, lang) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve(v, lang) for v in node]
    return node


@cache
def load_raw(name):
    """@brief Reads one bundled JSON file without resolving translations.
    @param name File name inside assets/text_data, without the .json extension.
    @return The parsed JSON data, with the {"en": ..., "el": ...} entries intact.
    """
    path = files(_TEXT_DATA_PACKAGE).joinpath(f"{name}.json")
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def _load(name, lang):
    return _resolve(load_raw(name), lang)


def load(name, lang=None):
    """@brief Reads one of the bundled JSON text files in the active language.
    @param name File name inside assets/text_data, without the .json extension.
    @param lang Language code. Defaults to the active language.
    @return The parsed JSON data with every translation resolved to a string.
    """
    return _load(name, lang or get_language())


def page_title(key, lang=None):
    """@brief Returns the display title of a page.
    @param key Stable page id, for example "Introduction" or "Credits".
    @param lang Language code. Defaults to the active language.
    @return The translated title, or the key itself if navigation.json has none.
    """
    return load("navigation", lang).get("titles", {}).get(key, key)


def faq_body(lang=None):
    """@brief Flattens the FAQ entries from faq.json into one block of text.
    @param lang Language code. Defaults to the active language.
    @return The FAQ as question/answer pairs separated by blank lines.
    """
    ui = load("ui_strings", lang)
    q, a = ui["faq_question_prefix"], ui["faq_answer_prefix"]
    entries = load("faq", lang)["entries"]
    return "\n\n".join(f"{q}{e['question']}\n{a}{e['answer']}" for e in entries)


def pages(lang=None):
    """@brief Builds the text pages defined in pages.json.

    Entries with a "body_from" key get the FAQ text as their body.
    @param lang Language code. Defaults to the active language.
    @return A dict of page id to {"body": text}, in display order.
    """
    resolved = {}
    for key, page in load("pages", lang).items():
        if "body_from" in page:
            resolved[key] = {"body": faq_body(lang)}
        else:
            resolved[key] = {"body": page["body"]}
    return resolved
