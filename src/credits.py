# Author: Emanuela Goxha 2026 <ics23184@uom.edu.gr>
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QFont


CREDITS =[
    {
        "name": "Apostolos Chalis",
        "role": "Main Deveoper",
        "projects":["UniOS","UniBackpack","Unidesk"],
    },
    {
        "name": "Emanuela Goxha",
        "role": "Developer & Designer",
        "projects":["UniMate","Unidesk"],
    },
    {
        "name": "Malamatenia Soulioti",
        "role": "Main Designer",
    },
    {
        "name":"Ioannis Michadasis",
        "role":"Developer",
        "projects":["UniOS","UniBackpack"],
    },
    {
        "name":"Alexandra Iordanidou",
        "role":"Community moderator",
        "projects":["UniDesk"],
    },
    {
        "name":"Konstantina Deligianni",
        "role":"Developer",
        "projects":["UniOS"],
    },
    ]

class CreditsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        for person in CREDITS:
            layout.addWidget(self._credit_card(person))

        layout.addStretch()

    def _credit_card(self, person):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        name = QLabel(f"<b>{person['name']}</b>")
        name.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(name)
        
        role = QLabel(person["role"])
        role.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(role)

        if person.get("projects"):
            projects_str = ", ".join(person["projects"])
            projects = QLabel(f"Projects: {projects_str}")
            projects.setStyleSheet("background-color: transparent; border: none;")
            layout.addWidget(projects)

        return frame