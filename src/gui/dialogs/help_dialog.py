from typing import Optional

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout, QWidget

from src.common.localization import Language, get_text


class HelpDialog(QDialog):
    def __init__(self, lang: Language, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(get_text("help_title", lang))
        self.resize(750, 520)
        self._init_ui(lang)

    def _init_ui(self, lang: Language) -> None:
        layout = QVBoxLayout(self)

        browser = QTextBrowser(self)
        browser.setHtml(self._generate_help_html(lang))
        layout.addWidget(browser)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def _generate_help_html(self, lang: Language) -> str:
        if lang == Language.RU:
            return """
            <h3>Руководство пользователя — Текстовый редактор Compiler</h3>
            <p>Программа представляет собой специализированный текстовый редактор с поддержкой функций языкового процессора.</p>

            <h4>1. Меню «Файл»</h4>
            <ul>
                <li><b>Создать (Ctrl+N):</b> Создать новый пустой документ во вкладке.</li>
                <li><b>Открыть (Ctrl+O):</b> Открыть существующий файл с диска.</li>
                <li><b>Сохранить (Ctrl+S):</b> Сохранить текущие изменения в активном файле.</li>
                <li><b>Сохранить как (Ctrl+Shift+S):</b> Сохранить документ под новым именем/путем.</li>
                <li><b>Выход (Ctrl+Q):</b> Завершить работу приложения с проверкой несохраненных изменений.</li>
            </ul>

            <h4>2. Меню «Правка»</h4>
            <ul>
                <li><b>Отменить (Ctrl+Z):</b> Отменить последнее действие в редакторе.</li>
                <li><b>Повторить (Ctrl+Y):</b> Повторить отмененное действие.</li>
                <li><b>Вырезать (Ctrl+X):</b> Вырезать выделенный фрагмент в буфер обмена.</li>
                <li><b>Копировать (Ctrl+C):</b> Скопировать выделенный фрагмент в буфер обмена.</li>
                <li><b>Вставить (Ctrl+V):</b> Вставить текст из буфера обмена.</li>
                <li><b>Удалить (Del):</b> Удалить выделенный текст.</li>
                <li><b>Выделить все (Ctrl+A):</b> Выделить весь текст активного документа.</li>
            </ul>

            <h4>3. Меню «Вид»</h4>
            <ul>
                <li><b>Увеличить шрифт (Ctrl++):</b> Увеличить размер шрифта в окне редактора.</li>
                <li><b>Уменьшить шрифт (Ctrl+-):</b> Уменьшить размер шрифта в окне редактора.</li>
                <li><b>Сбросить масштаб (Ctrl+0):</b> Вернуть стандартный размер шрифта.</li>
            </ul>

            <h4>4. Меню «Текст»</h4>
            <ul>
                <li><b>Постановка задачи:</b> Описание целевой грамматики условного оператора Python.</li>
                <li><b>Грамматика:</b> Формальное задание терминалов, нетерминалов и правил вывода.</li>
                <li><b>Классификация грамматики:</b> Определение типа грамматики по Хомскому.</li>
                <li><b>Метод анализа:</b> Описание алгоритма синтаксического анализа.</li>
                <li><b>Тестовый пример:</b> Корректные примеры для проверки парсера.</li>
                <li><b>Список литературы:</b> Используемые литературные источники.</li>
                <li><b>Исходный код программы:</b> Описание архитектуры и модулей приложения.</li>
            </ul>

            <h4>5. Меню «Пуск»</h4>
            <ul>
                <li><b>Запуск синтаксического анализатора (F5):</b> Запустить лексический токенизатор и синтаксический анализ текста. Результаты выводятся в нижнюю панель. Ошибки отображаются в таблице, клик по ошибке подсвечивает строку в редакторе.</li>
            </ul>

            <h4>6. Меню «Локализация»</h4>
            <ul>
                <li>Переключение языка интерфейса между русским и английским.</li>
            </ul>

            <h4>7. Меню «Справка»</h4>
            <ul>
                <li><b>Вызов справки (F1):</b> Открыть настоящее руководство.</li>
                <li><b>О программе:</b> Информация об авторе и назначении системы.</li>
            </ul>
            """
        else:
            return """
            <h3>User Guide — Compiler Text Editor</h3>
            <p>The program is a specialized text editor supporting language processor features.</p>

            <h4>1. File Menu</h4>
            <ul>
                <li><b>New (Ctrl+N):</b> Create a new empty document tab.</li>
                <li><b>Open (Ctrl+O):</b> Open an existing file from disk.</li>
                <li><b>Save (Ctrl+S):</b> Save current changes to the active file.</li>
                <li><b>Save As (Ctrl+Shift+S):</b> Save current document to a new location.</li>
                <li><b>Exit (Ctrl+Q):</b> Exit the application with unsaved changes prompt.</li>
            </ul>

            <h4>2. Edit Menu</h4>
            <ul>
                <li><b>Undo (Ctrl+Z):</b> Undo the last editing action.</li>
                <li><b>Redo (Ctrl+Y):</b> Redo the last undone action.</li>
                <li><b>Cut (Ctrl+X):</b> Cut selected text to clipboard.</li>
                <li><b>Copy (Ctrl+C):</b> Copy selected text to clipboard.</li>
                <li><b>Paste (Ctrl+V):</b> Paste text from clipboard.</li>
                <li><b>Delete (Del):</b> Delete selected text.</li>
                <li><b>Select All (Ctrl+A):</b> Select all text in active document.</li>
            </ul>

            <h4>3. View Menu</h4>
            <ul>
                <li><b>Zoom In (Ctrl++):</b> Increase font size.</li>
                <li><b>Zoom Out (Ctrl+-):</b> Decrease font size.</li>
                <li><b>Reset Zoom (Ctrl+0):</b> Restore default font size.</li>
            </ul>

            <h4>4. Text Menu</h4>
            <ul>
                <li>Access Problem Statement, Grammar, Classification, Analysis Method, Test Examples, References, and Source Code.</li>
            </ul>

            <h4>5. Run Menu</h4>
            <ul>
                <li><b>Run Syntax Analyzer (F5):</b> Execute tokenizer and syntactic analysis. Errors are shown in a table, clicking an error navigates to the line.</li>
            </ul>

            <h4>6. Language Menu</h4>
            <ul>
                <li>Switch interface language between Russian and English.</li>
            </ul>

            <h4>7. Help Menu</h4>
            <ul>
                <li><b>Help Topics (F1):</b> Open this user guide.</li>
                <li><b>About:</b> Information about the program.</li>
            </ul>
            """
