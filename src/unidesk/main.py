from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

import sys
import os

from unidesk.home import UniOSWelcome

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, src_dir)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")

    icon_path = os.path.abspath(os.path.join(src_dir, "..", "resources", "unios.png"))
    app.setWindowIcon(QIcon(icon_path))

    window = UniOSWelcome()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
