from typing import Optional

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout, QWidget


class InfoDialog(QDialog):
    def __init__(self, title: str, content: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(650, 450)
        self._init_ui(content)

    def _init_ui(self, content: str) -> None:
        layout = QVBoxLayout(self)

        browser = QTextBrowser(self)
        browser.setPlainText(content)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
