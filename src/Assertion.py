from typing import Any, List, Optional
from javalang.tree import MethodInvocation


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
        self.chains = []
        self.max_depth = 0

        if expected:
            chain, depth = self._extract_chain(expected)
            if chain and depth > 0 and chain not in self.chains:
                self.chains.extend(chain)
                self.max_depth = max(self.max_depth, depth)

        if actual:
            chain, depth = self._extract_chain(actual)
            if chain and depth > 0 and chain not in self.chains:
                self.chains.extend(chain)
                self.max_depth = max(self.max_depth, depth)

        if arguments:
            for arg in arguments:
                chain, depth = self._extract_chain(arg)
                if chain and depth > 0 and chain not in self.chains:
                    self.chains.extend(chain)
                    self.max_depth = max(self.max_depth, depth)

        self.args = self._extract_args()

    def _extract_chain(self, element):
        if not element:
            return [], 0

        if isinstance(element, MethodInvocation):
            chain = []
            depth = 0

            current = element
            while isinstance(current, MethodInvocation):
                chain.append(current)
                depth += 1

                if hasattr(current, "qualifier") and isinstance(
                    current.qualifier, MethodInvocation
                ):
                    current = current.qualifier
                else:
                    break

            if hasattr(element, "selectors") and element.selectors:
                for selector in element.selectors:
                    if isinstance(selector, MethodInvocation):
                        sub_chain, sub_depth = self._extract_chain(selector)
                        chain.extend(sub_chain)
                        depth += sub_depth

            return chain, depth

        return [], 0

    def _extract_args(self):
        chain_args = []
        for method_invocation in self.chains:
            if isinstance(method_invocation, MethodInvocation):
                flat_args = []
                if method_invocation.arguments:
                    for arg in method_invocation.arguments:
                        if hasattr(arg, "value"):
                            tokens = [
                                token.strip() for token in str(arg.value).split(",")
                            ]
                            flat_args.extend(tokens)
                        elif hasattr(arg, "member"):
                            flat_args.append(str(arg.member).strip())
                        else:
                            flat_args.append(str(arg).strip())
                if (flat_args, len(flat_args)) not in chain_args and len(flat_args) > 0:
                    chain_args.append((flat_args, len(flat_args)))
        return chain_args

    def __repr__(self):
        base_repr = super().__repr__()[:-1]
        return f"{base_repr}, chains={self.chains}, max_depth={self.max_depth})"
