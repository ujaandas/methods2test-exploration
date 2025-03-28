from typing import List


class Repository:
    def __init__(self, url: str, id: str):
        self.id = id
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
