import os
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from .home import UniOSWelcome


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")

    icon_path = os.path.abspath(
        os.path.join(src_dir, "..", "resources", "unios.png")
    )
    app.setWindowIcon(QIcon(icon_path))

    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
