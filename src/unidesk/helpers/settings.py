"""@file settings.py
@brief UniDesk's own preferences, kept apart from the shared UniOS academic profile."""

import json
import os


def _settings_path():
    """@brief Location of the settings file, resolved on every call so tests can redirect HOME."""
    return os.path.join(os.path.expanduser("~"), ".config", "unidesk", "settings.json")


def _read():
    """@brief Reads the settings file.
    @return The saved settings dict, or {} if the file is missing, corrupt or not a dict.
    """
    try:
        with open(_settings_path(), encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def load_language():
    """@brief Returns the language the user picked with the language button.
    @return The saved language code, or None if nothing valid is saved.
    """
    lang = _read().get("language")
    return lang if isinstance(lang, str) else None


def save_language(lang):
    """@brief Remembers the language for the next start.

    A failure to write (read-only home, for example) is ignored: the language
    still changes for the current session.
    @param lang Language code to save.
    """
    data = _read()
    data["language"] = lang
    path = _settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass
