# from DatasetExplorer import DatasetExplorer
import json
from TestClass import TestClass
from pathlib import Path
from javalang.parse import parse
from javalang.tree import ClassDeclaration
from Assertion import SequencedAssertion

# Step 1: Step through the dataset, and generate the Repository, Modules and Pairs and save it in results/
# DatasetExplorer("../dataset/eval").step()

# Step 2: Now, we should have pairs in results/, step through and count whatever is needed
results_dir = Path("../results")
pair_files = results_dir.glob("**/pair_*.json")

for pair_file in pair_files:
    with pair_file.open("r") as pf:
        pair_data = json.load(pf)

    test_class_code = pair_data.get("test_class")
    parsed_tree = parse(test_class_code)

    test_classes = []
    for _, class_node in parsed_tree.filter(ClassDeclaration):
        test_classes.append(TestClass(parsed_class=class_node))

    for test_class in test_classes:
        for method in [
            method for method in test_class.test_methods if method.assertions
        ]:
            print(f"Processing TestMethod: {method.name} ({pair_file})")
            for assertion in method.assertions:
                print("----- Assertion -----")
                print(assertion)
                print("---------------------\n")

                seq_assertion = assertion.transform(SequencedAssertion)
                print("----- Sequenced Assertion -----")
                print(seq_assertion)
                print(f"Sequence Depth: {seq_assertion.seq_depth}")
                print("-------------------------------\n")
