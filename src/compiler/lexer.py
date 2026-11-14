import re
from typing import Final

from src.compiler.models import ErrorRecord
from src.compiler.token import Token, TokenType


class Lexer:
    # Token specification pairs: (TokenType, Regex)
    _RULES: Final[list[tuple[TokenType, str]]] = [
        (TokenType.KEYWORD_IF, r"\bif\b"),
        (TokenType.KEYWORD_ELSE, r"\belse\b"),
        (TokenType.KEYWORD_AND, r"\band\b"),
        (TokenType.KEYWORD_OR, r"\bor\b"),
        (TokenType.COLON, r":"),
        (TokenType.OP_LE, r"<="),
        (TokenType.OP_GE, r">="),
        (TokenType.OP_EQ, r"=="),
        (TokenType.OP_NE, r"!="),
        (TokenType.OP_LT, r"<"),
        (TokenType.OP_GT, r">"),
        (TokenType.ASSIGN, r"="),
        (TokenType.LPAREN, r"\("),
        (TokenType.RPAREN, r"\)"),
        # Support literal keyword representations if written explicitly
        (TokenType.TERM_NEWLINE, r"\bNEWLINE\b"),
        (TokenType.TERM_INDENT, r"\bINDENT\b"),
        (TokenType.TERM_DEDENT, r"\bDEDENT\b"),
        (TokenType.IDENTIFIER, r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ]

    def __init__(self, source_code: str, file_path: str = "untitled") -> None:
        self._source: str = source_code
        self._file_path: str = file_path
        self._tokens: list[Token] = []
        self._errors: list[ErrorRecord] = []

    def tokenize(self) -> tuple[list[Token], list[ErrorRecord]]:
        self._tokens.clear()
        self._errors.clear()

        # Check if code uses real indentation/newlines or single-line literal words
        if "\n" in self._source:
            self._tokenize_python_indentation()
        else:
            self._tokenize_inline()

        return self._tokens, self._errors

    def _tokenize_python_indentation(self) -> None:
        indent_stack: list[int] = [0]
        raw_lines = self._source.splitlines(keepends=True)
        char_pos = 0

        for line_idx, raw_line in enumerate(raw_lines, start=1):
            line_len = len(raw_line)
            line_stripped = raw_line.rstrip("\r\n")

            # Check for empty or comment-only line
            if not line_stripped.strip() or line_stripped.lstrip().startswith("#"):
                char_pos += line_len
                continue

            # Calculate indentation (expand tab to 4 spaces)
            expanded_indent = 0
            leading_len = 0
            for ch in line_stripped:
                if ch == " ":
                    expanded_indent += 1
                    leading_len += 1
                elif ch == "\t":
                    expanded_indent += 4
                    leading_len += 1
                else:
                    break

            # Indentation level transitions
            current_level = indent_stack[-1]
            if expanded_indent > current_level:
                indent_stack.append(expanded_indent)
                self._tokens.append(
                    Token(
                        type=TokenType.TERM_INDENT,
                        value=" " * expanded_indent,
                        line=line_idx,
                        column=1,
                        position=char_pos,
                        length=leading_len,
                    )
                )
            elif expanded_indent < current_level:
                while indent_stack and expanded_indent < indent_stack[-1]:
                    indent_stack.pop()
                    self._tokens.append(
                        Token(
                            type=TokenType.TERM_DEDENT,
                            value="",
                            line=line_idx,
                            column=1,
                            position=char_pos,
                            length=0,
                        )
                    )
                if not indent_stack or indent_stack[-1] != expanded_indent:
                    self._errors.append(
                        ErrorRecord(
                            index=len(self._errors) + 1,
                            file_path=self._file_path,
                            line=line_idx,
                            column=1,
                            message=f"Ошибка отступа: несоответствие внешнему уровню ({expanded_indent} пробелов)",
                        )
                    )

            # Tokenize line content after leading indentation
            col = leading_len + 1
            line_pos = leading_len
            line_tokens_count = 0

            while line_pos < len(line_stripped):
                ch = line_stripped[line_pos]

                if ch in (" ", "\t"):
                    line_pos += 1
                    col += 1
                    continue

                if ch == "#":
                    # Comment rest of line
                    break

                matched = False
                for token_type, pattern in self._RULES:
                    regex = re.compile(pattern)
                    match = regex.match(line_stripped, line_pos)
                    if match:
                        val = match.group(0)
                        val_len = len(val)
                        self._tokens.append(
                            Token(
                                type=token_type,
                                value=val,
                                line=line_idx,
                                column=col,
                                position=char_pos + line_pos,
                                length=val_len,
                            )
                        )
                        line_pos += val_len
                        col += val_len
                        line_tokens_count += 1
                        matched = True
                        break

                if not matched:
                    self._errors.append(
                        ErrorRecord(
                            index=len(self._errors) + 1,
                            file_path=self._file_path,
                            line=line_idx,
                            column=col,
                            message=f"Недопустимый символ: '{ch}'",
                        )
                    )
                    line_pos += 1
                    col += 1

            if line_tokens_count > 0:
                self._tokens.append(
                    Token(
                        type=TokenType.TERM_NEWLINE,
                        value="\n",
                        line=line_idx,
                        column=len(line_stripped) + 1,
                        position=char_pos + len(line_stripped),
                        length=1,
                    )
                )

            char_pos += line_len

        # Emit remaining DEDENT tokens at EOF
        last_line = len(raw_lines)
        last_col = len(raw_lines[-1]) + 1 if raw_lines else 1
        while len(indent_stack) > 1:
            indent_stack.pop()
            self._tokens.append(
                Token(
                    type=TokenType.TERM_DEDENT,
                    value="",
                    line=last_line,
                    column=last_col,
                    position=char_pos,
                    length=0,
                )
            )

        # Emit EOF
        self._tokens.append(
            Token(
                type=TokenType.EOF,
                value="",
                line=last_line,
                column=last_col,
                position=char_pos,
                length=0,
            )
        )

    def _tokenize_inline(self) -> None:
        pos = 0
        length = len(self._source)
        line = 1
        col = 1

        while pos < length:
            char = self._source[pos]

            if char in (" ", "\t", "\r"):
                pos += 1
                col += 1
                continue

            matched = False
            for token_type, pattern in self._RULES:
                regex = re.compile(pattern)
                match = regex.match(self._source, pos)
                if match:
                    val = match.group(0)
                    val_len = len(val)
                    self._tokens.append(
                        Token(
                            type=token_type,
                            value=val,
                            line=line,
                            column=col,
                            position=pos,
                            length=val_len,
                        )
                    )
                    pos += val_len
                    col += val_len
                    matched = True
                    break

            if not matched:
                self._errors.append(
                    ErrorRecord(
                        index=len(self._errors) + 1,
                        file_path=self._file_path,
                        line=line,
                        column=col,
                        message=f"Недопустимый символ: '{char}'",
                    )
                )
                pos += 1
                col += 1

        self._tokens.append(
            Token(
                type=TokenType.EOF,
                value="",
                line=line,
                column=col,
                position=pos,
                length=0,
            )
        )
