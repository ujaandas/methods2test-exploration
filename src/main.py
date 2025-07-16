import json
from TestClass import TestClass
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from javalang.parse import parse
from javalang.tree import ClassDeclaration
from javalang.parser import JavaSyntaxError
from collections import Counter


total_assertions = 0
assertions_with_seq = 0
assertions_with_seq_args = 0
assertion_test_dist = []
assertion_types = {}
sequence_lengths = []
sequence_depths = []
assertions_with_std = 0

variable_counts = []

results_dir = Path("../results")
pair_files = list(results_dir.glob("**/pair_*.json"))

for pair_file in pair_files:
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
        for method in [m for m in test_class.test_methods if m.assertions]:
            method_assertion_count = 0
            for assertion in method.assertions:
                total_assertions += 1
                method_assertion_count += 1

                variable_counts.append(assertion.variable_count)

                if len(assertion.arguments) > 0:
                    assertions_with_seq_args += 1
                depth = assertion.get_depth()
                length = assertion.get_length()
                if depth > 0:
                    sequence_depths.append(depth)
                if length >= 1:
                    assertions_with_seq += 1
                    sequence_lengths.append(length)
                key = assertion.method_name.removeprefix("assert")
                assertion_types[key] = assertion_types.get(key, 0) + 1
            assertion_test_dist.append(method_assertion_count)

if sequence_lengths:
    length_counts = Counter(sequence_lengths)
    lengths = sorted(length_counts.keys())
    counts = [length_counts[length] for length in lengths]

    plt.figure(figsize=(10, 6))
    plt.bar(lengths, counts, edgecolor="black")
    plt.yscale("log")
    plt.title("Distribution of Method Sequence Lengths")
    plt.xlabel("Sequence Length")
    plt.ylabel("Frequency")
    plt.xticks(lengths)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("../results/mseq_len.png")
    plt.show()
else:
    print("No sequence length data available.")

if sequence_depths:
    depth_counts = Counter(sequence_depths)
    depths = sorted(depth_counts.keys())
    counts = [depth_counts[depth] for depth in depths]

    plt.figure(figsize=(10, 6))
    plt.bar(depths, counts, edgecolor="black")
    plt.yscale("log")
    plt.title("Distribution of Method Sequence Depths")
    plt.xlabel("Sequence Depth")
    plt.ylabel("Frequency")
    plt.xticks(depths)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("../results/mseq_depth.png")
    plt.show()
else:
    print("No sequence depth data available.")

if assertion_test_dist:
    max_bin = 10
    transformed = [x if x <= max_bin else max_bin + 1 for x in assertion_test_dist]
    assertion_counts = Counter(transformed)
    assertion_values = sorted(assertion_counts.keys())
    counts = [assertion_counts[val] for val in assertion_values]

    xtick_labels = (
        [str(i) for i in range(1, max_bin + 1)] + [f"{max_bin}+"]
        if max_bin + 1 in assertion_values
        else [str(i) for i in assertion_values]
    )

    plt.figure(figsize=(10, 6))
    plt.bar(assertion_values, counts, edgecolor="black")
    plt.yscale("log")
    plt.title("Distribution of Assertions Per Test Method")
    plt.xlabel("Number of Assertions")
    plt.ylabel("Frequency")
    plt.xticks(assertion_values, xtick_labels)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("../results/assertions_count.png")
    plt.show()
else:
    print("No assertions-per-test data available.")

if assertion_types:
    series = pd.Series(assertion_types)
    plt.figure(figsize=(10, 6))
    series.sort_values(ascending=False).plot(
        kind="bar", color="skyblue", edgecolor="black"
    )
    plt.title("Distribution of Assertion Types")
    plt.xlabel("Assertion Type")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("../results/assertion_type.png")
    plt.show()
else:
    print("No assertion type data available.")

if variable_counts:
    var_counts_counter = Counter(variable_counts)
    var_keys = sorted(var_counts_counter.keys())
    var_values = [var_counts_counter[key] for key in var_keys]

    plt.figure(figsize=(10, 6))
    plt.bar(var_keys, var_values, edgecolor="black")
    plt.yscale("log")
    plt.title("Distribution of Variable Counts per Assertion")
    plt.xlabel("Number of Variables in Assertion")
    plt.ylabel("Frequency")
    plt.xticks(var_keys)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("../results/variable_count_dist.png")
    plt.show()
else:
    print("No variable count data available.")

print("----- Summary Statistics -----")
print(f"Total Assertions: {total_assertions}")
print(f"Assertions with Method Sequences: {assertions_with_seq}")
print(f"Assertions with Method Sequence Arguments: {assertions_with_seq_args}")
if assertion_test_dist:
    avg_assertions = sum(assertion_test_dist) / len(assertion_test_dist)
    print(f"Average Assertions Per Test: {avg_assertions:.2f}")
else:
    print("No test method assertion data available.")

if assertion_types:
    series = pd.Series(assertion_types)
    most_common = series.idxmax()
    most_common_count = series.max()
    print(
        f"Most Common Assertion Type: {most_common} ({most_common_count} occurrences)"
    )

pct_single_seq = (
    (sequence_lengths.count(1) / len(sequence_lengths) * 100) if sequence_lengths else 0
)
print(f"Percentage of Single Method Sequences of Total: {pct_single_seq:.2f}%")

pct_one_assertion = (
    (assertion_test_dist.count(1) / len(assertion_test_dist) * 100)
    if assertion_test_dist
    else 0
)
print(f"Percentage of Test Methods with One Assertion: {pct_one_assertion:.2f}%")

pct_seq_assertions = (
    (assertions_with_seq / total_assertions * 100) if total_assertions else 0
)
print(f"Percentage of Assertions with Method Sequences: {pct_seq_assertions:.2f}%")

pct_seq_args = (
    (assertions_with_seq_args / total_assertions * 100) if total_assertions else 0
)
print(f"Percentage of Assertions with Method Sequence Arguments: {pct_seq_args:.2f}%")

if variable_counts:
    total_variables = sum(variable_counts)
    avg_variables = total_variables / total_assertions if total_assertions else 0
    print(f"Total Variable References: {total_variables}")
    print(f"Average Variables per Assertion: {avg_variables:.2f}")
