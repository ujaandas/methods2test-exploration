from typing import Any, Dict, Optional, List
from javalang.tree import MethodInvocation, MemberReference


class Dependency:
    def __init__(
        self,
        variable_name: str,
        type_name: str,
        qualified_name: str = "",
        is_imported: bool = False,
    ):
        self.variable_name = variable_name
        self.type_name = type_name
        self.qualified_name = qualified_name
        self.is_imported = is_imported

    def __repr__(self):
        return f"Dependency(variable_name={self.variable_name!r}, type_name={self.type_name!r}, qualified_name={self.qualified_name!r}, is_imported={self.is_imported})"


# based on https://junit.org/junit4/javadoc/4.13/org/junit/Assert.html

assertion_signatures: Dict[str, Dict[int, list]] = {
    "assertTrue": {
        1: ["condition"],
        2: ["message", "condition"],
    },
    "assertFalse": {
        1: ["condition"],
        2: ["message", "condition"],
    },
    "assertEquals": {
        2: ["expected", "actual"],
        3: ["message", "expected", "actual"],
    },
    "assertNotEquals": {
        2: ["unexpected", "actual"],
        3: ["message", "unexpected", "actual"],
    },
    "assertArrayEquals": {
        2: ["expected", "actual"],
        3: ["message", "expected", "actual"],
    },
    "assertNull": {
        1: ["object"],
        2: ["message", "object"],
    },
    "assertNotNull": {
        1: ["object"],
        2: ["message", "object"],
    },
    "assertSame": {
        2: ["expected", "actual"],
        3: ["message", "expected", "actual"],
    },
    "assertNotSame": {
        2: ["unexpected", "actual"],
        3: ["message", "unexpected", "actual"],
    },
    # "fail": {
    #     0: [],
    #     1: ["message"],
    # },
    "assertThrows": {
        2: ["expected_exception", "runnable"],
        3: ["message", "expected_exception", "runnable"],
    },
    "assertThat": {
        2: ["actual", "matcher"],
        3: ["message", "actual", "matcher"],
    },
}


class Assertion:
    def __init__(
        self,
        method_name: str,
        line_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.method_name = method_name
        self.line_number = line_number
        self.details = details if details is not None else {}
        self.arguments: List[Any] = []

        for key, value in self.details.items():
            self._extract_arguments(value)

        # self.dependencies: List[Dependency] = []
        self.std_lib_dependencies: List[Dependency] = []

        self.variable_count = sum(
            1 for arg in self.arguments if isinstance(arg, MemberReference)
        )

    def __repr__(self):
        details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"Assertion(method_name={self.method_name}, line_number={self.line_number}, {details_str})"

    @classmethod
    def from_invocation(cls, invocation: MethodInvocation) -> "Assertion":
        method_name = invocation.member
        args = invocation.arguments if invocation.arguments else []
        line_number = invocation.position.line if invocation.position else None

        signatures = assertion_signatures.get(method_name)
        if signatures is None:
            print(f"Unknown assertion method: {method_name}")
            return None

        expected_fields = signatures.get(len(args))
        if expected_fields is None:
            print(f"Unexpected number of arguments for {method_name}: {len(args)}")
            return None

        details = dict(zip(expected_fields, args))
        return cls(method_name, line_number, details)

    def _extract_arguments(self, element: Any):
        if isinstance(element, MethodInvocation):
            if element.arguments:
                self.arguments.extend(element.arguments)

                for arg in element.arguments:
                    self._extract_arguments(arg)

            if element.qualifier:
                self._extract_arguments(element.qualifier)

            if element.selectors:
                for selector in element.selectors:
                    self._extract_arguments(selector)

        elif isinstance(element, list):
            for item in element:
                self._extract_arguments(item)

    def _calculate_length(self, method: MethodInvocation) -> int:
        if not isinstance(method, MethodInvocation):
            return 0

        length = 1

        if method.qualifier:
            length += self._calculate_length(method.qualifier)

        if method.selectors:
            length += sum(
                self._calculate_length(selector) for selector in method.selectors
            )

        return length

    def _calculate_depth(self, element: Any) -> int:
        if isinstance(element, MethodInvocation):
            depth = 1

            if element.arguments:
                argument_depths = [
                    self._calculate_depth(arg) for arg in element.arguments
                ]
                depth += max(argument_depths, default=0)

            if element.qualifier:
                depth = max(depth, self._calculate_depth(element.qualifier))

            if element.selectors:
                selector_depths = [
                    self._calculate_depth(selector) for selector in element.selectors
                ]
                depth = max(depth, max(selector_depths, default=0))

            return depth

        elif isinstance(element, list):
            return max((self._calculate_depth(item) for item in element), default=0)

        else:
            return 0

    def get_length(self) -> int:
        max_length = 0
        for value in self.details.values():
            if isinstance(value, MethodInvocation):
                length = self._calculate_length(value)
                max_length = max(max_length, length)
        return max_length

    def get_depth(self) -> int:
        max_depth = 0
        for value in self.details.values():
            depth = self._calculate_depth(value)
            max_depth = max(max_depth, depth)
        return max_depth
