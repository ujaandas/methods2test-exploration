from DatasetExplorer import DatasetExplorer
import json
from TestClass import TestClass
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from javalang.parse import parse
from javalang.tree import ClassDeclaration
from javalang.parser import JavaSyntaxError
from Assertion import SequencedAssertion

# Step 1: Step through the dataset, and generate the Repository, Modules and Pairs and save it in results/
# DatasetExplorer("../dataset/eval").step()

# Step 2: Now, we should have pairs in results/, step through and count whatever is needed
# stats
total_assertions = 0
assertions_with_seq = 0
assertions_with_seq_args = 0
assertion_test_dist = []
assertion_types = []
sequence_lengths = []

results_dir = Path("../results")
pair_files = results_dir.glob("**/pair_*.json")

for i, pair_file in enumerate(pair_files):
    with pair_file.open("r") as pf:
        pair_data = json.load(pf)

    test_class_code = pair_data.get("test_class")
    try:
        parsed_tree = parse(test_class_code)
    except JavaSyntaxError as e:
        print(f"Syntax Error in {pair_file}: {e}")
        continue

    test_classes = []
    for _, class_node in parsed_tree.filter(ClassDeclaration):
        test_classes.append(TestClass(parsed_class=class_node))

    for test_class in test_classes:
        for method in [
            method for method in test_class.test_methods if method.assertions
        ]:
            # print(f"Processing TestMethod: {method.name} ({pair_file})")
            method_assertion_count = 0

            for assertion in method.assertions:
                total_assertions += 1
                method_assertion_count += 1

                # print("----- Assertion -----")
                # print(assertion)
                # print("---------------------\n")

                # seq_assertion = assertion.transform(SequencedAssertion)
                # print("----- Sequenced Assertion -----")
                # print(seq_assertion)
                # print(f"Sequence Depth: {seq_assertion.max_depth}")
                # print(f"Sequence Args: {seq_assertion.args}")
                # print("-------------------------------\n")

                seq_assertion = assertion.transform(SequencedAssertion)

                if seq_assertion.max_depth > 0:
                    assertions_with_seq += 1
                    sequence_lengths.append(seq_assertion.max_depth)

                    if seq_assertion.args:
                        assertions_with_seq_args += 1

                assertion_types.append(assertion.method_name)

            assertion_test_dist.append(method_assertion_count)

# viz

# dist of method seq len
plt.figure(figsize=(10, 6))
plt.hist(sequence_lengths, bins=range(1, max(sequence_lengths) + 2), edgecolor="black")
plt.title("Distribution of Method Sequence Lengths")
plt.xlabel("Sequence Length")
plt.ylabel("Frequency")
plt.xticks(range(1, max(sequence_lengths) + 1))
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("../results/mseq_len.png")
plt.show()

# assertions per test method
plt.figure(figsize=(10, 6))
plt.hist(
    assertion_test_dist, bins=range(1, max(assertion_test_dist) + 2), edgecolor="black"
)
plt.title("Distribution of Assertions Per Test Method")
plt.xlabel("Number of Assertions")
plt.ylabel("Frequency")
plt.xticks(range(1, max(assertion_test_dist) + 1))
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("../results/assertions_count.png")
plt.show()

# dist of assert types
assertion_type_counts = pd.Series(assertion_types).value_counts()
plt.figure(figsize=(10, 6))
assertion_type_counts.plot(kind="bar", color="skyblue", edgecolor="black")
plt.title("Distribution of Assertion Types")
plt.xlabel("Assertion Type")
plt.ylabel("Frequency")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("../results/assertion_type.png")
plt.show()

# summary
print("----- Summary Statistics -----")
print(f"Total Assertions: {total_assertions}")
print(f"Assertions with Method Sequences: {assertions_with_seq}")
print(f"Assertions with Method Sequence Arguments: {assertions_with_seq_args}")
print(
    f"Average Assertions Per Test: {sum(assertion_test_dist) / len(assertion_test_dist):.2f}"
)
print(
    f"Most Common Assertion Type: {assertion_type_counts.idxmax()} ({assertion_type_counts.max()} occurrences)"
)

print(
    f"Percentage of Single Method Sequences of Total: {(sequence_lengths.count(1) / len(sequence_lengths)) * 100:.2f}%"
)

print(
    f"Percentage of Test Methods with One Assertion: {(assertion_test_dist.count(1) / len(assertion_test_dist)) * 100:.2f}%"
)

print(
    f"Percentage of Assertions with Method Sequences of Total Assertions: {(assertions_with_seq / total_assertions) * 100:.2f}%"
)

print(
    f"Percentage of Assertions with Method Sequence Arguments of Total Assertions: {(assertions_with_seq_args / total_assertions) * 100:.2f}%"
)
