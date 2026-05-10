# Author: Emanuela Goxha 2026 <ics23184@uom.edu.gr>
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from credits import CreditsTab
from links import LinksTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniDesk")
        self.setMinimumSize(550, 450)

        tabs = QTabWidget()
        tabs.addTab(CreditsTab(), "Credits")
        tabs.addTab(LinksTab(), "Links")

        self.setCentralWidget(tabs)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UniDesk")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()