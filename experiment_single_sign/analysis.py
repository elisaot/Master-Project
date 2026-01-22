import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
from src.single_signs.evaluate import (
    compare_signwriting,
    summarize_lengths_and_means,
    count_empty_strings,
    compare_length,
    count_unique_values,
    analyze_value_columns,
    visualize_signwriting,
)
import matplotlib.pyplot as plt


def extract_annotation_values(eaf_path):
    """Extract all <ANNOTATION_VALUE>...</ANNOTATION_VALUE> texts from an .eaf file."""
    tree = ET.parse(eaf_path)
    root = tree.getroot()

    return " ".join(
        elem.text.strip() for elem in root.findall(".//ANNOTATION_VALUE") if elem.text
    )


def process_eaf_folder(folder_path):
    """Build a table containing filename, stem, and list of annotation values."""
    data = []

    for file_path in glob.glob(os.path.join(folder_path, "*.eaf")):
        filename = os.path.basename(file_path)
        stem = os.path.splitext(filename)[0]

        values = extract_annotation_values(file_path)

        data.append({"name": filename, "stem": stem, "value": values})

    df = pd.DataFrame(data)
    return df


def split_stem(s):
    parts = s.split("_", 1)
    return parts if len(parts) == 2 else ("", s)


if __name__ == "__main__":
    exp_folder = "experiment_single_sign/results/normalized_poses/"
    experiment_df = process_eaf_folder(exp_folder)

    org_folder = "experiment_single_sign/results/originals/normalized_poses/"
    original_df = process_eaf_folder(org_folder)

    merged_df = original_df
    merged_df["cut_value"] = np.nan
    merged_df["speed_value"] = np.nan
    merged_df["both_value"] = np.nan

    # Add prefix + base columns
    experiment_df["prefix"], experiment_df["base"] = zip(
        *experiment_df["stem"].map(split_stem)
    )

    for prefix in experiment_df["prefix"].unique():

        # Create the column name to fill
        col = f"{prefix}_value"

        # If df2 has that column, perform the merge for only this prefix
        if col in merged_df.columns:

            # Filter df1 only for this prefix
            tmp = experiment_df[experiment_df["prefix"] == prefix][["base", "value"]]

            # Merge into df2 (left join)
            merged_df = merged_df.merge(
                tmp, how="left", left_on="stem", right_on="base", suffixes=("", "_new")
            )

            # Fill the appropriate column
            merged_df[col] = merged_df["value_new"]

            # Cleanup
            merged_df = merged_df.drop(columns=["base", "value_new"])

    print(f"\nNumbers of missing entries per columns:")
    counts = compare_length(merged_df)

    merged_df = merged_df.applymap(
        lambda x: " " if isinstance(x, float) and pd.isna(x) else x
    )
    print(f"\nNumber of entries with no predictions:")
    # counts["original_value"] = counts.pop("value")
    no_predicts = count_empty_strings(merged_df, counts=counts)

    print("\nNumber of unique predictions per column:")
    count_unique_values(merged_df)

    # Analyze value columns and plot histograms
    # analyze_value_columns(merged_df)

    sw_df = pd.read_csv("data/results/tables/matched_single_signs.csv")
    result_df = compare_signwriting(merged_df, sw_df, experiment=True)

    summary_df = summarize_lengths_and_means(result_df)

    column_means = summary_df.mean()
    table = column_means.unstack(level=0)
    print("\nMean of each column:")
    print(table)

    # draw three random samples and vizualize the SW for manual inspection.
    output_dir = "experiment_single_sign/visualizations"
    os.makedirs(output_dir, exist_ok=True)  # creates the folder if needed

    counts = result_df["stem"].value_counts()
    stems = counts[counts == 1].index.tolist()

    np.random.seed(42)
    samples = np.random.choice(stems, size=3, replace=False)

    cols = ["original_value", "speed_value", "reference"]

    sample_df = result_df[result_df["stem"].isin(samples)][["stem"] + cols]
    # Optional: reset index
    sample_df = sample_df.reset_index(drop=True)

    # Save to CSV
    output_file = "experiment_single_sign/visualizations/samples.csv"
    sample_df.to_csv(output_file, index=False)

    for sample in samples:
        for col in cols:
            sw_value = result_df[result_df["stem"] == sample][col].values[0]
            print(f"Visualizing stem: {sample}, column: {col}")
            visualize_signwriting(
                sw_value,
                filename=f"experiment_single_sign/visualizations/{sample}_{col}",
            )

    quit()
    merged_df.to_csv("experiment_single_sign/SW_annotations.csv", index=False)


"""Example output of the code above:
Numbers of missing entries per columns:
Column 'value' NaN count:
0
Column 'cut_value' NaN count:
8
Column 'speed_value' NaN count:
0
Column 'both_value' NaN count:
12

Number of entries with no predictions:
Column 'value' has 82 empty entries.
Column 'cut_value' has 51 empty entries.
Column 'speed_value' has 40 empty entries.
Column 'both_value' has 34 empty entries.

Number of unique predictions per column:
Column 'value' unique values: 1749 (75.55%)
Column 'cut_value' unique values: 1448 (62.55%)
Column 'speed_value' unique values: 1683 (72.70%)
Column 'both_value' unique values: 1345 (58.10%)

Mean of each column:
                      both       cut  original     speed
CHRF              0.224172  0.222806  0.215246  0.221483
CLIPScore         0.854425  0.853023  0.852385  0.855416
SymbolsDistances  0.178293  0.174245  0.164952  0.169814
TokenizedBLEU     0.047062  0.046225  0.043882  0.045184
avg_len           1.951344  1.983664  2.099069  2.119796

"""
# The multiplisities and empty predictions of the experiments are only exarbated when merged with references due to multiplicities there as well. I.e. length of experiment is about 2000 rows, whereas the merged experiment and references have a length of about 5000 rows.
