from typing import List
from javalang.tree import MethodDeclaration, MethodInvocation
from Assertion import Assertion
import javalang


def build_symbol_table(method_decl: MethodDeclaration) -> dict:
    sym = {}
    for _, node in method_decl.filter(javalang.tree.LocalVariableDeclaration):
        typename = node.type.name
        for decl in node.declarators:
            sym[decl.name] = typename
    return sym


class TestMethod:
    def __init__(self, parsed_method: MethodDeclaration):
        self.name: str = parsed_method.name
        self.line_number: int = (
            parsed_method.position.line if parsed_method.position else -1
        )
        self.assertions: List[Assertion] = []
        self._extract_assertions(parsed_method)
        self.symbol_table = build_symbol_table(parsed_method)

    def _extract_assertions(self, parsed_method: MethodDeclaration) -> None:
        for _, invocation_node in parsed_method.filter(MethodInvocation):
            if invocation_node.member.startswith("assert"):
                assertion = Assertion.from_invocation(invocation_node)
                if assertion:
                    self.assertions.append(assertion)

    def collect_std_lib_dependencies(self, imports: List[str]) -> None:
        for assertion in self.assertions:
            # print(self.symbol_table)
            assertion.collect_std_lib_dep(self.symbol_table)

    def __repr__(self) -> str:
        return f"TestMethod(name={self.name}, line_number={self.line_number}, assertions={self.assertions})"
