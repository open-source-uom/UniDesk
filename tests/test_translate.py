"""Tests for the saved UniDesk preferences (HOME is redirected by conftest)."""

import json
import os

from unidesk.helpers import translate


def test_no_saved_language_by_default():
    assert translate.load_language() is None


def test_language_round_trip():
    translate.save_language("el")
    assert translate.load_language() == "el"


def test_corrupt_file_is_ignored():
    path = translate._settings_path()
    os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not json")
    assert translate.load_language() is None


def test_non_dict_json_is_ignored():
    path = translate._settings_path()
    os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(["el"], f)
    assert translate.load_language() is None


def test_save_keeps_other_keys():
    path = translate._settings_path()
    os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"other": 1}, f)
    translate.save_language("el")
    with open(path, encoding="utf-8") as f:
        assert json.load(f) == {"other": 1, "language": "el"}


def test_unwritable_location_does_not_raise(isolated_home):
    # A regular file where the ~/.config directory should be makes makedirs fail.
    (isolated_home / ".config").write_text("not a directory")
    translate.save_language("el")  # must not raise
    assert translate.load_language() is None


def test_does_not_touch_the_shared_academic_profile(isolated_home):
    translate.save_language("el")
    assert not (isolated_home / ".unios").exists()
