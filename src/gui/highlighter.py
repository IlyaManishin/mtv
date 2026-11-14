from typing import NamedTuple

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument


class HighlightingRule(NamedTuple):
    pattern: QRegularExpression
    format: QTextCharFormat


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)
        self._rules: list[HighlightingRule] = []
        self._setup_rules()

    def _setup_rules(self) -> None:
        # Keywords: if, else, and, or
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["\\bif\\b", "\\belse\\b", "\\band\\b", "\\bor\\b"]
        for kw in keywords:
            self._rules.append(HighlightingRule(QRegularExpression(kw), keyword_format))


        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#098658"))
        self._rules.append(HighlightingRule(QRegularExpression("\\b[0-9]+(\\.[0-9]+)?\\b"), number_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A31515"))
        self._rules.append(HighlightingRule(QRegularExpression("\".*?\""), string_format))
        self._rules.append(HighlightingRule(QRegularExpression("'.*?'"), string_format))

        # Operators and punctuation
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#795E26"))
        self._rules.append(HighlightingRule(QRegularExpression(r"(<=|>=|==|!=|[-:=+*/()<>]|!)"), operator_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))
        comment_format.setFontItalic(True)
        self._rules.append(HighlightingRule(QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text: str) -> None:
        for rule in self._rules:
            match_iterator = rule.pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)
