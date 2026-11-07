from src.compiler.models import AnalysisResult, ErrorRecord
from src.compiler.token import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token], file_path: str = "untitled") -> None:
        self._tokens: list[Token] = tokens
        self._file_path: str = file_path
        self._cursor: int = 0
        self._errors: list[ErrorRecord] = []
        self._log: list[str] = []

    def parse(self) -> AnalysisResult:
        self._cursor = 0
        self._errors.clear()
        self._log.clear()

        # Check if empty (only EOF token)
        if len(self._tokens) <= 1:
            self._log.append("Предупреждение: Входной поток токенов пуст.")
            return AnalysisResult(
                is_valid=False,
                log_messages=self._log,
                errors=[],
                tokens=self._tokens,
            )

        self._log.append(f"Запуск синтаксического анализатора (токенов: {len(self._tokens) - 1}).")

        self._parse_statement()

        if self._errors:
            self._log.append(f"Синтаксический анализ завершен с ошибками: {len(self._errors)} шт.")
            return AnalysisResult(
                is_valid=False,
                log_messages=self._log,
                errors=self._errors,
                tokens=self._tokens,
            )

        self._log.append("Синтаксический анализ успешно завершен. Ошибок не обнаружено.")
        return AnalysisResult(
            is_valid=True,
            log_messages=self._log,
            errors=[],
            tokens=self._tokens,
        )

    def _current_token(self) -> Token:
        if self._cursor < len(self._tokens):
            return self._tokens[self._cursor]
        return self._tokens[-1]

    def _expect(self, expected_type: TokenType, description: str) -> bool:
        tok = self._current_token()
        if tok.type == expected_type:
            self._cursor += 1
            return True

        found_str = f"'{tok.value}'" if tok.value else "конец файла"
        self._errors.append(
            ErrorRecord(
                index=len(self._errors) + 1,
                file_path=self._file_path,
                line=tok.line,
                column=tok.column,
                message=f"Ожидалось: {description}, но получено: {found_str}",
            )
        )
        return False

    def _parse_statement(self) -> None:
        # <IfStmt> -> 'if' <Condition> ':' 'NEWLINE' 'INDENT' <Assignment> 'NEWLINE' 'DEDENT'
        #             'else' ':' 'NEWLINE' 'INDENT' <Assignment> 'NEWLINE' 'DEDENT'
        if not self._expect(TokenType.KEYWORD_IF, "'if'"):
            return

        if not self._parse_condition():
            return

        if not self._expect(TokenType.COLON, "':' после условия"):
            return

        if not self._expect(TokenType.TERM_NEWLINE, "'NEWLINE' после ':'"):
            return

        if not self._expect(TokenType.TERM_INDENT, "'INDENT' в начале блока if"):
            return

        if not self._parse_assignment():
            return

        if not self._expect(TokenType.TERM_NEWLINE, "'NEWLINE' после присваивания"):
            return

        if not self._expect(TokenType.TERM_DEDENT, "'DEDENT' в конце блока if"):
            return

        if not self._expect(TokenType.KEYWORD_ELSE, "'else'"):
            return

        if not self._expect(TokenType.COLON, "':' после 'else'"):
            return

        if not self._expect(TokenType.TERM_NEWLINE, "'NEWLINE' после 'else:'"):
            return

        if not self._expect(TokenType.TERM_INDENT, "'INDENT' в начале блока else"):
            return

        if not self._parse_assignment():
            return

        if not self._expect(TokenType.TERM_NEWLINE, "'NEWLINE' после присваивания в else"):
            return

        if not self._expect(TokenType.TERM_DEDENT, "'DEDENT' в конце блока else"):
            return

        tok = self._current_token()
        if tok.type != TokenType.EOF:
            self._errors.append(
                ErrorRecord(
                    index=len(self._errors) + 1,
                    file_path=self._file_path,
                    line=tok.line,
                    column=tok.column,
                    message=f"Лишние символы после оператора: '{tok.value}'",
                )
            )

    def _parse_condition(self) -> bool:
        # <Condition> -> <Condition> "or" <Condition> | <Condition> "and" <Condition> | <ident>
        if not self._parse_primary_condition():
            return False

        while self._current_token().type in (TokenType.KEYWORD_AND, TokenType.KEYWORD_OR):
            self._cursor += 1
            if not self._parse_primary_condition():
                return False

        return True

    def _parse_primary_condition(self) -> bool:
        tok = self._current_token()
        if tok.type == TokenType.LPAREN:
            self._cursor += 1
            if not self._parse_condition():
                return False
            return self._expect(TokenType.RPAREN, "')' закрывающая скобка условия")

        if tok.type == TokenType.IDENTIFIER:
            self._cursor += 1
            return True

        self._errors.append(
            ErrorRecord(
                index=len(self._errors) + 1,
                file_path=self._file_path,
                line=tok.line,
                column=tok.column,
                message=f"Ожидался идентификатор в условии, получено: '{tok.value}'",
            )
        )
        return False

    def _parse_assignment(self) -> bool:
        # <Assignment> -> <ident> '=' <ident>
        if not self._expect(TokenType.IDENTIFIER, "идентификатор слева от '='"):
            return False

        if not self._expect(TokenType.ASSIGN, "'=' в присваивании"):
            return False

        if not self._expect(TokenType.IDENTIFIER, "идентификатор справа от '='"):
            return False

        return True
