"""@file main.py
@brief UniDesk entry point."""

import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from .ui.main_window import UniOSWelcome


def main():
    """@brief Creates the Qt application, shows the welcome window and runs it.

    The app icon comes from the installed pixmap, then the repo resources folder,
    then the icon theme.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("unidesk")
    app.setDesktopFileName("unidesk")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    system_icon = "/usr/share/pixmaps/unidesk.png"

    local_icon_1 = os.path.abspath(os.path.join(current_dir, "..", "resources", "unios.png"))
    local_icon_2 = os.path.abspath(os.path.join(current_dir, "..", "..", "resources", "unios.png"))

    if os.path.exists(system_icon):
        app_icon = QIcon(system_icon)
    elif os.path.exists(local_icon_1):
        app_icon = QIcon(local_icon_1)
    elif os.path.exists(local_icon_2):
        app_icon = QIcon(local_icon_2)
    else:
        app_icon = QIcon.fromTheme("unidesk", QIcon.fromTheme("preferences-desktop"))

    app.setWindowIcon(app_icon)

    window = UniOSWelcome()
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
