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
            if invocation_node.member.startswith("assert"):
                assertion = Assertion.from_invocation(invocation_node)
                if assertion:
                    self.assertions.append(assertion)

    def __repr__(self) -> str:
        return f"TestMethod(name={self.name}, line_number={self.line_number}, assertions={self.assertions}"
