"""Shared fixtures: keep every test away from the real $HOME."""

import os

import pytest

# Must be set before any QApplication exists (pytest-qt creates it lazily).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Pin the UI language so the suite doesn't depend on the machine's locale.
# Must be set before unidesk is imported. Translation tests pass lang= explicitly.
os.environ["UNIDESK_LANG"] = "en"


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Point HOME and both helper paths into a temp dir.

    The helpers compute their paths at import time, so patching HOME alone
    is not enough; the module constants are patched too.
    """
    from unidesk.helpers import academic_config, autostart

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    config_dir = home / ".unios"
    monkeypatch.setattr(academic_config, "CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(
        academic_config, "CONFIG_PATH", str(config_dir / "academicConfig.json")
    )
    monkeypatch.setattr(
        autostart,
        "AUTOSTART_PATH",
        str(home / ".config" / "autostart" / "unidesk.desktop"),
    )
    return home


@pytest.fixture(autouse=True)
def reset_language():
    """The language button changes a process-wide setting, so reset it around every test."""
    from unidesk.helpers import text_data

    text_data.set_language("en")
    yield
    text_data.set_language("en")
