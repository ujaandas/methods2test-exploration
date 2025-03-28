from typing import Any, List, Optional
from javalang.parse import parse_expression
from javalang.tree import MethodInvocation, MemberReference


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

    def __repr__(self):
        return f"Assertion(method_name={self.method_name}, expected={self.expected}, actual={self.actual}, arguments={self.arguments}, line_number={self.line_number})"

    def transform(self, SubClass: type):
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
        self, method_name, expected=None, actual=None, arguments=None, line_number=None
    ):
        super().__init__(method_name, expected, actual, arguments, line_number)
        self.method_sequence = self._extract_method_seq(self.arguments)
        if self.method_sequence is not None:
            self.method_sequence = self._nest_method_chain(self.method_sequence)
            self.actual = self._unparse_method_chain(self.method_sequence)

    def flatten(self):
        if self.method_sequence:
            return self._flatten_node(self.method_sequence)
        return []

    def __repr__(self):
        flattened = self.flatten()
        return f"SequencedAssertion(method_name={self.method_name}, expected={self.expected}, actual={self.actual}, method_sequence={flattened}, line_number={self.line_number})"

    def _extract_method_seq(self, args: List[Any]):
        for arg in args:
            if isinstance(arg, str):
                try:
                    expr = parse_expression(arg)
                    if isinstance(expr, (MethodInvocation, MemberReference)):
                        return expr
                except Exception:
                    continue
        return None

    def _nest_method_chain(self, node):
        if isinstance(node, MethodInvocation):
            if node.selectors and len(node.selectors) > 1:
                nested = node.selectors[-1]
                for sel in reversed(node.selectors[:-1]):
                    sel = self._nest_method_chain(sel)
                    nested = MethodInvocation(
                        member=sel.member,
                        arguments=sel.arguments,
                        qualifier=sel.qualifier,
                        selectors=[nested],
                    )
                node.selectors = [nested]
            elif node.selectors and len(node.selectors) == 1:
                node.selectors[0] = self._nest_method_chain(node.selectors[0])
            if node.qualifier and isinstance(
                node.qualifier, (MethodInvocation, MemberReference)
            ):
                node.qualifier = self._nest_method_chain(node.qualifier)
            return node
        elif isinstance(node, MemberReference):
            return node
        return node

    def _flatten_node(self, node):
        chain = []
        if isinstance(node, MethodInvocation):
            if node.qualifier and isinstance(
                node.qualifier, (MethodInvocation, MemberReference)
            ):
                chain.extend(self._flatten_node(node.qualifier))
            chain.append(node)
        elif isinstance(node, MemberReference):
            chain.append(node)
        return chain

    def _unparse_method_chain(self, node):
        if isinstance(node, MethodInvocation):
            qualifier_str = ""
            if node.qualifier:
                if isinstance(node.qualifier, (MethodInvocation, MemberReference)):
                    qualifier_str = self._unparse_method_chain(node.qualifier)
                else:
                    qualifier_str = str(node.qualifier)
            args_str = "(" + ", ".join(str(arg) for arg in node.arguments) + ")"
            selectors_str = ""
            if hasattr(node, "selectors") and node.selectors:
                for sel in node.selectors:
                    if isinstance(sel, MethodInvocation):
                        selectors_str += "." + self._unparse_method_chain(sel)
                    elif isinstance(sel, MemberReference):
                        selectors_str += "." + sel.member
                    else:
                        selectors_str += "." + str(sel)
            if qualifier_str:
                return f"{qualifier_str}.{node.member}{args_str}{selectors_str}"
            else:
                return f"{node.member}{args_str}{selectors_str}"
        elif isinstance(node, MemberReference):
            return node.member
        else:
            return str(node)
