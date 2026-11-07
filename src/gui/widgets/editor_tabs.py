from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTabWidget, QWidget

from src.common.localization import Language, get_text
from src.gui.widgets.code_editor import CodeEditor


class EditorTabs(QTabWidget):
    cursor_info_changed = pyqtSignal(int, int)
    current_title_changed = pyqtSignal(str)
    file_path_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_lang: Language = Language.RU
        self._untitled_counter: int = 1
        self._file_paths: dict[CodeEditor, Optional[str]] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(lambda idx: self.close_tab(idx, create_new_if_empty=True))
        self.currentChanged.connect(self._on_current_changed)

    def update_language(self, lang: Language) -> None:
        self._current_lang = lang

    def new_document(self, content: str = "") -> CodeEditor:
        editor = CodeEditor(self)
        editor.setPlainText(content)

        title = f"{get_text('default_tab_name', self._current_lang)} {self._untitled_counter}"
        self._untitled_counter += 1
        self._file_paths[editor] = None

        index = self.addTab(editor, title)
        self.setCurrentIndex(index)

        editor.cursor_info_changed.connect(self._on_editor_cursor_info)
        editor.file_dropped.connect(self.open_file_by_path)
        editor.textChanged.connect(lambda: self._on_editor_text_changed(editor))

        return editor

    def current_editor(self) -> Optional[CodeEditor]:
        widget = self.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def current_file_path(self) -> Optional[str]:
        editor = self.current_editor()
        if editor is not None:
            return self._file_paths.get(editor)
        return None

    def open_file_dialog(self) -> bool:
        filters = get_text("file_filter", self._current_lang)
        file_path, _ = QFileDialog.getOpenFileName(
            self, get_text("action_open", self._current_lang), "", filters
        )
        if file_path:
            return self.open_file_by_path(file_path)
        return False

    def open_file_by_path(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.is_file():
            return False

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="cp1251")
            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Could not read file:\n{ex}")
                return False

        # If current document is empty, unmodified, and untitled, reuse it
        curr = self.current_editor()
        if (
            curr is not None
            and self._file_paths.get(curr) is None
            and not curr.document().isModified()
            and not curr.toPlainText()
        ):
            target_editor = curr
            self._file_paths[target_editor] = str(path.resolve())
            target_editor.setPlainText(content)
            target_editor.document().setModified(False)
            idx = self.indexOf(target_editor)
            self.setTabText(idx, path.name)
            self.current_title_changed.emit(path.name)
            self.file_path_changed.emit(str(path.resolve()))
            return True

        editor = CodeEditor(self)
        editor.setPlainText(content)
        editor.document().setModified(False)
        self._file_paths[editor] = str(path.resolve())

        index = self.addTab(editor, path.name)
        self.setCurrentIndex(index)

        editor.cursor_info_changed.connect(self._on_editor_cursor_info)
        editor.file_dropped.connect(self.open_file_by_path)
        editor.textChanged.connect(lambda: self._on_editor_text_changed(editor))

        self.current_title_changed.emit(path.name)
        self.file_path_changed.emit(str(path.resolve()))
        return True

    def save_current(self) -> bool:
        editor = self.current_editor()
        if editor is None:
            return False

        path_str = self._file_paths.get(editor)
        if path_str is None:
            return self.save_current_as()

        return self._write_to_file(editor, path_str)

    def save_current_as(self) -> bool:
        editor = self.current_editor()
        if editor is None:
            return False

        filters = get_text("file_filter", self._current_lang)
        suggested = self.tabText(self.indexOf(editor)).rstrip("*")
        file_path, _ = QFileDialog.getSaveFileName(
            self, get_text("action_save_as", self._current_lang), suggested, filters
        )
        if not file_path:
            return False

        if self._write_to_file(editor, file_path):
            self._file_paths[editor] = file_path
            path = Path(file_path)
            self.setTabText(self.indexOf(editor), path.name)
            self.current_title_changed.emit(path.name)
            self.file_path_changed.emit(file_path)
            return True
        return False

    def _write_to_file(self, editor: CodeEditor, file_path: str) -> bool:
        try:
            path = Path(file_path)
            path.write_text(editor.toPlainText(), encoding="utf-8")
            editor.document().setModified(False)
            idx = self.indexOf(editor)
            clean_title = path.name
            self.setTabText(idx, clean_title)
            return True
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{ex}")
            return False

    def prompt_save_if_modified(self, index: int) -> bool:
        widget = self.widget(index)
        if not isinstance(widget, CodeEditor):
            return True

        if not widget.document().isModified():
            return True

        title = self.tabText(index).rstrip("*")
        msg = get_text("save_prompt_msg", self._current_lang).format(name=title)
        reply = QMessageBox.question(
            self,
            get_text("save_prompt_title", self._current_lang),
            msg,
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            self.setCurrentIndex(index)
            return self.save_current()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def close_tab(self, index: int, create_new_if_empty: bool = True) -> bool:
        if not self.prompt_save_if_modified(index):
            return False

        widget = self.widget(index)
        if isinstance(widget, CodeEditor):
            self._file_paths.pop(widget, None)

        self.removeTab(index)
        if create_new_if_empty and self.count() == 0:
            self.new_document()
        return True

    def close_all_tabs(self) -> bool:
        while self.count() > 0:
            last_idx = self.count() - 1
            if not self.close_tab(last_idx, create_new_if_empty=False):
                return False
        return True

    def _on_editor_cursor_info(self, line: int, col: int) -> None:
        editor = self.sender()
        if editor == self.current_editor():
            self.cursor_info_changed.emit(line, col)

    def _on_editor_text_changed(self, editor: CodeEditor) -> None:
        idx = self.indexOf(editor)
        if idx != -1:
            title = self.tabText(idx)
            is_mod = editor.document().isModified()
            if is_mod and not title.endswith("*"):
                self.setTabText(idx, f"{title}*")
            elif not is_mod and title.endswith("*"):
                self.setTabText(idx, title[:-1])

    def _on_current_changed(self, index: int) -> None:
        if index < 0:
            return
        editor = self.current_editor()
        if editor is not None:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.cursor_info_changed.emit(line, col)
            path = self._file_paths.get(editor)
            self.file_path_changed.emit(path or "")
            self.current_title_changed.emit(self.tabText(index).rstrip("*"))
