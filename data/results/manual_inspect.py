import pandas as pd

df = pd.read_csv("tables/matched_single_signs.csv")

unique_vid = df["Filename"].unique()

print(len(unique_vid))
"""2316 uniqe videos from the matches."""