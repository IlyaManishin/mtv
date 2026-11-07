from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCloseEvent, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QMenu,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QToolBar,
    QWidget,
)

from src.common.constants import (
    APP_NAME,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
from src.common.localization import Language, get_text
from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.gui.dialogs.about_dialog import AboutDialog
from src.gui.dialogs.help_dialog import HelpDialog
from src.gui.dialogs.info_dialog import InfoDialog
from src.gui.icons import (
    create_about_icon,
    create_copy_icon,
    create_cut_icon,
    create_help_icon,
    create_new_icon,
    create_open_icon,
    create_paste_icon,
    create_redo_icon,
    create_run_icon,
    create_save_icon,
    create_undo_icon,
)
from src.gui.widgets.editor_tabs import EditorTabs
from src.gui.widgets.output_panel import OutputPanel


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_lang: Language = Language.RU
        self._current_title: str = APP_NAME

        # Core components
        self._editor_tabs: EditorTabs = EditorTabs(self)
        self._output_panel: OutputPanel = OutputPanel(self)
        self._splitter: QSplitter = QSplitter(Qt.Orientation.Vertical, self)

        # UI bars
        self._menu_bar: QMenuBar = self.menuBar()
        self._tool_bar: QToolBar = QToolBar("MainToolbar", self)
        self._status_bar: QStatusBar = self.statusBar()

        # Action holders for retranslation
        self._actions: dict[str, QAction] = {}
        self._menus: dict[str, QMenu] = {}

        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._connect_signals()
        self._apply_translations()
        # Create initial empty document
        self._editor_tabs.new_document()

    def _init_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._splitter.addWidget(self._editor_tabs)
        self._splitter.addWidget(self._output_panel)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 2)
        self._splitter.setSizes([450, 250])

        self.setCentralWidget(self._splitter)
        self.addToolBar(self._tool_bar)
        self.setStatusBar(self._status_bar)

    def _create_actions(self) -> None:
        # File actions
        act_new = QAction(create_new_icon(), "", self)
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(lambda: self._editor_tabs.new_document())
        self._actions["new"] = act_new

        act_open = QAction(create_open_icon(), "", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self._editor_tabs.open_file_dialog)
        self._actions["open"] = act_open

        act_save = QAction(create_save_icon(), "", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self._editor_tabs.save_current)
        self._actions["save"] = act_save

        act_save_as = QAction("", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self._editor_tabs.save_current_as)
        self._actions["save_as"] = act_save_as

        act_exit = QAction("", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        self._actions["exit"] = act_exit

        # Edit actions
        act_undo = QAction(create_undo_icon(), "", self)
        act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        act_undo.triggered.connect(self._on_undo)
        self._actions["undo"] = act_undo

        act_redo = QAction(create_redo_icon(), "", self)
        act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        act_redo.triggered.connect(self._on_redo)
        self._actions["redo"] = act_redo

        act_cut = QAction(create_cut_icon(), "", self)
        act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        act_cut.triggered.connect(self._on_cut)
        self._actions["cut"] = act_cut

        act_copy = QAction(create_copy_icon(), "", self)
        act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        act_copy.triggered.connect(self._on_copy)
        self._actions["copy"] = act_copy

        act_paste = QAction(create_paste_icon(), "", self)
        act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        act_paste.triggered.connect(self._on_paste)
        self._actions["paste"] = act_paste

        act_delete = QAction("", self)
        act_delete.setShortcut(QKeySequence.StandardKey.Delete)
        act_delete.triggered.connect(self._on_delete)
        self._actions["delete"] = act_delete

        act_select_all = QAction("", self)
        act_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        act_select_all.triggered.connect(self._on_select_all)
        self._actions["select_all"] = act_select_all

        # View zoom actions
        act_zoom_in = QAction("", self)
        act_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        act_zoom_in.triggered.connect(self._on_zoom_in)
        self._actions["zoom_in"] = act_zoom_in

        act_zoom_out = QAction("", self)
        act_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        act_zoom_out.triggered.connect(self._on_zoom_out)
        self._actions["zoom_out"] = act_zoom_out

        act_zoom_reset = QAction("", self)
        act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_zoom_reset.triggered.connect(self._on_zoom_reset)
        self._actions["zoom_reset"] = act_zoom_reset

        # Text menu actions
        self._actions["task_statement"] = self._create_info_action("action_task_statement")
        self._actions["grammar"] = self._create_info_action("action_grammar")
        self._actions["grammar_classification"] = self._create_info_action("action_grammar_classification")
        self._actions["analysis_method"] = self._create_info_action("action_analysis_method")
        self._actions["test_example"] = self._create_info_action("action_test_example")
        self._actions["literature"] = self._create_info_action("action_literature")
        self._actions["source_code"] = self._create_info_action("action_source_code")

        # Run action
        act_run = QAction(create_run_icon(), "", self)
        act_run.setShortcut(QKeySequence("F5"))
        act_run.triggered.connect(self._on_run_analysis)
        self._actions["run"] = act_run

        # Help actions
        act_help = QAction(create_help_icon(), "", self)
        act_help.setShortcut(QKeySequence.StandardKey.HelpContents)
        act_help.triggered.connect(self._on_show_help)
        self._actions["help"] = act_help

        act_about = QAction(create_about_icon(), "", self)
        act_about.triggered.connect(self._on_show_about)
        self._actions["about"] = act_about

        # Language actions
        act_lang_ru = QAction("Русский", self)
        act_lang_ru.setCheckable(True)
        act_lang_ru.setChecked(True)
        act_lang_ru.triggered.connect(lambda: self._set_language(Language.RU))
        self._actions["lang_ru"] = act_lang_ru

        act_lang_en = QAction("English", self)
        act_lang_en.setCheckable(True)
        act_lang_en.setChecked(False)
        act_lang_en.triggered.connect(lambda: self._set_language(Language.EN))
        self._actions["lang_en"] = act_lang_en

    def _create_info_action(self, title_key: str) -> QAction:
        action = QAction("", self)
        action.triggered.connect(lambda: self._on_show_text_info(title_key))
        return action

    def _on_show_text_info(self, title_key: str) -> None:
        title = get_text(title_key, self._current_lang)
        msg = (
            f"Раздел «{title}» будет реализован на следующих этапах разработки."
            if self._current_lang == Language.RU
            else f"Section \"{title}\" will be implemented in subsequent stages."
        )
        InfoDialog(title, msg, self).exec()

    def _create_menus(self) -> None:
        self._menu_bar.clear()

        # File menu
        menu_file = self._menu_bar.addMenu("")
        menu_file.addAction(self._actions["new"])
        menu_file.addAction(self._actions["open"])
        menu_file.addAction(self._actions["save"])
        menu_file.addAction(self._actions["save_as"])
        menu_file.addSeparator()
        menu_file.addAction(self._actions["exit"])
        self._menus["file"] = menu_file

        # Edit menu
        menu_edit = self._menu_bar.addMenu("")
        menu_edit.addAction(self._actions["undo"])
        menu_edit.addAction(self._actions["redo"])
        menu_edit.addSeparator()
        menu_edit.addAction(self._actions["cut"])
        menu_edit.addAction(self._actions["copy"])
        menu_edit.addAction(self._actions["paste"])
        menu_edit.addAction(self._actions["delete"])
        menu_edit.addSeparator()
        menu_edit.addAction(self._actions["select_all"])
        self._menus["edit"] = menu_edit

        # Text menu
        menu_text = self._menu_bar.addMenu("")
        menu_text.addAction(self._actions["task_statement"])
        menu_text.addAction(self._actions["grammar"])
        menu_text.addAction(self._actions["grammar_classification"])
        menu_text.addAction(self._actions["analysis_method"])
        menu_text.addAction(self._actions["test_example"])
        menu_text.addAction(self._actions["literature"])
        menu_text.addAction(self._actions["source_code"])
        self._menus["text"] = menu_text

        # Run menu
        menu_run = self._menu_bar.addMenu("")
        menu_run.addAction(self._actions["run"])
        self._menus["run"] = menu_run

        # View menu
        menu_view = self._menu_bar.addMenu("")
        menu_view.addAction(self._actions["zoom_in"])
        menu_view.addAction(self._actions["zoom_out"])
        menu_view.addAction(self._actions["zoom_reset"])
        self._menus["view"] = menu_view

        # Language menu
        menu_lang = self._menu_bar.addMenu("")
        menu_lang.addAction(self._actions["lang_ru"])
        menu_lang.addAction(self._actions["lang_en"])
        self._menus["language"] = menu_lang

        # Help menu
        menu_help = self._menu_bar.addMenu("")
        menu_help.addAction(self._actions["help"])
        menu_help.addAction(self._actions["about"])
        self._menus["help"] = menu_help

    def _create_toolbar(self) -> None:
        self._tool_bar.setMovable(False)
        self._tool_bar.clear()

        # Toolbar icons matching specification
        self._tool_bar.addAction(self._actions["new"])
        self._tool_bar.addAction(self._actions["open"])
        self._tool_bar.addAction(self._actions["save"])
        self._tool_bar.addSeparator()

        self._tool_bar.addAction(self._actions["undo"])
        self._tool_bar.addAction(self._actions["redo"])
        self._tool_bar.addSeparator()

        self._tool_bar.addAction(self._actions["copy"])
        self._tool_bar.addAction(self._actions["cut"])
        self._tool_bar.addAction(self._actions["paste"])
        self._tool_bar.addSeparator()

        self._tool_bar.addAction(self._actions["run"])
        self._tool_bar.addSeparator()

        self._tool_bar.addAction(self._actions["help"])
        self._tool_bar.addAction(self._actions["about"])

    def _connect_signals(self) -> None:
        self._editor_tabs.cursor_info_changed.connect(self._on_cursor_changed)
        self._editor_tabs.current_title_changed.connect(self._on_document_title_changed)
        self._output_panel.error_selected.connect(self._on_error_selected)

    def _apply_translations(self) -> None:
        lang = self._current_lang
        self._editor_tabs.update_language(lang)
        self._output_panel.update_language(lang)

        self._menus["file"].setTitle(get_text("menu_file", lang))
        self._menus["edit"].setTitle(get_text("menu_edit", lang))
        self._menus["text"].setTitle(get_text("menu_text", lang))
        self._menus["run"].setTitle(get_text("menu_run", lang))
        self._menus["view"].setTitle(get_text("menu_view", lang))
        self._menus["language"].setTitle(get_text("menu_language", lang))
        self._menus["help"].setTitle(get_text("menu_help", lang))

        self._actions["new"].setText(get_text("action_new", lang))
        self._actions["new"].setToolTip(get_text("action_new", lang))

        self._actions["open"].setText(get_text("action_open", lang))
        self._actions["open"].setToolTip(get_text("action_open", lang))

        self._actions["save"].setText(get_text("action_save", lang))
        self._actions["save"].setToolTip(get_text("action_save", lang))

        self._actions["save_as"].setText(get_text("action_save_as", lang))
        self._actions["save_as"].setToolTip(get_text("action_save_as", lang))

        self._actions["exit"].setText(get_text("action_exit", lang))

        self._actions["undo"].setText(get_text("action_undo", lang))
        self._actions["undo"].setToolTip(get_text("action_undo", lang))

        self._actions["redo"].setText(get_text("action_redo", lang))
        self._actions["redo"].setToolTip(get_text("action_redo", lang))

        self._actions["cut"].setText(get_text("action_cut", lang))
        self._actions["cut"].setToolTip(get_text("action_cut", lang))

        self._actions["copy"].setText(get_text("action_copy", lang))
        self._actions["copy"].setToolTip(get_text("action_copy", lang))

        self._actions["paste"].setText(get_text("action_paste", lang))
        self._actions["paste"].setToolTip(get_text("action_paste", lang))

        self._actions["delete"].setText(get_text("action_delete", lang))
        self._actions["select_all"].setText(get_text("action_select_all", lang))

        self._actions["zoom_in"].setText(get_text("action_zoom_in", lang))
        self._actions["zoom_out"].setText(get_text("action_zoom_out", lang))
        self._actions["zoom_reset"].setText(get_text("action_zoom_reset", lang))

        self._actions["task_statement"].setText(get_text("action_task_statement", lang))
        self._actions["grammar"].setText(get_text("action_grammar", lang))
        self._actions["grammar_classification"].setText(get_text("action_grammar_classification", lang))
        self._actions["analysis_method"].setText(get_text("action_analysis_method", lang))
        self._actions["test_example"].setText(get_text("action_test_example", lang))
        self._actions["literature"].setText(get_text("action_literature", lang))
        self._actions["source_code"].setText(get_text("action_source_code", lang))

        self._actions["run"].setText(get_text("action_run", lang))
        self._actions["run"].setToolTip(get_text("action_run", lang))

        self._actions["help"].setText(get_text("action_help", lang))
        self._actions["help"].setToolTip(get_text("action_help", lang))

        self._actions["about"].setText(get_text("action_about", lang))
        self._actions["about"].setToolTip(get_text("action_about", lang))

        self._status_bar.showMessage(get_text("status_ready", lang))

    def _set_language(self, lang: Language) -> None:
        self._current_lang = lang
        self._actions["lang_ru"].setChecked(lang == Language.RU)
        self._actions["lang_en"].setChecked(lang == Language.EN)
        self._apply_translations()

    def _on_undo(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.undo()

    def _on_redo(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.redo()

    def _on_cut(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.cut()

    def _on_copy(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.copy()

    def _on_paste(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.paste()

    def _on_delete(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.textCursor().removeSelectedText()

    def _on_select_all(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.selectAll()

    def _on_zoom_in(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.zoom_in()
        self._output_panel.zoom_in()

    def _on_zoom_out(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.zoom_out()
        self._output_panel.zoom_out()

    def _on_zoom_reset(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.reset_zoom()
        self._output_panel.reset_zoom()

    def _on_run_analysis(self) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is None:
            return

        curr.clear_error_highlight()
        code_text = curr.toPlainText()
        path = self._editor_tabs.current_file_path() or "untitled"

        # Step 1: Lexical analysis (Tokenizer)
        lexer = Lexer(code_text, file_path=path)
        tokens, lexical_errors = lexer.tokenize()

        if lexical_errors:
            logs = [
                f"Лексический анализ: обнаружено ошибок: {len(lexical_errors)}.",
                "Синтаксический анализ остановлен из-за лексических ошибок.",
            ]
            self._output_panel.set_log_messages(logs)
            self._output_panel.set_errors(lexical_errors)
            return

        # Step 2: Syntactic analysis (Parser)
        parser = Parser(tokens, file_path=path)
        result = parser.parse()

        # Prepend token count info to log
        result.log_messages.insert(
            0, f"Токенизация успешно выполнена: распознано токенов: {len(tokens) - 1}."
        )

        self._output_panel.set_log_messages(result.log_messages)
        self._output_panel.set_errors(result.errors)

    def _on_error_selected(self, line: int, col: int) -> None:
        curr = self._editor_tabs.current_editor()
        if curr is not None:
            curr.set_error_highlight(line, col)
            self._editor_tabs.setFocus()

    def _on_cursor_changed(self, line: int, col: int) -> None:
        text = get_text("status_cursor", self._current_lang).format(line=line, col=col)
        self._status_bar.showMessage(text)

    def _on_document_title_changed(self, title: str) -> None:
        self._current_title = title
        self.setWindowTitle(f"{APP_NAME} - {title}")

    def _on_show_help(self) -> None:
        dialog = HelpDialog(self._current_lang, self)
        dialog.exec()

    def _on_show_about(self) -> None:
        dialog = AboutDialog(self._current_lang, self)
        dialog.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._editor_tabs.close_all_tabs():
            event.accept()
        else:
            event.ignore()
