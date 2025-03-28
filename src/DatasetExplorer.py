import json
from pathlib import Path
from TestClass import TestClass
from javalang.parse import parse
from javalang.tree import ClassDeclaration
from Assertion import SequencedAssertion
# from Repository import Repository, SubRepository, Pair
# from typing import List


class DatasetExplorer:
    def __init__(self, dataset_dir: str):
        self.dataset_dir: Path = Path(dataset_dir)
        # self.repositories: List[Repository] = []

    def _transform_filename(self, num: int, base: str) -> str:
        s = str(num)
        base_length = len(base)
        if not s.startswith(base):
            raise ValueError(f"The number {num} does not start with the base {base}")
        suffix = s[base_length:]
        return f"{base}_{suffix}"

    def step(self):
        subdir_names = sorted(
            [int(x.stem) for x in self.dataset_dir.iterdir() if x.is_dir()]
        )
        for sd in subdir_names:
            base_str = str(sd)
            this_repo_sd = self.dataset_dir / base_str
            print(f"Processing directory: {this_repo_sd}")

            this_repo_files = [
                this_repo_sd / f"{self._transform_filename(x, base_str)}.json"
                for x in sorted(
                    [int(path.stem) for path in this_repo_sd.glob("*.json")]
                )
            ]

            # with open(this_repo_files[0]) as f:
            #     first_file = json.loads(f.read())
            # this_repo_url = first_file.get("repository").get("url")

            for file in this_repo_files:
                with open(file, "r") as f:
                    data = json.load(f)

                test_class_data = data.get("test_class", {})
                test_case_data = data.get("test_case", {})

                class_name = test_class_data.get("identifier", "DummyClass")

                fields_list = test_class_data.get("fields", [])
                fields_str = "\n    ".join(
                    field.get("original_string", "") for field in fields_list
                )

                method_str = test_case_data.get("body", "")

                java_class_code = (
                    f"public class {class_name} {{\n"
                    f"    {fields_str}\n\n"
                    f"    {method_str}\n"
                    f"}}"
                )

                print("----- Reconstructed Java Class -----")
                print(java_class_code)
                print("--------------------------------------\n")

                try:
                    parsed_tree = parse(java_class_code)

                    # print("----- Parsed Tree -----")
                    # print(parsed_tree)
                    # print("-----------------------\n")

                    test_classes = []
                    for _, class_node in parsed_tree.filter(ClassDeclaration):
                        test_classes.append(TestClass(class_node))

                    all_assertions = [
                        assertion
                        for tc in test_classes
                        for tm in tc.test_methods
                        for assertion in tm.assertions
                    ]

                    print("----- Assertion 1 -----")
                    print(all_assertions[0])
                    print("-----------------------\n")

                    print("----- Sequenced Assertion 1 -----")
                    print(all_assertions[0].transform(SequencedAssertion))
                    print("-----------------------\n")
                except Exception as e:
                    print(f"Parsing failed for {file}: {e}")

                break
            break
