from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    KEYWORD_IF = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_AND = auto()
    KEYWORD_OR = auto()
    TERM_NEWLINE = auto()
    TERM_INDENT = auto()
    TERM_DEDENT = auto()
    COLON = auto()
    ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    IDENTIFIER = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    position: int
    length: int
