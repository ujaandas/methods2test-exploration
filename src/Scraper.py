import requests
import base64
import xml.etree.ElementTree as ET
from typing import List


class Repository:
    def __init__(self, url: str):
        self.url = url
        parts = url.rstrip("/").split("/")
        self.name = parts[-1]
        self.owner = parts[-2]

        self.sub_repos: List[SubRepository] = []


class SubRepository:
    def __init__(self, pom: str):
        self.pom: str = pom
        self.pom_hash = None
        self.pairs: List[Pair] = []


class Pair:
    def __init__(self):
        self.focal_class: str = None
        self.test_class: str = None


class TreeNode:
    def __init__(
        self,
        name: str,
        node_type: str,
        sha: str = None,
        url: str = None,
        parent: "TreeNode" = None,
    ):
        self.name = name
        self.type = node_type
        self.sha = sha
        self.url = url
        self.parent = parent
        self.children = {}

        if parent is None or parent.full_path == "":
            self.full_path = name
        else:
            self.full_path = f"{parent.full_path}/{name}"


class Scraper:
    def __init__(self, token: str):
        self.token = token
        self.tree = None
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get_tree(self, repo: Repository):
        base_repo_url = f"https://api.github.com/repos/{repo.owner}/{repo.name}"

        repo_response = requests.get(base_repo_url, headers=self.headers)
        if repo_response.status_code != 200:
            print(
                f"Failed to retrieve repository info for {repo.url}: {repo_response.json()}"
            )
            return None
        repo_info = repo_response.json()
        # print(repo_info)
        default_branch = repo_info.get("default_branch")

        branch_url = f"{base_repo_url}/branches/{default_branch}"
        branch_response = requests.get(branch_url, headers=self.headers)
        if branch_response.status_code != 200:
            print(
                f"Failed to retrieve branch info for {repo.url}: {branch_response.json()}"
            )
            return None
        branch_info = branch_response.json()
        commit_sha = branch_info.get("commit", {}).get("sha")
        if not commit_sha:
            print(f"Commit SHA not found for '{default_branch}' in {repo.url}")
            return None

        tree_url = f"{base_repo_url}/git/trees/{commit_sha}?recursive=1"
        tree_response = requests.get(tree_url, headers=self.headers)
        if tree_response.status_code != 200:
            print(
                f"Failed to retrieve tree for commit {commit_sha}: {tree_response.json()}"
            )
            return None

        return tree_response.json()

    def _build_tree(self, tree_items: list):
        root = TreeNode("", "tree")
        for item in tree_items:
            path = item.get("path")
            if not path:
                continue
            parts = path.split("/")
            current_node = root
            for i, part in enumerate(parts):
                if part not in current_node.children:
                    if i == len(parts) - 1:
                        node = TreeNode(
                            name=part,
                            node_type=item.get("type"),
                            sha=item.get("sha"),
                            url=item.get("url"),
                            parent=current_node,
                        )
                    else:
                        node = TreeNode(part, "tree", parent=current_node)
                    current_node.children[part] = node
                current_node = current_node.children[part]
        return root

    def _get_file_content(self, file_url: str):
        response = requests.get(file_url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to get file content: {file_url}")
            return None
        file_json = response.json()
        if file_json.get("encoding") == "base64" and "content" in file_json:
            content = base64.b64decode(file_json["content"]).decode("utf-8")
            return content
        return None

    def find_nodes_by_filename(self, node: TreeNode, filename: str):
        matches = []
        if node.type == "blob" and node.name == filename:
            matches.append(node)
        for child in node.children.values():
            matches.extend(self.find_nodes_by_filename(child, filename))
        return matches

    def get_module_for_node(self, node: TreeNode):
        current = node.parent
        while current:
            if (
                "pom.xml" in current.children
                and current.children["pom.xml"].type == "blob"
            ):
                return current, current.children["pom.xml"]
            current = current.parent
        return None, None

    def scrape_with_class_pairs(
        self,
        repo: Repository,
        class_pairs: list,
    ):
        tree_json = self._get_tree(repo)
        if not tree_json:
            print(f"Failed to retrieve file tree for {repo.url}")
            return

        self.tree = self._build_tree(tree_json.get("tree", []))
        if not self.tree:
            print("Failed to build repository tree")
            return

        subrepos_by_pom = {}

        for test_class, focal_class in class_pairs:
            focal_nodes = self.find_nodes_by_filename(self.tree, focal_class)
            test_nodes = self.find_nodes_by_filename(self.tree, test_class)

            if not focal_nodes:
                print(f"Focal class '{focal_class}' not found in the repository tree.")
                continue
            if not test_nodes:
                print(f"Test class '{test_class}' not found in the repository tree.")
                continue

            for focal_node in focal_nodes:
                module_dir, pom_node = self.get_module_for_node(focal_node)
                if not pom_node:
                    print(
                        f"Could not find a pom.xml for focal file at '{focal_node.full_path}'."
                    )
                    continue

                matching_test_nodes = [
                    tn
                    for tn in test_nodes
                    if module_dir.full_path == ""
                    or tn.full_path.startswith(module_dir.full_path)
                ]

                if not matching_test_nodes:
                    print(
                        f"No matching test file found under module '{module_dir.full_path}' for focal '{focal_node.full_path}'"
                    )
                    continue

                for test_node in matching_test_nodes:
                    pom_content = self._get_file_content(pom_node.url)
                    if not pom_content:
                        print(
                            f"Failed to retrieve pom.xml content at '{pom_node.full_path}'."
                        )
                        continue

                    try:
                        pom_scraper = POMScraper(pom_content)
                    except ValueError as e:
                        print(
                            f"Skipping invalid pom.xml at '{pom_node.full_path}': {e}"
                        )
                        continue

                    junit_ok, java_ok = pom_scraper.is_valid()
                    if not (java_ok and junit_ok):
                        print(
                            f"pom.xml at '{pom_node.full_path}' does not meet requirements."
                        )
                        continue

                    pair = Pair()
                    pair.focal_class = focal_node.full_path
                    pair.test_class = test_node.full_path

                    pom_hash = pom_node.sha
                    if pom_hash not in subrepos_by_pom:
                        sub_repo = SubRepository(pom_content)
                        sub_repo.pom_hash = pom_hash
                        sub_repo.pairs.append(pair)
                        subrepos_by_pom[pom_hash] = sub_repo
                    else:
                        subrepos_by_pom[pom_hash].pairs.append(pair)

        repo.sub_repos.extend(subrepos_by_pom.values())
        print(
            f"Scraping completed for repo '{repo.name}'. Found {len(repo.sub_repos)} module(s)."
        )


class POMScraper:
    def __init__(self, pom_content: str):
        try:
            self.root = ET.fromstring(pom_content)
        except ET.ParseError as e:
            raise ValueError("Invalid XML content in POM") from e
        self.ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

    def _get_text(self, el: ET.Element):
        return el.text.strip() if el is not None and el.text else None

    def _check_junit(self, ensure_junit_ver: int = 4):
        expected_prefix = f"{ensure_junit_ver}."
        for dep in self.root.findall(".//mvn:dependency", self.ns):
            group_id = self._get_text(dep.find("mvn:groupId", self.ns))
            artifact_id = self._get_text(dep.find("mvn:artifactId", self.ns))
            version = self._get_text(dep.find("mvn:version", self.ns))
            if (
                group_id == "junit"
                and artifact_id == "junit"
                and version
                and version.startswith(expected_prefix)
            ):
                return True
        return False

    def _check_java_props(self, java_ver: str):
        props = self.root.find("mvn:properties", self.ns)
        if props is not None:
            # check for <java.version>
            if self._get_text(props.find("mvn:java.version", self.ns)) == java_ver:
                return True
            # Check for both <maven.compiler.source> and <maven.compiler.target>
            src = self._get_text(props.find("mvn:maven.compiler.source", self.ns))
            tgt = self._get_text(props.find("mvn:maven.compiler.target", self.ns))
            if (
                src == java_ver or tgt == java_ver
            ):  # should be AND, but use OR for looser restr.
                return True
        return False

    def _check_java_plugin(self, java_ver: str):
        for plugin in self.root.findall(".//mvn:plugin", self.ns):
            artifact = self._get_text(plugin.find("mvn:artifactId", self.ns))
            if artifact == "maven-compiler-plugin":
                config = plugin.find("mvn:configuration", self.ns)
                if config is not None:
                    src = self._get_text(config.find("mvn:source", self.ns))
                    tgt = self._get_text(config.find("mvn:target", self.ns))
                    if src == java_ver and tgt == java_ver:
                        return True
        return False

    def check_java(self, java_ver: int):
        expected_java_ver = str(java_ver)
        if self._check_java_props(expected_java_ver):
            return True
        return self._check_java_plugin(expected_java_ver)

    def is_valid(self, ensure_java_ver: int = 17, ensure_junit_ver: int = 4):
        junit_ok = self._check_junit(ensure_junit_ver)
        # java_ok = self.check_java(ensure_java_ver)
        #! CHANGE THIS FOR STRICTER CHECKING!
        java_ok = True
        return junit_ok, java_ok
