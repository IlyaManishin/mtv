from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget

from src.common.constants import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, MAX_FONT_SIZE, MIN_FONT_SIZE
from src.common.localization import Language, get_text
from src.compiler.models import ErrorRecord
from src.gui.widgets.error_table import ErrorTable


class OutputPanel(QWidget):
    error_selected = pyqtSignal(int, int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_lang: Language = Language.RU
        self._font_size: int = DEFAULT_FONT_SIZE

        self._tabs: QTabWidget = QTabWidget(self)
        self._log_edit: QPlainTextEdit = QPlainTextEdit(self)
        self._error_table: ErrorTable = ErrorTable(self)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabs)

        self._log_edit.setReadOnly(True)
        font = QFont(DEFAULT_FONT_FAMILY, self._font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._log_edit.setFont(font)

        self._tabs.addTab(self._log_edit, get_text("tab_output", self._current_lang))
        self._tabs.addTab(self._error_table, get_text("tab_errors", self._current_lang))

        self._error_table.error_selected.connect(self.error_selected.emit)

    def update_language(self, lang: Language) -> None:
        self._current_lang = lang
        self._tabs.setTabText(0, get_text("tab_output", lang))
        self._tabs.setTabText(1, get_text("tab_errors", lang))
        self._error_table.update_headers(lang)

    def set_log_messages(self, messages: list[str]) -> None:
        self._log_edit.setPlainText("\n".join(messages))

    def append_log(self, text: str) -> None:
        self._log_edit.appendPlainText(text)

    def set_errors(self, errors: list[ErrorRecord]) -> None:
        self._error_table.set_errors(errors)
        if errors:
            self._tabs.setCurrentIndex(1)
        else:
            self._tabs.setCurrentIndex(0)

    def clear(self) -> None:
        self._log_edit.clear()
        self._error_table.clear_errors()

    def zoom_in(self, delta: int = 1) -> None:
        if self._font_size + delta <= MAX_FONT_SIZE:
            self._font_size += delta
            self._apply_font_size()

    def zoom_out(self, delta: int = 1) -> None:
        if self._font_size - delta >= MIN_FONT_SIZE:
            self._font_size -= delta
            self._apply_font_size()

    def reset_zoom(self) -> None:
        self._font_size = DEFAULT_FONT_SIZE
        self._apply_font_size()

    def _apply_font_size(self) -> None:
        font = self._log_edit.font()
        font.setPointSize(self._font_size)
        self._log_edit.setFont(font)
