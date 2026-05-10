# Author: Emanuela Goxha 2026 <ics23184@uom.edu.gr>
from PyQt6.QtWidgets import QMainWindow, QTabWidget

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