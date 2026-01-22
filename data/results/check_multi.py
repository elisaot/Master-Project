import pandas as pd
import matplotlib.pyplot as plt
from get_tables import clean_modified
from pathlib import Path


def plot_hist(df, save_name):
    if "modified" not in df.columns:
        df["modified"] = df["Gloss"].str.replace("-", " ", regex=False)
        # Step 2: Remove everything from first occurrence of '(', ')', ':', digit, or '/'
        df["modified"] = df["modified"].apply(clean_modified)
        df["modified"] = df["modified"].str.strip()
        df["modified"] = df["modified"].str.lower()

    duplicates = df[df.duplicated(subset=["modified"])]
    print(duplicates)

    # gloss_counts = df["Gloss_y"].value_counts()
    gloss_counts = df["modified"].value_counts()
    most_common_value = gloss_counts.idxmax()
    most_common_count = gloss_counts.max()

    print(most_common_value, most_common_count)

    plt.figure(figsize=(10, 6))
    plt.hist(
        gloss_counts,
        bins=range(1, gloss_counts.max() + 2),
        edgecolor="black",
        align="left",
    )
    plt.xlabel("Number of Occurrences")
    plt.ylabel("Number of Glosses")
    plt.title("Histogram of Gloss Multiplicities")
    plt.xticks(range(1, gloss_counts.max() + 1))

    plt.savefig(f"{save_name}.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    paths = (
        "tables/matched_single_signs.csv",
        "tables/signpuddle_dict.csv",
        "tables/statped_dict.csv",
    )
    for path in paths:
        df = pd.read_csv(path)
        path = Path(path)
        stem = path.stem
        plot_hist(df, stem)


"""Signpuddle: [3035 rows x 3 columns] -> vann 22"""
"""Statped: [1989 rows x 5 columns] -> spille 15"""
"""Matched: [4075 rows x 7 columns] -> vann 66"""
