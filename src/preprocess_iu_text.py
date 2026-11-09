
import pandas as pd
import re
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "iu_reports.csv"
OUTPUT_FILE = ROOT / "results" / "iu_reports_preprocessed.csv"


def clean_text(text):
    """Clean clinical text without changing its medical meaning."""

    if pd.isna(text):
        return ""

    text = str(text)

    # Normalize spaces and line breaks
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def main():

    print("Loading IU X-Ray reports...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Reports loaded: {len(df)}")

    # Clean clinical sections
    text_columns = [
        "indication",
        "findings",
        "impression",
        "comparison"
    ]

    for column in text_columns:
        df[column] = df[column].apply(clean_text)

    # Combine clinically relevant sections
    df["report_text"] = (
        "Indication: " + df["indication"] +
        " Findings: " + df["findings"] +
        " Impression: " + df["impression"]
    )

    # Remove reports with no useful clinical text
    before = len(df)

    df = df[
        (df["findings"] != "") |
        (df["impression"] != "")
    ].copy()

    removed = before - len(df)

    # Track availability of clinical sections
    df["has_findings"] = df["findings"].str.strip() != ""
    df["has_impression"] = df["impression"].str.strip() != ""

    # Display section statistics
    print("\nSECTION AVAILABILITY:")
    print(df["has_findings"].value_counts())
    print(df["has_impression"].value_counts())

    # Save processed dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
)

    print("\nText preprocessing completed!")
    print(f"Reports before filtering: {before}")
    print(f"Reports removed: {removed}")
    print(f"Reports retained: {len(df)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nExample processed report:")
    print(df["report_text"].iloc[0])


if __name__ == "__main__":
    main()
