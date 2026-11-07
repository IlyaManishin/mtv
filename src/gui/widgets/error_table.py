from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QWidget

from src.common.localization import Language, get_text
from src.compiler.models import ErrorRecord


class ErrorTable(QTableWidget):
    error_selected = pyqtSignal(int, int)  # line (1-based), column (1-based)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(0, 5, parent)
        self._current_lang: Language = Language.RU
        self._init_ui()

    def _init_ui(self) -> None:
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.cellClicked.connect(self._on_cell_activated)
        self.cellDoubleClicked.connect(self._on_cell_activated)
        self.update_headers(self._current_lang)

    def update_headers(self, lang: Language) -> None:
        self._current_lang = lang
        headers = [
            get_text("col_num", lang),
            get_text("col_file", lang),
            get_text("col_line", lang),
            get_text("col_col", lang),
            get_text("col_msg", lang),
        ]
        self.setHorizontalHeaderLabels(headers)

    def set_errors(self, errors: list[ErrorRecord]) -> None:
        self.setRowCount(len(errors))
        for row_idx, err in enumerate(errors):
            item_num = QTableWidgetItem(str(err.index))
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_file = QTableWidgetItem(err.file_path)

            item_line = QTableWidgetItem(str(err.line))
            item_line.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_col = QTableWidgetItem(str(err.column))
            item_col.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_msg = QTableWidgetItem(err.message)

            self.setItem(row_idx, 0, item_num)
            self.setItem(row_idx, 1, item_file)
            self.setItem(row_idx, 2, item_line)
            self.setItem(row_idx, 3, item_col)
            self.setItem(row_idx, 4, item_msg)

    def clear_errors(self) -> None:
        self.setRowCount(0)

    def _on_cell_activated(self, row: int, _: int) -> None:
        line_item = self.item(row, 2)
        col_item = self.item(row, 3)
        if line_item is not None and col_item is not None:
            try:
                line = int(line_item.text())
                col = int(col_item.text())
                self.error_selected.emit(line, col)
            except ValueError:
                pass
