import requests
import base64
from pathlib import Path
import json
from POMScraper import POMScraper


class Repository:
    def __init__(self, url, id):
        self.url = url
        self.id = id
        parts = url.rstrip("/").split("/")
        self.name = parts[-1]
        self.owner = parts[-2]
        self.modules = []
        self.tree = None

    def _get_file_content(self, file_url, headers):
        response = requests.get(file_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get file content: {file_url}")
            return None
        file_json = response.json()
        if file_json.get("encoding") == "base64" and "content" in file_json:
            content = base64.b64decode(file_json["content"]).decode("utf-8")
            return content
        return None

    def fetch_file_tree(self, token):
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        base_repo_url = f"https://api.github.com/repos/{self.owner}/{self.name}"
        repo_resp = requests.get(base_repo_url, headers=headers)
        if repo_resp.status_code != 200:
            print(f"Error fetching repo info for {self.url}")
            return

        default_branch = repo_resp.json().get("default_branch")
        branch_resp = requests.get(
            f"{base_repo_url}/branches/{default_branch}", headers=headers
        )
        if branch_resp.status_code != 200:
            print(f"Error fetching branch info for {self.url}")
            return

        commit_sha = branch_resp.json().get("commit", {}).get("sha")
        if not commit_sha:
            print(f"Commit SHA not found for {self.url}")
            return

        tree_resp = requests.get(
            f"{base_repo_url}/git/trees/{commit_sha}?recursive=1", headers=headers
        )
        if tree_resp.status_code != 200:
            print(f"Error fetching tree for commit {commit_sha}")
            return

        self.tree = tree_resp.json().get("tree", [])

    def add_all_modules(self, token):
        print("Adding modules...")
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        if self.tree is None:
            print("File tree not available!")
            return
        module_info = {}

        for item in self.tree:
            if item.get("type") != "blob":
                continue
            path = item.get("path")
            if path.endswith("pom.xml"):
                parts = path.split("/")
                module_root = "/".join(parts[:-1])
                module_info[module_root] = {"pom_path": path, "files": []}
                print(f"Found pom at {path}")

        for item in self.tree:
            if item.get("type") != "blob":
                continue
            path = item.get("path")
            for module_root in module_info:
                if module_root == "" or path.startswith(module_root + "/"):
                    module_info[module_root]["files"].append(path.split("/")[-1])

        if len(module_info.values()) <= 0:
            print("No pom.xml!")
            return

        for module_root, info in module_info.items():
            pom_node = next(
                (item for item in self.tree if item.get("path") == info["pom_path"]),
                None,
            )
            if not pom_node:
                continue
            pom_content = self._get_file_content(pom_node.get("url"), headers)
            if not pom_content:
                continue
            try:
                pom_scraper = POMScraper(pom_content)
                print(f"POM at {pom_node}")
            except ValueError as e:
                print(f"Skipping pom.xml at {info['pom_path']} due to error: {e}")
                continue
            if not pom_scraper.is_valid():
                print(f"pom.xml at {info['pom_path']} is invalid.")
                continue

            mod = Module(module_root, info["pom_path"], info["files"])
            mod.pom_hash = pom_node.get("sha")
            if module_root == "":
                print("Setting root module explicitly.")
                self.root_module = mod  # assign as root
            else:
                print(f"Adding module: {mod.module_root.split('/')[-1]}")
                self.modules.append(mod)

    def save(self, results_dir="../results"):
        results_dir = Path(results_dir)

        modules_with_pairs = [mod for mod in self.modules if mod.pairs]

        repo_folder = results_dir / self.name
        repo_folder.mkdir(parents=True, exist_ok=True)

        if not modules_with_pairs:
            print("No pairs!")
            return

        repo_data = {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "owner": self.owner,
        }

        for mod in modules_with_pairs:
            mod_folder_name = (
                mod.module_root.replace("/", "_") if mod.module_root else self.name
            )
            mod_folder = repo_folder / mod_folder_name
            mod_folder.mkdir(parents=True, exist_ok=True)

            mod_data = {
                "module_root": mod.module_root,
                "pom_path": mod.pom_path,
            }

            for idx, pair in enumerate(mod.pairs, start=1):
                pair_data = {
                    "focal_class": pair.focal_class,
                    "test_class": pair.test_class,
                    "m2t_loc": pair.m2t_loc,
                }
                pair_file = mod_folder / f"pair_{idx}.json"
                with pair_file.open("w") as pf:
                    json.dump(pair_data, pf, indent=2)

            mod_file = mod_folder / "module_info.json"
            with mod_file.open("w") as mf:
                json.dump(mod_data, mf, indent=2)

        repo_file = repo_folder / "repo_info.json"
        with repo_file.open("w") as rf:
            json.dump(repo_data, rf, indent=2)


class Module:
    def __init__(self, module_root, pom_path, file_list):
        self.module_root = module_root
        self.pom_path = pom_path
        self.file_list = file_list
        self.pairs = []

    def __repr__(self):
        return f"Module(root={self.module_root}, pom={self.pom_path}, files={len(self.file_list)})"


class Pair:
    def __init__(self, focal_class: str, test_class: str, m2t_loc: str):
        self.focal_class = focal_class
        self.test_class = test_class
        self.m2t_loc = m2t_loc

    def __repr__(self):
        return f"Pair(focal_class={self.focal_class}, test_class={self.test_class})"
