# from javalang.parse import parse
# from javalang.tree import ClassDeclaration
# from TestClass import TestClass
# from DatasetExplorer import DatasetExplorer
from Assertion import Assertion, SequencedAssertion

# with open("samples/AssertionSeq.java") as f:
#     sample = f.read()

# parsed_tree = parse(sample)
# test_classes = []
# for _, class_node in parsed_tree.filter(ClassDeclaration):
#     test_classes.append(TestClass(parsed_class=class_node))


# print(test_classes)

# from Scraper import Scraper, Repository

# repo = Repository("https://github.com/justinsb/jetcd")
# pairs_to_find = [("SmokeTest.java", "EtcdClient.java")]
# Scraper(
#     token="."
# ).scrape_with_class_pairs(repo, pairs_to_find)

# for sub_repo in repo.sub_repos:
#     print(f"\nModule with pom hash {sub_repo.pom_hash}:")
#     for pair in sub_repo.pairs:
#         print(f"  Focal: {pair.focal_class}  |  Test: {pair.test_class}")

# DatasetExplorer("../dataset/eval").step()

assertion = Assertion(
    method_name="assertEquals",
    expected="0",
    actual="a.foo().bar()",
    arguments=["0", "a.foo(foo.a(1)).bar(2).baz(3).qoz(4)"],
    line_number=42,
)

print("----- Assertion 1 -----")
print(assertion)
print("-----------------------\n")

print("----- Sequenced Assertion 1 -----")
seq_assertion = assertion.transform(SequencedAssertion)
print(seq_assertion)
print("-----------------------\n")
