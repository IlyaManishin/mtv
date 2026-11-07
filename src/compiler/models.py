from dataclasses import dataclass

from src.compiler.token import Token


@dataclass(frozen=True)
class ErrorRecord:
    index: int
    file_path: str
    line: int
    column: int
    message: str


@dataclass(frozen=True)
class AnalysisResult:
    is_valid: bool
    log_messages: list[str]
    errors: list[ErrorRecord]
    tokens: list[Token]
