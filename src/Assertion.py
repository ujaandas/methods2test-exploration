from typing import Any, List, Optional


class Assertion:
    def __init__(
        self,
        method_name: str,
        expected: Optional[Any] = None,
        actual: Optional[Any] = None,
        arguments: Optional[List[Any]] = None,
        line_number: Optional[int] = None,
    ):
        self.method_name = method_name
        self.expected = expected
        self.actual = actual
        self.arguments = arguments if arguments else []
        self.line_number = line_number

    def __repr__(self) -> str:
        return (
            f"Assertion(method_name={self.method_name}, expected={self.expected}, "
            f"actual={self.actual}, arguments={self.arguments}, "
            f"line_number={self.line_number})"
        )


class SequencedAssertion(Assertion):
    def __init__(
        self,
        method_name,
        expected=None,
        actual=None,
        arguments=None,
        line_number=None,
        method_sequence=None,
    ):
        super().__init__(method_name, expected, actual, arguments, line_number)
        self.method_sequence = method_sequence if method_sequence else []

    def __repr__(self):
        return (
            f"AssertionWithSequence(method_name={self.method_name}, "
            f"expected={self.expected}, actual={self.actual}, "
            f"method_sequence={self.method_sequence}, "
            f"line_number={self.line_number})"
        )
