import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("analysis_output2.csv")

if "Total" not in df.columns:
    df["Total"] = df["Instance"] + df["Static"]
df.sort_values("Total", ascending=True, inplace=True)

cutoff = 100

df_major = df[df["Total"] >= cutoff].copy()
df_minor = df[df["Total"] < cutoff].copy()
if not df_minor.empty:
    others = {
        "Package Prefix": "Other",
        "Instance": df_minor["Instance"].sum(),
        "Static": df_minor["Static"].sum(),
        "Total": df_minor["Total"].sum(),
    }
    df_major = pd.concat([df_major, pd.DataFrame([others])], ignore_index=True)
    df_major.sort_values("Total", ascending=True, inplace=True)
else:
    df_major = df.copy()

plt.figure(figsize=(18, 12))
plt.bar(df_major["Package Prefix"], df_major["Total"], color="lightgreen")
plt.ylabel("Total Usage Count")
plt.title("Total Package Prefix Usage by Package Prefix")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("../../results/total_pkg_prefix.png")
plt.show()


plt.figure(figsize=(18, 12))
plt.scatter(df_major["Static"], df_major["Instance"], s=100, alpha=0.7, color="purple")
for idx, row in df_major.iterrows():
    plt.text(
        row["Static"] * 1.05,
        row["Instance"] * 1.05,
        row["Package Prefix"],
        fontsize=9,
        verticalalignment="center",
    )
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Static Count")
plt.ylabel("Instance Count")
plt.title("Static vs. Instance Usage")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("../../results/pkg_prefix_scatter.png")
plt.show()

plt.figure(figsize=(18, 12))
plt.bar(
    df_major["Package Prefix"], df_major["Static"], color="salmon", label="Static Count"
)
plt.bar(
    df_major["Package Prefix"],
    df_major["Instance"],
    bottom=df_major["Static"],
    color="skyblue",
    label="Instance Count",
)
plt.ylabel("Usage Count")
plt.title("Package Prefix Usage Distribution")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig("../../results/pkg_prefix_bar.png")
plt.show()
