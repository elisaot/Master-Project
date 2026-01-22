import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys
import re
from pathlib import Path

# Add the directory that *contains* the signwriting_evaluation folder
sys.path.append(str(Path(__file__).parent / "signwriting-evaluation"))

from signwriting_evaluation.metrics.bleu import SignWritingBLEU
from signwriting_evaluation.metrics.chrf import SignWritingCHRF
from signwriting_evaluation.metrics.clip import (
    SignWritingCLIPScore,
    signwriting_to_clip_image,
)
from signwriting_evaluation.metrics.similarity import SignWritingSimilarityMetric


def visualize_signwriting(value, filename="SignWriting_Visualization"):
    """Generate and display a SignWriting image from its string representation."""
    from PIL import Image

    v = value.split()
    if len(v) > 1:
        for i in range(len(v)):
            img = signwriting_to_clip_image(v[i], size=224)
            img.save(f"{filename}_{i+1}.png")
    else:
        img = signwriting_to_clip_image(value, size=224)
        img.save(f"{filename}.png")


def analyze_value_columns(
    merged_df, col_prefix="value", output_dir="experiment_single_sign"
):
    """
    For each *_value columnplot and save histogram of value multiplicities
    """

    value_cols = [c for c in merged_df.columns if c.endswith(col_prefix)]

    for col in value_cols:
        # normalize: treat whitespace-only as empty and drop
        series = merged_df[col].astype(str).str.strip().replace("", None).dropna()

        gloss_counts = series.value_counts()

        # ---- histogram ----
        plt.figure(figsize=(10, 6))
        plt.hist(
            gloss_counts.values,
            bins=range(1, gloss_counts.max() + 2),
            edgecolor="black",
            align="left",
        )
        plt.xlabel("Number of Occurrences")
        plt.ylabel("Number of Glosses")
        plt.title(f"Histogram of Gloss Multiplicities ({col})")
        plt.xticks(rotation=45)

        plt.savefig(
            f"{output_dir}/experiment_pred_{col}_hist.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.show()


def normalize_sw(value):
    """Convert NaN or non-string inputs into safe empty strings."""
    if isinstance(value, str):
        return value
    if pd.isna(value):
        return ""
    return str(value)


def any_match(hypothesis, reference):
    """Return True if reference matches any entry in hypothesis list."""
    # Normalize reference
    reference = normalize_sw(reference)
    # if not isinstance(hypothesis, list):
    # return False
    final_hypothesis = normalize_sw(hypothesis)
    return reference in final_hypothesis


def get_metrics(hypothesis, reference, metrics):
    """Return a list of instantiated SignWriting evaluation metric objects."""
    # Normalize reference
    reference = normalize_sw(reference)

    if not isinstance(hypothesis, str):
        return {metric.name: [np.nan] for metric in metrics}

    final_hypothesis = normalize_sw(hypothesis)

    results = {}
    for metric in metrics:
        results[metric.name] = [metric.score(final_hypothesis, reference)]
    return results


def overlay_all_metrics_kde(df, col_prefix="value"):
    """
    Create subplots for all metrics overlaying original/cut/speed/both variants
    using KDE curves with light fills and legend below the title.
    """

    variants = ["original", "cut", "speed", "both"]
    colors = {"original": "blue", "cut": "orange", "speed": "green", "both": "pink"}

    # Detect metrics dynamically
    metric_names = sorted(
        {
            col.split("_")[2]  # e.g. both_value_CHRF_scores -> CHRF
            for col in df.columns
            if col.endswith("_scores") and f"_{col_prefix}_" in col
        }
    )

    n_metrics = len(metric_names)
    fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 5), sharey=True)

    # Make axes iterable if only one metric
    if n_metrics == 1:
        axes = [axes]

    for ax, metric in zip(axes, metric_names):
        for variant in variants:
            colname = f"{variant}_{col_prefix}_{metric}_scores"
            if colname not in df:
                continue
            try:
                values = np.concatenate(df[colname].dropna().to_list())
            except ValueError:
                values = np.array([])
            if len(values) == 0:
                continue
            values = values[np.isfinite(values)]
            kde = gaussian_kde(values)
            xs = np.linspace(np.min(values), np.max(values), 300)
            ys = kde(xs)
            ax.plot(xs, ys, label=variant, color=colors.get(variant, None), lw=2)
            # ax.fill_between(xs, 0, ys, color=colors.get(variant, None), alpha=0.25)

        ax.set_title(metric)
        ax.set_xlabel("Score")
        ax.grid(True, linestyle="--", alpha=0.4)

    axes[0].set_ylabel("Density")

    # Move legend below title, centered
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("SignWriting Metric Distributions (Overlayed by Variant)", fontsize=16)
    fig.legend(
        handles,
        labels,
        ncol=len(variants),
        fontsize=12,
        bbox_to_anchor=(0.5, 1.0),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(
        f"experiment_single_sign/scores_hists.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def count_empty_strings(df, col_prefix="value", counts=None):
    """
    Count space-only placeholder strings (" ") in SignWriting columns.
    """

    str_cols = [c for c in df.columns if c.endswith(col_prefix)]

    empty_counts = {}
    if counts is not None:
        for col in str_cols:
            empty_count = df[col].str.strip().eq("").sum()
            empty_counts[col] = empty_count
            total = empty_count - counts[col]
            print(f"Column '{col}' has {total} empty entries.")
    else:
        for col in str_cols:
            empty_count = df[col].str.strip().eq("").sum()
            empty_counts[col] = empty_count
            print(f"Column '{col}' has {empty_count} empty entries.")
    return empty_counts


def count_unique_values(df, col_prefix="value"):
    value_cols = [c for c in df.columns if c.endswith(col_prefix)]

    unique_counts = {}
    for col in value_cols:
        total = len(df[col])
        unique_counts[col] = df[col].str.strip().replace("", np.nan).dropna().nunique()
        percentage = (unique_counts[col] / total) * 100
        print(f"Column '{col}' unique values: {unique_counts[col]} ({percentage:.2f}%)")

    return unique_counts


def compare_length(df, col_prefix="value"):
    """
    Count NaN values in all SignWriting columns in df.
    """

    str_cols = [c for c in df.columns if c.endswith(col_prefix)]

    nan_counts = {}
    for col in str_cols:
        nan_count = df[col].isna().sum()
        nan_counts[col] = nan_count
        print(f"Column '{col}' NaN count:\n{nan_count}")

    return nan_counts


def compare_signwriting(res_df, sw_df, experiment=False):
    """
    Compare all SignWriting columns in res_df with
    SignWriting lists in sw_df, matched by stem and 'stem.mp4' filename.
    """

    # Prepare filename stem for matching
    sw = sw_df.copy()
    sw["stem_from_filename"] = sw["Filename"].str.replace(".mp4", "", regex=False)

    # Merge on stem
    merged = res_df.merge(
        sw, left_on="stem", right_on="stem_from_filename", how="left"
    ).rename(columns={"Signwriting": "reference", "value": "original_value"})

    # gloss_counts = merged[
    #    merged.duplicated(subset=["stem", "reference", "Gloss_x"], keep=False)
    # ]["stem"].value_counts()
    # print(gloss_counts)

    metrics = [
        SignWritingBLEU(),
        SignWritingCHRF(),
        SignWritingCLIPScore(),
        SignWritingSimilarityMetric(),
    ]
    # Identify SW columns
    list_cols = [c for c in merged.columns if c.endswith("_value")]

    # Create match columns for every list column
    for col in list_cols:
        newcol = f"{col}_matches"
        merged[newcol] = merged.apply(
            lambda row: any_match(row[col], row["reference"]), axis=1
        )
        # compute all metrics in one pass
        scores = merged.apply(
            lambda row: get_metrics(row[col], row["reference"], metrics), axis=1
        )

        # turn dicts into columns
        scores_expanded = pd.DataFrame(scores.tolist(), index=merged.index)

        # assign each metric column
        for metric in metrics:
            metric_name = metric.name
            merged[f"{col}_{metric_name}_scores"] = scores_expanded[metric_name]

    # 5. Combined flag for "any match in any list column"
    # match_cols = [c + "_matches" for c in list_cols]
    # merged["any_match"] = merged[match_cols].any(axis=1)
    # merged.drop_duplicates(
    #    subset=["stem", "Filename", "name", "reference"], inplace=True
    # )
    if experiment:
        plt.style.use("bmh")
        overlay_all_metrics_kde(merged, col_prefix="value")

    return merged


def summarize_lengths_and_means(merged_df, variants=None, col_prefix="value"):
    if variants is None:
        variants = ["original", "cut", "speed", "both"]

    # A dict that will map (variant, metric) → column Series
    nested_data = {}

    def avg_len(x):
        # x is a space-separated string; " " means empty
        if isinstance(x, str):
            x = x.strip()
            return 0 if x == "" else len(x.split())
        return np.nan

    for variant in variants:
        # ---- average length for the list column ----
        list_col = f"{variant}_{col_prefix}"
        if list_col in merged_df.columns:
            nested_data[(variant, "avg_len")] = merged_df[list_col].apply(avg_len)
        else:
            nested_data[(variant, "avg_len")] = np.nan

        # ---- collect all *_scores columns for this variant ----
        score_cols = [
            col
            for col in merged_df.columns
            if col.startswith(f"{variant}_{col_prefix}_") and col.endswith("_scores")
        ]

        for col in score_cols:
            # extract metric name inside: variant_value_<metric>_scores
            metric_name = re.sub(f"^{variant}_{col_prefix}_", "", col)
            metric_name = metric_name.replace("_scores", "")

            nested_data[(variant, metric_name)] = merged_df[col].apply(np.mean)

    # Build a DataFrame with MultiIndex columns
    summary_nested = pd.DataFrame(nested_data)

    # Sort for nicer display
    summary_nested = summary_nested.sort_index(axis=1, level=[0, 1])

    return summary_nested
