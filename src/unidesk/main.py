import os
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from .home import UniOSWelcome


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.abspath(
        os.path.join(current_dir, "..", "..", "resources", "unios.png")
    )
    app.setWindowIcon(QIcon(icon_path))

    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
