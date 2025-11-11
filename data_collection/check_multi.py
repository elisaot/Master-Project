import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("tables/signpuddle_dict.csv")


# Find completely duplicated rows
duplicates = df[df.duplicated(subset=["modified"])]
# print(duplicates)

gloss_counts = df["Gloss"].value_counts()

plt.figure(figsize=(10, 6))
plt.hist(
    gloss_counts, bins=range(1, gloss_counts.max() + 2), edgecolor="black", align="left"
)
plt.xlabel("Number of Occurrences")
plt.ylabel("Number of Glosses")
plt.title("Histogram of Gloss Multiplicities")
plt.xticks(range(1, gloss_counts.max() + 1))

plt.savefig("Signpuddle_gloss_histogram.png", dpi=300, bbox_inches="tight")
plt.show()
