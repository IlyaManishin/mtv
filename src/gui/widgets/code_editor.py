from typing import Optional

from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QFontMetricsF,
    QPaintEvent,
    QPainter,
    QResizeEvent,
    QTextCursor,
    QTextFormat,
    QWheelEvent,
)
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from src.common.constants import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, MAX_FONT_SIZE, MIN_FONT_SIZE
from src.gui.highlighter import PythonSyntaxHighlighter
from src.gui.widgets.line_number_area import LineNumberArea


class CodeEditor(QPlainTextEdit):
    cursor_info_changed = pyqtSignal(int, int)  # line (1-based), column (1-based)
    file_dropped = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._line_number_area: LineNumberArea = LineNumberArea(self)
        self._current_font_size: int = DEFAULT_FONT_SIZE
        self._error_line: Optional[int] = None

        self._init_ui()
        self._highlighter: PythonSyntaxHighlighter = PythonSyntaxHighlighter(self.document())

    def _init_ui(self) -> None:
        font = QFont(DEFAULT_FONT_FAMILY, self._current_font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(" ") * 4)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

        self._update_line_number_area_width(0)
        self.highlight_lines()
        self.setAcceptDrops(True)

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(max(1, self.blockCount()))))
        space = 15 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def _update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        content_rect = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(content_rect.left(), content_rect.top(), self.line_number_area_width(), content_rect.height())
        )

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        painter.setPen(QColor("#787878"))
        painter.setFont(self.font())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number_str = str(block_number + 1)
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number_str,
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.setPen(QColor("#D0D0D0"))
        painter.drawLine(
            self._line_number_area.width() - 1,
            event.rect().top(),
            self._line_number_area.width() - 1,
            event.rect().bottom(),
        )

    def _on_cursor_position_changed(self) -> None:
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_info_changed.emit(line, col)
        self.highlight_lines()

    def highlight_lines(self) -> None:
        extra_selections: list[QTextEdit.ExtraSelection] = []

        if not self.isReadOnly():
            # Current caret line highlight
            current_selection = QTextEdit.ExtraSelection()
            current_selection.format.setBackground(QColor("#E8F2FE"))
            current_selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            current_selection.cursor = self.textCursor()
            current_selection.cursor.clearSelection()
            extra_selections.append(current_selection)

        # Highlight error line if set (yellow background)
        if self._error_line is not None and self._error_line > 0:
            block = self.document().findBlockByNumber(self._error_line - 1)
            if block.isValid():
                error_selection = QTextEdit.ExtraSelection()
                error_selection.format.setBackground(QColor("#FFF485"))
                error_selection.format.setProperty(
                    QTextFormat.Property.FullWidthSelection, True
                )
                error_selection.cursor = QTextCursor(block)
                error_selection.cursor.clearSelection()
                extra_selections.append(error_selection)

        self.setExtraSelections(extra_selections)

    def set_error_highlight(self, line: int, column: int) -> None:
        self._error_line = line
        block = self.document().findBlockByNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            col_target = max(0, column - 1)
            cursor.setPosition(block.position() + min(col_target, block.length() - 1))
            self.setTextCursor(cursor)
            self.centerCursor()
        self.highlight_lines()

    def clear_error_highlight(self) -> None:
        self._error_line = None
        self.highlight_lines()

    def zoom_in(self, delta: int = 1) -> None:
        if self._current_font_size + delta <= MAX_FONT_SIZE:
            self._current_font_size += delta
            self._apply_font_size()

    def zoom_out(self, delta: int = 1) -> None:
        if self._current_font_size - delta >= MIN_FONT_SIZE:
            self._current_font_size -= delta
            self._apply_font_size()

    def reset_zoom(self) -> None:
        self._current_font_size = DEFAULT_FONT_SIZE
        self._apply_font_size()

    def _apply_font_size(self) -> None:
        font = self.font()
        font.setPointSize(self._current_font_size)
        self.setFont(font)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(" ") * 4)
        self._update_line_number_area_width(0)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                local_path = urls[0].toLocalFile()
                if local_path:
                    self.file_dropped.emit(local_path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
