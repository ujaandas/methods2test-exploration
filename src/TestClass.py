from typing import List
from javalang.tree import ClassDeclaration
from TestMethod import TestMethod


class TestClass:
    def __init__(self, parsed_class: ClassDeclaration):
        self.name: str = parsed_class.name
        self.test_methods: List[TestMethod] = [
            TestMethod(method) for method in self.parsed_class.methods
        ]

    def __repr__(self) -> str:
        return f"TestClass(name={self.name}, test_methods={self.test_methods})"
