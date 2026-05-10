# Author: Emanuela Goxha 2026 <ics23184@uom.edu.gr>
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices


LINKS = [
    {"label": "Discord Chanel", 
     "url": "https://discord.gg/FJbv84uT",
     "project":["UniDesk"],
    },
    #{"label": "UniMate",         "url": ""},
    #{"label": "Welcome Site","url": ""},
]

class LinksTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        for link in LINKS:
            layout.addWidget(self._link_card(link))

        layout.addStretch()

    def _link_card(self, link):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        label = QLabel(f"<b>{link['label']}</b>")
        label.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(label)

        if link.get("projects"):
            projects_str = ", ".join(link["projects"])
            layout.addWidget(QLabel(f"Projects: {projects_str}"))

        btn = QPushButton("🔗  Open Link")
        btn.clicked.connect(lambda _, u=link["url"]: QDesktopServices.openUrl(QUrl(u)))
        layout.addWidget(btn)

        return frame