from typing import List
from javalang.tree import MethodDeclaration, MethodInvocation
from Assertion import Assertion


class TestMethod:
    def __init__(self, parsed_method: MethodDeclaration):
        self.name: str = parsed_method.name
        self.line_number: int = (
            parsed_method.position.line if parsed_method.position else -1
        )
        self.assertions: List[Assertion] = []
        self._extract_assertions(parsed_method)

    def _extract_assertions(self, parsed_method: MethodDeclaration) -> None:
        for _, invocation_node in parsed_method.filter(MethodInvocation):
            if invocation_node.member.startswith("assertEquals"):
                assertion = Assertion(
                    method_name=invocation_node.member,
                    expected=invocation_node.arguments[0]
                    if len(invocation_node.arguments) > 0
                    else None,
                    actual=invocation_node.arguments[1]
                    if len(invocation_node.arguments) > 1
                    else None,
                    arguments=invocation_node.arguments,
                    line_number=invocation_node.position.line
                    if invocation_node.position
                    else -1,
                )
                self.assertions.append(assertion)

    def __repr__(self) -> str:
        return f"TestMethod(name={self.name}, line_number={self.line_number}, assertions={self.assertions}"
