"""@file autostart.py
@brief Turns UniDesk autostart on or off for the current user."""

import os

# Disabling autostart drops a hidden override of the system-wide entry that
# the package installs in /etc/xdg/autostart.
AUTOSTART_PATH = os.path.expanduser("~/.config/autostart/unidesk.desktop")

_DISABLED_ENTRY = (
    "[Desktop Entry]\nType=Application\nName=UniDesk\n"
    "Exec=unidesk\nIcon=unios\nTerminal=false\n"
    "X-KDE-autostart-condition=false\nHidden=true\n"
)


def is_autostart_disabled():
    """@brief Checks whether the user has turned autostart off.
    @return True if a user override hides the system autostart entry.
    """
    if not os.path.exists(AUTOSTART_PATH):
        return False
    with open(AUTOSTART_PATH, encoding="utf-8") as f:
        return "Hidden=true" in f.read()


def set_autostart(enabled):
    """@brief Enables autostart by removing the user override, or disables it by writing one.
    @param enabled True to start UniDesk on login, False to turn that off.
    """
    if enabled:
        if os.path.exists(AUTOSTART_PATH):
            os.remove(AUTOSTART_PATH)
    else:
        os.makedirs(os.path.dirname(AUTOSTART_PATH), exist_ok=True)
        with open(AUTOSTART_PATH, "w", encoding="utf-8") as f:
            f.write(_DISABLED_ENTRY)
