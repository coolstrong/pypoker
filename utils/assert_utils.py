
from typing import TypeVar


T = TypeVar("T")

def assert_expr(value: T | None, message: str | None = None) -> T:
    assert value, message
    return value