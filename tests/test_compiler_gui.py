import os
import sys
import unittest

# Ensure headless operation for Qt in testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

from src.common.constants import APP_NAME
from src.common.localization import Language
from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.compiler.token import TokenType
from src.gui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)


class TestLexer(unittest.TestCase):
    def test_token_positions_and_attributes(self) -> None:
        source = "if a:\n    x = y"
        lexer = Lexer(source, file_path="sample.py")
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)

        # Token 0: if
        self.assertEqual(tokens[0].type, TokenType.KEYWORD_IF)
        self.assertEqual(tokens[0].value, "if")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

        # Token 1: a
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "a")
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 4)

        # Token 2: :
        self.assertEqual(tokens[2].type, TokenType.COLON)
        self.assertEqual(tokens[2].line, 1)
        self.assertEqual(tokens[2].column, 5)

        # Token 3: \n (TERM_NEWLINE)
        self.assertEqual(tokens[3].type, TokenType.TERM_NEWLINE)
        self.assertEqual(tokens[3].line, 1)

        # Token 4: 4 spaces indent (TERM_INDENT)
        self.assertEqual(tokens[4].type, TokenType.TERM_INDENT)
        self.assertEqual(tokens[4].line, 2)
        self.assertEqual(tokens[4].column, 1)
        self.assertEqual(tokens[4].length, 4)

        # Token 5: x
        self.assertEqual(tokens[5].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[5].value, "x")
        self.assertEqual(tokens[5].line, 2)
        self.assertEqual(tokens[5].column, 5)

        # Token 6: =
        self.assertEqual(tokens[6].type, TokenType.ASSIGN)
        self.assertEqual(tokens[6].line, 2)
        self.assertEqual(tokens[6].column, 7)

        # Token 7: y
        self.assertEqual(tokens[7].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[7].value, "y")
        self.assertEqual(tokens[7].line, 2)
        self.assertEqual(tokens[7].column, 9)

        # DEDENT at EOF
        has_dedent = any(t.type == TokenType.TERM_DEDENT for t in tokens)
        self.assertTrue(has_dedent)

    def test_lexer_unknown_characters(self) -> None:
        source = "if @:"
        lexer = Lexer(source, file_path="bad.py")
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line, 1)
        self.assertEqual(errors[0].column, 4)
        self.assertIn("@", errors[0].message)


class TestParser(unittest.TestCase):
    def test_valid_basic_statement(self) -> None:
        source = "if a: NEWLINE INDENT x=y NEWLINE DEDENT else: NEWLINE INDENT z=w NEWLINE DEDENT"
        lexer = Lexer(source, file_path="basic.py")
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0)

        parser = Parser(tokens, file_path="basic.py")
        result = parser.parse()
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_valid_real_python_code(self) -> None:
        source = "if a:\n    x = y\nelse:\n    z = w\n"
        lexer = Lexer(source, file_path="real.py")
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0)

        parser = Parser(tokens, file_path="real.py")
        result = parser.parse()
        self.assertTrue(result.is_valid, f"Failed with errors: {result.errors}")
        self.assertEqual(len(result.errors), 0)

    def test_valid_compound_condition_real_python(self) -> None:
        source = "if a or b and c:\n    x = y\nelse:\n    z = w\n"
        lexer = Lexer(source, file_path="compound_real.py")
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0)

        parser = Parser(tokens, file_path="compound_real.py")
        result = parser.parse()
        self.assertTrue(result.is_valid, f"Failed with errors: {result.errors}")
        self.assertEqual(len(result.errors), 0)

    def test_syntax_error_missing_colon(self) -> None:
        source = "if a NEWLINE INDENT x=y NEWLINE DEDENT else: NEWLINE INDENT z=w NEWLINE DEDENT"
        tokens, _ = Lexer(source, file_path="err.py").tokenize()
        result = Parser(tokens, file_path="err.py").parse()
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("':'", result.errors[0].message)

    def test_multiple_errors_found(self) -> None:
        source = "if a\n    x =\nelse\n    z ="
        tokens, _ = Lexer(source, file_path="multi.py").tokenize()
        result = Parser(tokens, file_path="multi.py").parse()
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 4)
        lines = [err.line for err in result.errors]
        self.assertEqual(lines, [1, 2, 3, 4])


class TestGui(unittest.TestCase):
    def setUp(self) -> None:
        self.window = MainWindow()

    def tearDown(self) -> None:
        # Test safe non-looping cleanup
        self.window._editor_tabs.close_all_tabs()
        self.window.close()

    def test_initial_state(self) -> None:
        self.assertTrue(self.window.windowTitle().startswith(APP_NAME))
        self.assertEqual(self.window._editor_tabs.count(), 1)
        curr = self.window._editor_tabs.current_editor()
        self.assertIsNotNone(curr)

    def test_run_analysis_action(self) -> None:
        curr = self.window._editor_tabs.current_editor()
        assert curr is not None
        curr.setPlainText("if a: NEWLINE INDENT x=y NEWLINE DEDENT else: NEWLINE INDENT z=w NEWLINE DEDENT")

        self.window._on_run_analysis()
        self.assertEqual(self.window._output_panel._error_table.rowCount(), 0)
        log = self.window._output_panel._log_edit.toPlainText()
        self.assertIn("Лексический анализ", log)
        self.assertIn("успешно завершен", log)

    def test_error_navigation(self) -> None:
        curr = self.window._editor_tabs.current_editor()
        assert curr is not None
        curr.setPlainText("if a: NEWLINE")  # incomplete

        self.window._on_run_analysis()
        self.assertGreater(self.window._output_panel._error_table.rowCount(), 0)

        # Trigger navigation
        self.window._on_error_selected(1, 13)
        self.assertEqual(curr._error_line, 1)

    def test_zoom(self) -> None:
        curr = self.window._editor_tabs.current_editor()
        assert curr is not None
        initial_font_size = curr._current_font_size

        self.window._on_zoom_in()
        self.assertEqual(curr._current_font_size, initial_font_size + 1)
        self.window._on_zoom_out()
        self.assertEqual(curr._current_font_size, initial_font_size)
        self.window._on_zoom_reset()
        self.assertEqual(curr._current_font_size, 12)

    def test_localization(self) -> None:
        self.window._set_language(Language.EN)
        self.assertEqual(self.window._actions["new"].text(), "New")
        self.assertEqual(self.window._menus["file"].title(), "&File")

        self.window._set_language(Language.RU)
        self.assertEqual(self.window._actions["new"].text(), "Создать")
        self.assertEqual(self.window._menus["file"].title(), "&Файл")


if __name__ == "__main__":
    unittest.main()
