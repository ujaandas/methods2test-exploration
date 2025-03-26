# from javalang.parse import parse
# from javalang.tree import ClassDeclaration
# from TestClass import TestClass

# with open("samples/AssertionSeq.java") as f:
#     sample = f.read()

# parsed_tree = parse(sample)
# test_classes = []
# for _, class_node in parsed_tree.filter(ClassDeclaration):
#     test_classes.append(TestClass(parsed_class=class_node))


# print(test_classes)

# from Scraper import POMScraper

# with open(
#     "/Users/ooj/Dev/Research/assertion/spoon-assertion-finder/repos/jetcd/pom.xml",
#     "r",
# ) as f:
#     pom = f.read()

# pom = POMScraper(pom)
# print(pom.is_valid())
