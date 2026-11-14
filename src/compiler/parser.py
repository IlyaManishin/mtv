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

        # Check for empty token stream (only EOF)
        if len(self._tokens) <= 1:
            self._log.append("Предупреждение: Входной поток токенов пуст.")
            return AnalysisResult(
                is_valid=False,
                log_messages=self._log,
                errors=[],
                tokens=self._tokens,
            )

        self._log.append(f"Запуск синтаксического анализатора (токенов: {len(self._tokens) - 1}).")

        # Parse statements until EOF using panic-mode recovery
        while self._current_token().type != TokenType.EOF:
            initial_cursor = self._cursor
            self._parse_statement()

            # Prevent potential infinite loops if a rule fails to advance cursor
            if self._cursor == initial_cursor:
                tok = self._current_token()
                if tok.type != TokenType.EOF:
                    self._record_error(
                        tok,
                        f"Неожиданный токен вне оператора: '{tok.value}'. Пропуск токена.",
                    )
                    self._cursor += 1

        if self._errors:
            self._log.append(
                f"Синтаксический анализ завершен с ошибками: обнаружено {len(self._errors)} шт."
            )
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

    def _advance(self) -> Token:
        tok = self._current_token()
        if self._cursor < len(self._tokens):
            self._cursor += 1
        return tok

    @staticmethod
    def _format_tok(tok: Token) -> str:
        if tok.type == TokenType.EOF:
            return "конец файла"
        if tok.type == TokenType.TERM_NEWLINE:
            return "перевод строки"
        if tok.type == TokenType.TERM_INDENT:
            return "отступ"
        if tok.type == TokenType.TERM_DEDENT:
            return "возврат отступа"
        return f"'{tok.value}'"

    def _record_error(self, tok: Token, message: str) -> None:
        self._errors.append(
            ErrorRecord(
                index=len(self._errors) + 1,
                file_path=self._file_path,
                line=tok.line,
                column=tok.column,
                message=message,
            )
        )

    def _skip_until(self, sync_types: set[TokenType]) -> None:
        # Panic mode: consume tokens until a synchronizing token or EOF is found
        while self._current_token().type not in sync_types and self._current_token().type != TokenType.EOF:
            self._cursor += 1

    def _parse_statement(self) -> None:
        # Expected grammar:
        # <IfStmt> -> 'if' <Condition> ':' 'NEWLINE' 'INDENT' <Assignment> 'NEWLINE' 'DEDENT'
        #             'else' ':' 'NEWLINE' 'INDENT' <Assignment> 'NEWLINE' 'DEDENT'

        # 1. 'if'
        if self._current_token().type == TokenType.KEYWORD_IF:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(
                tok,
                f"Ожидалось ключевое слово 'if' в начале условного оператора, получено {self._format_tok(tok)}",
            )
            self._skip_until({TokenType.KEYWORD_IF, TokenType.KEYWORD_ELSE, TokenType.EOF})
            if self._current_token().type != TokenType.KEYWORD_IF:
                return
            self._advance()

        # 2. <Condition>
        self._parse_condition()

        # 3. ':' after condition
        if self._current_token().type == TokenType.COLON:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Пропущено двоеточие ':' после условия")
            if self._current_token().type not in (TokenType.TERM_NEWLINE, TokenType.TERM_INDENT):
                self._skip_until({TokenType.TERM_NEWLINE, TokenType.TERM_INDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})

        # 4. 'NEWLINE' after 'if:'
        if self._current_token().type == TokenType.TERM_NEWLINE:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался перевод строки после заголовка 'if:'")
            if self._current_token().type != TokenType.TERM_INDENT:
                self._skip_until({TokenType.TERM_INDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})

        # 5. 'INDENT' before 'if' body
        if self._current_token().type == TokenType.TERM_INDENT:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался отступ (блок команд) после 'if:'")

        # 6. <Assignment> in 'if' branch
        self._parse_assignment(context="в блоке 'if'")

        # 7. 'NEWLINE' after assignment in 'if'
        if self._current_token().type == TokenType.TERM_NEWLINE:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался перевод строки после выражения в блоке 'if'")
            if self._current_token().type not in (TokenType.TERM_DEDENT, TokenType.KEYWORD_ELSE):
                self._skip_until({TokenType.TERM_DEDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})

        # 8. 'DEDENT' ending 'if' block
        if self._current_token().type == TokenType.TERM_DEDENT:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался возврат отступа (конец блока 'if')")
            if self._current_token().type != TokenType.KEYWORD_ELSE:
                self._skip_until({TokenType.KEYWORD_ELSE, TokenType.EOF})

        # 9. 'else'
        if self._current_token().type == TokenType.KEYWORD_ELSE:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, f"Ожидалась ветка 'else:', получено {self._format_tok(tok)}")
            if self._current_token().type not in (TokenType.COLON, TokenType.TERM_NEWLINE, TokenType.TERM_INDENT):
                self._skip_until({TokenType.KEYWORD_IF, TokenType.EOF})
                return

        # 10. ':' after 'else'
        if self._current_token().type == TokenType.COLON:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Пропущено двоеточие ':' после 'else'")
            if self._current_token().type not in (TokenType.TERM_NEWLINE, TokenType.TERM_INDENT):
                self._skip_until({TokenType.TERM_NEWLINE, TokenType.TERM_INDENT, TokenType.EOF})

        # 11. 'NEWLINE' after 'else:'
        if self._current_token().type == TokenType.TERM_NEWLINE:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался перевод строки после 'else:'")
            if self._current_token().type != TokenType.TERM_INDENT:
                self._skip_until({TokenType.TERM_INDENT, TokenType.EOF})

        # 12. 'INDENT' before 'else' body
        if self._current_token().type == TokenType.TERM_INDENT:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался отступ (блок команд) после 'else:'")

        # 13. <Assignment> in 'else' branch
        self._parse_assignment(context="в блоке 'else'")

        # 14. 'NEWLINE' after assignment in 'else'
        if self._current_token().type == TokenType.TERM_NEWLINE:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался перевод строки после выражения в блоке 'else'")
            if self._current_token().type != TokenType.TERM_DEDENT:
                self._skip_until({TokenType.TERM_DEDENT, TokenType.EOF})

        # 15. 'DEDENT' ending 'else' block
        if self._current_token().type == TokenType.TERM_DEDENT:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, "Ожидался возврат отступа (конец блока 'else')")

    def _parse_condition(self) -> None:
        # <Condition> -> <Condition> "or" <Condition> | <Condition> "and" <Condition> | <ident>
        tok = self._current_token()
        if tok.type in (TokenType.COLON, TokenType.TERM_NEWLINE, TokenType.TERM_INDENT, TokenType.EOF):
            self._record_error(tok, "Ожидалось логическое условие после 'if'")
            return

        self._parse_primary_condition()

        while self._current_token().type in (TokenType.KEYWORD_AND, TokenType.KEYWORD_OR):
            op_tok = self._advance()
            next_tok = self._current_token()
            if next_tok.type in (TokenType.COLON, TokenType.TERM_NEWLINE, TokenType.EOF):
                self._record_error(next_tok, f"Ожидался операнд после логического оператора '{op_tok.value}'")
                break
            self._parse_primary_condition()

    COMPARISON_OPS = (
        TokenType.OP_LT,
        TokenType.OP_GT,
        TokenType.OP_LE,
        TokenType.OP_GE,
        TokenType.OP_EQ,
        TokenType.OP_NE,
    )

    def _parse_primary_condition(self) -> None:
        tok = self._current_token()
        if tok.type == TokenType.LPAREN:
            self._advance()
            self._parse_condition()
            if self._current_token().type == TokenType.RPAREN:
                self._advance()
            else:
                self._record_error(self._current_token(), "Ожидалась закрывающая скобка ')' в условии")
        elif tok.type in self.COMPARISON_OPS:
            op_tok = self._advance()
            self._record_error(op_tok, f"Пропущен левый операнд перед оператором сравнения '{op_tok.value}'")
            if self._current_token().type == TokenType.IDENTIFIER:
                self._advance()
        elif tok.type == TokenType.IDENTIFIER:
            self._advance()
            # Check for comparison operator: <ident> <Op> <ident>
            if self._current_token().type in self.COMPARISON_OPS:
                op_tok = self._advance()
                right_tok = self._current_token()
                if right_tok.type == TokenType.IDENTIFIER:
                    self._advance()
                else:
                    self._record_error(
                        right_tok,
                        f"Ожидался идентификатор справа от оператора сравнения '{op_tok.value}', получено {self._format_tok(right_tok)}",
                    )
        else:
            self._record_error(
                tok,
                f"Некорректное условие: ожидался идентификатор, получено {self._format_tok(tok)}",
            )
            self._skip_until({TokenType.COLON, TokenType.KEYWORD_AND, TokenType.KEYWORD_OR, TokenType.TERM_NEWLINE, TokenType.EOF})

    def _parse_assignment(self, context: str) -> None:
        # <Assignment> -> <ident> '=' <ident>
        # Left side identifier
        tok = self._current_token()
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
        elif tok.type == TokenType.ASSIGN:
            self._record_error(tok, f"Пропущен идентификатор слева от '=' {context}")
        else:
            self._record_error(
                tok,
                f"Ожидался идентификатор слева от '=' {context}, получено {self._format_tok(tok)}",
            )
            if self._current_token().type != TokenType.ASSIGN:
                self._skip_until({TokenType.ASSIGN, TokenType.TERM_NEWLINE, TokenType.TERM_DEDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})

        # Equals sign '='
        if self._current_token().type == TokenType.ASSIGN:
            self._advance()
        else:
            tok = self._current_token()
            self._record_error(tok, f"Ожидался знак '=' в присваивании {context}, получено {self._format_tok(tok)}")
            if self._current_token().type != TokenType.IDENTIFIER:
                self._skip_until({TokenType.IDENTIFIER, TokenType.TERM_NEWLINE, TokenType.TERM_DEDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})

        # Right side identifier
        tok = self._current_token()
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
        else:
            self._record_error(
                tok,
                f"Ожидался идентификатор справа от '=' {context}, получено {self._format_tok(tok)}",
            )
            self._skip_until({TokenType.TERM_NEWLINE, TokenType.TERM_DEDENT, TokenType.KEYWORD_ELSE, TokenType.EOF})
