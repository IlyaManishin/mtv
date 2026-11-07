from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from src.common.constants import APP_NAME, APP_VERSION
from src.common.localization import Language, get_text


class AboutDialog(QDialog):
    def __init__(self, lang: Language, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(get_text("about_title", lang))
        self.resize(480, 280)
        self._init_ui(lang)

    def _init_ui(self, lang: Language) -> None:
        layout = QVBoxLayout(self)

        title_label = QLabel(f"<h2>{APP_NAME}</h2>", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel(f"<b>Версия:</b> {APP_VERSION}", self)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        if lang == Language.RU:
            desc = (
                "<p align='center'><b>Текстовый редактор для языкового процессора</b></p>"
                "<p align='justify'>Лабораторная работа по разработке пользовательского интерфейса (GUI) "
                "языкового процессора.<br>"
                "Язык реализации: Python / PyQt6.<br>"
                "Грамматика: Условный оператор Python (if-else, вариант 5).</p>"
            )
        else:
            desc = (
                "<p align='center'><b>Text Editor for Language Processor</b></p>"
                "<p align='justify'>Laboratory project: Graphical User Interface for language processor.<br>"
                "Implementation: Python / PyQt6.<br>"
                "Grammar: Python Conditional Statement (if-else, variant 5).</p>"
            )

        desc_label = QLabel(desc, self)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
