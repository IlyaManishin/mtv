from enum import Enum
from typing import Final


class Language(str, Enum):
    RU = "ru"
    EN = "en"


TRANSLATIONS: Final[dict[str, dict[Language, str]]] = {
    # Menus
    "menu_file": {Language.RU: "&Файл", Language.EN: "&File"},
    "menu_edit": {Language.RU: "&Правка", Language.EN: "&Edit"},
    "menu_text": {Language.RU: "&Текст", Language.EN: "&Text"},
    "menu_run": {Language.RU: "&Пуск", Language.EN: "&Run"},
    "menu_help": {Language.RU: "&Справка", Language.EN: "&Help"},
    "menu_view": {Language.RU: "&Вид", Language.EN: "&View"},
    "menu_language": {Language.RU: "&Локализация", Language.EN: "&Language"},

    # File actions
    "action_new": {Language.RU: "Создать", Language.EN: "New"},
    "action_open": {Language.RU: "Открыть", Language.EN: "Open"},
    "action_save": {Language.RU: "Сохранить", Language.EN: "Save"},
    "action_save_as": {Language.RU: "Сохранить как...", Language.EN: "Save As..."},
    "action_exit": {Language.RU: "Выход", Language.EN: "Exit"},

    # Edit actions
    "action_undo": {Language.RU: "Отменить", Language.EN: "Undo"},
    "action_redo": {Language.RU: "Повторить", Language.EN: "Redo"},
    "action_cut": {Language.RU: "Вырезать", Language.EN: "Cut"},
    "action_copy": {Language.RU: "Копировать", Language.EN: "Copy"},
    "action_paste": {Language.RU: "Вставить", Language.EN: "Paste"},
    "action_delete": {Language.RU: "Удалить", Language.EN: "Delete"},
    "action_select_all": {Language.RU: "Выделить все", Language.EN: "Select All"},

    # View actions
    "action_zoom_in": {Language.RU: "Увеличить шрифт", Language.EN: "Zoom In"},
    "action_zoom_out": {Language.RU: "Уменьшить шрифт", Language.EN: "Zoom Out"},
    "action_zoom_reset": {Language.RU: "Сбросить масштаб", Language.EN: "Reset Zoom"},

    # Text menu actions
    "action_task_statement": {Language.RU: "Постановка задачи", Language.EN: "Problem Statement"},
    "action_grammar": {Language.RU: "Грамматика", Language.EN: "Grammar"},
    "action_grammar_classification": {Language.RU: "Классификация грамматики", Language.EN: "Grammar Classification"},
    "action_analysis_method": {Language.RU: "Метод анализа", Language.EN: "Analysis Method"},
    "action_test_example": {Language.RU: "Тестовый пример", Language.EN: "Test Example"},
    "action_literature": {Language.RU: "Список литературы", Language.EN: "References"},
    "action_source_code": {Language.RU: "Исходный код программы", Language.EN: "Source Code"},

    # Run action
    "action_run": {Language.RU: "Пуск", Language.EN: "Run"},
    "action_run_parser": {Language.RU: "Запуск синтаксического анализатора", Language.EN: "Run Syntax Analyzer"},

    # Help actions
    "action_help": {Language.RU: "Вызов справки", Language.EN: "Help Topics"},
    "action_about": {Language.RU: "О программе", Language.EN: "About"},

    # Output panel tabs
    "tab_output": {Language.RU: "Результаты", Language.EN: "Output"},
    "tab_errors": {Language.RU: "Таблица ошибок", Language.EN: "Error Table"},

    # Error table headers
    "col_num": {Language.RU: "№", Language.EN: "#"},
    "col_file": {Language.RU: "Файл", Language.EN: "File"},
    "col_line": {Language.RU: "Строка", Language.EN: "Line"},
    "col_col": {Language.RU: "Столбец", Language.EN: "Column"},
    "col_msg": {Language.RU: "Сообщение", Language.EN: "Message"},

    # Status & Dialogs
    "status_ready": {Language.RU: "Готово", Language.EN: "Ready"},
    "status_cursor": {Language.RU: "Стр {line}, Кол {col}", Language.EN: "Ln {line}, Col {col}"},
    "default_tab_name": {Language.RU: "Новый документ", Language.EN: "New Document"},
    "save_prompt_title": {Language.RU: "Сохранение изменений", Language.EN: "Save Changes"},
    "save_prompt_msg": {
        Language.RU: "Сохранить изменения в документе \"{name}\"?",
        Language.EN: "Save changes to document \"{name}\"?",
    },
    "file_filter": {
        Language.RU: "Текстовые файлы (*.txt *.py);;Все файлы (*.*)",
        Language.EN: "Text files (*.txt *.py);;All files (*.*)",
    },
    "about_title": {Language.RU: "О программе Compiler", Language.EN: "About Compiler"},
    "help_title": {Language.RU: "Справка - Руководство пользователя", Language.EN: "Help - User Guide"},
}


def get_text(key: str, lang: Language) -> str:
    item = TRANSLATIONS.get(key)
    if item is None:
        return key
    return item.get(lang, item.get(Language.RU, key))
