import os
import json
from pathlib import Path
from dotenv import load_dotenv
from Repository import Repository, Pair

load_dotenv()


class DatasetExplorer:
    def __init__(self, dataset_dir: str):
        self.dataset_dir: Path = Path(dataset_dir)
        # self.repositories: List[Repository] = []

    def _transform_filename(self, num: int, base: str) -> str:
        s = str(num)
        if not s.startswith(base):
            raise ValueError(f"The number {num} does not start with the base {base}")
        suffix = s[len(base) :]
        return f"{base}_{suffix}"

    def step(self):
        subdir_names = sorted(
            [int(x.stem) for x in self.dataset_dir.iterdir() if x.is_dir()]
        )
        for sd in subdir_names:  # first one doesnt have pom.xml so for testing, skip!
            base_str = str(sd)
            repo_sd = self.dataset_dir / base_str

            repo_files = [
                repo_sd / f"{self._transform_filename(x, base_str)}.json"
                for x in sorted([int(path.stem) for path in repo_sd.glob("*.json")])
            ]

            with open(repo_files[0]) as f:
                first_file = json.loads(f.read())

            repo_url = first_file.get("repository").get("url")
            repo = Repository(repo_url, base_str)

            # check if processed already
            if repo.name in [
                str(x.stem) for x in Path("../results").iterdir() if x.is_dir()
            ]:
                print(f"Skipping repo: {repo.name} ({base_str})")
                continue

            print(f"Processing repo: {repo.name} ({base_str})")

            GITHUB_PAT = os.getenv("GITHUB_PAT")
            repo.fetch_file_tree(GITHUB_PAT)
            repo.add_all_modules(GITHUB_PAT)

            for file in repo_files:
                with open(file, "r") as f:
                    data = json.load(f)

                focal_class = data.get("focal_class").get("file").split("/")[-1]
                test_class = data.get("test_class").get("file").split("/")[-1]

                for module in repo.modules:
                    print(f"  Processing module: {module.module_root.split('/')[-1]}")
                    print(f"  Contains files: {module.file_list}")
                    if (
                        focal_class in module.file_list
                        and test_class in module.file_list
                    ):
                        pair = Pair(
                            self.build_focal(data),
                            self.build_test(data),
                            str(file),
                        )
                        module.pairs.append(pair)
            # save repo here
            repo.save()
            # break

    def build_test(self, data: str):
        test_class_data = data.get("test_class", {})
        test_case_data = data.get("test_case", {})

        test_class_name = test_class_data.get("identifier", "DummyTestClass")

        test_fields_list = test_class_data.get("fields", [])
        test_fields_str = "\n    ".join(
            field.get("original_string", "") for field in test_fields_list
        )

        test_method_str = test_case_data.get("body", "")

        return (
            f"public class {test_class_name} {{\n"
            f"    {test_fields_str}\n\n"
            f"    {test_method_str}\n"
            f"}}"
        )

    def build_focal(self, data: str):
        focal_class_data = data.get("focal_class", {})
        focal_method_data = data.get("focal_method", {})

        focal_class_name = focal_class_data.get("identifier", "DummyClass")

        focal_fields_list = focal_class_data.get("fields", [])
        focal_fields_str = "\n    ".join(
            field.get("original_string", "") for field in focal_fields_list
        )

        # focal_methods_list = focal_class_data.get("methods", [])
        # focal_methods_list = "\n    ".join(
        #     field.get("original_string", "") for field in focal_methods_list
        # ) # no method content / "original string" for focal class methods

        focal_method_str = focal_method_data.get("body", "")

        return (
            f"public class {focal_class_name} {{\n"
            f"    {focal_fields_str}\n\n"
            f"    {focal_method_str}\n"
            f"}}"
        )
