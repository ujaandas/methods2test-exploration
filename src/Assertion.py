from typing import Any, List, Optional
from javalang.tree import MethodInvocation, MemberReference
from javalang.parse import parse_expression


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

    def transform(self, SubClass: type):
        # get special type of assertion that is child to Assertion (ie; sequenced assertion)
        if not issubclass(SubClass, Assertion):
            print(f"{SubClass} is not a subclass of Assertion")
            return None

        return SubClass(
            self.method_name,
            self.expected,
            self.actual,
            self.arguments,
            self.line_number,
        )


class SequencedAssertion(Assertion):
    def __init__(
        self,
        method_name,
        expected=None,
        actual=None,
        arguments=None,
        line_number=None,
    ):
        super().__init__(method_name, expected, actual, arguments, line_number)
        self.method_sequence = extract_method_seq(self.arguments)

    def flatten(self):
        if self.method_sequence:
            return flatten_node(self.method_sequence)
        return []

    def __repr__(self):
        flattened = self.flatten()
        return (
            f"SequencedAssertion(method_name={self.method_name}, expected={self.expected}, "
            f"actual={self.actual}, method_sequence={flattened}, "
            f"line_number={self.line_number})"
        )


def flatten_node(node):
    chain = []
    if isinstance(node, MethodInvocation):
        if node.qualifier and isinstance(
            node.qualifier, (MethodInvocation, MemberReference)
        ):
            chain.extend(flatten_node(node.qualifier))
        chain.append(node)
    elif isinstance(node, MemberReference):
        chain.append(node)
    return chain


def extract_method_seq(args: List):
    for arg in args:
        if isinstance(arg, str):
            try:
                expr = parse_expression(arg)
                if isinstance(expr, (MethodInvocation, MemberReference)):
                    return expr
            except Exception:
                continue
    return None
