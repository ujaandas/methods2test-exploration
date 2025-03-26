import requests
import xml.etree.ElementTree as ET


class Repository:
    def __init__(self, url: str):
        self.url = url
        self.parts = url.rstrip("/").split("/")
        self.owner = self.parts[-2]
        self.name = self.parts[-1]

        self.pom = None
        self.test_classes = []


class Scraper:
    def __init__(self, token: str):
        self.token = token

    def _verify(self, repo: Repository):
        headers = {
            "Authorization": f"token {self.token}",
        }

        response = requests.get(
            f"https://api.github.com/search/code?q=repo:{repo.owner}/{repo.name}+filename:pom.xml",
            headers=headers,
        )

        rate_limit_remaining = int(response.headers.get("x-ratelimit-remaining"))
        rate_limit_reset = response.headers.get("x-ratelimit-reset")

        if response.status_code == 200:
            if rate_limit_remaining == 0:
                print("Rate limit exceeded. Exiting...")
                print(f"Rate limit reset time (UTC epoch seconds): {rate_limit_reset}")
                return "err"
            search_results = response.json()
            print(f"Found {search_results['total_count']} pom.xml files in {repo.url}")
            return search_results["total_count"] > 0
        else:
            print(f"Failed to search repo {repo.name}, {response.json()}")
            return "err"


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
        java_ok = self.check_java(ensure_java_ver)
        return junit_ok and java_ok
