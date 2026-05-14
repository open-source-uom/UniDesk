import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from unidesk.home import UniOSWelcome


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")
    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
