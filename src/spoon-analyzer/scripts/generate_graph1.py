import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("analysis_output1.csv")

if "Total" not in df.columns:
    df["Total"] = df["Instance"] + df["Static"]

df.sort_values("Total", ascending=True, inplace=True)

cutoff = 100

df_major = df[df["Total"] >= cutoff].copy()
df_minor = df[df["Total"] < cutoff].copy()

if not df_minor.empty:
    others = {
        "Library": "Other",
        "Instance": df_minor["Instance"].sum(),
        "Static": df_minor["Static"].sum(),
        "Total": df_minor["Total"].sum(),
    }
    df_major = pd.concat([df_major, pd.DataFrame([others])], ignore_index=True)
    df_major.sort_values("Total", ascending=True, inplace=True)
else:
    df_major = df.copy()

df_major["Library"] = df_major["Library"].apply(lambda x: x.split(".")[-1])

plt.figure(figsize=(18, 12))
plt.bar(df_major["Library"], df_major["Static"], color="salmon", label="Static Count")
plt.bar(
    df_major["Library"],
    df_major["Instance"],
    bottom=df_major["Static"],
    color="skyblue",
    label="Instance Count",
)
plt.ylabel("Usage Count")
plt.xticks(rotation=60, ha="right")
plt.title("Standard Library Usage Distribution")
plt.legend()
plt.tight_layout()
plt.savefig("../../results/stb_lib_bar_vertical.png")
plt.show()


plt.figure(figsize=(18, 12))
plt.scatter(df_major["Static"], df_major["Instance"], s=100, alpha=0.7, color="purple")
for idx, row in df_major.iterrows():
    plt.text(
        row["Static"] * 1.05,
        row["Instance"] * 1.05,
        row["Library"],
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
plt.savefig("../../results/stb_lib_scatter.png")
plt.show()

plt.figure(figsize=(18, 12))
plt.bar(df_major["Library"], df_major["Total"], color="lightgreen")
plt.ylabel("Total Usage Count")
plt.xticks(rotation=60, ha="right")
plt.title("Total Standard Library Usage by Library")
plt.tight_layout()
plt.savefig("../../results/total_std_lib_vertical.png")
plt.show()
