import pandas as pd
from pathlib import Path
import sqlite3
import requests
import xml.etree.ElementTree as ET
import csv
import re


def clean_modified(value):
    s = str(value).strip()

    # 1. If the string is a numeric ratio like "2:3"
    if re.fullmatch(r"\d+:\d+.*", s):
        cleaned = s
    else:
        # 2. Colon-separated string
        m = re.match(r"([^:]+):\s*(.+)", s)
        if m:
            if m.group(2).strip() == "stor":
                cleaned = m.group(1).strip()  # keep only before colon
            else:
                cleaned = m.group(2).strip()  # keep after colon
        else:
            cleaned = s

    # 3. Remove parentheses and everything after
    cleaned = re.sub(r"\(.*", "", cleaned)

    # 4. Remove digits only if **after letters**
    cleaned = re.sub(r"(?<=[A-Za-z] )\d+", "", cleaned)

    # 5. Optionally remove /, ? characters
    cleaned = re.sub(r"[/\?].*", "", cleaned)

    return cleaned.strip()


def ascii_to_norwegian(s):
    if not isinstance(s, str):
        return s
    mapping = {
        "aa": "å",
        "ae": "æ",
        "oe": "ø",
        "AA": "Å",
        "AE": "Æ",
        "OE": "Ø",
    }
    for ascii_seq, norwegian_char in mapping.items():
        s = s.replace(ascii_seq, norwegian_char)
    return s


def statped_dict_tabs(
    xml_url: str,
    video_folder_1: Path,
    video_folder_2: Path,
    output_csv_1: Path,
    output_csv_2: Path,
):
    """Fetch XML, match filenames with videos in two folders, and save separate tables"""

    # Fetch XML
    try:
        response = requests.get(xml_url, timeout=30)
        response.raise_for_status()
        xml_data = response.content
    except requests.RequestException as e:
        print(f"Failed to fetch XML: {e}")
        return

    # Parse XML
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return

    # Extract all entries from XML
    entries = []
    for elem in root.iter():
        filnavn = elem.get("filnavn")
        if filnavn:
            visningsord = elem.get("visningsord", "")
            beskrivelse = elem.get("kommetarviss", "")
            kommentar = elem.get("kommentar", "")
            entries.append((filnavn, visningsord, beskrivelse, kommentar))

    # Match entries to videos in each folder
    def match_videos(video_folder: Path):
        return [row for row in entries if (video_folder / f"{row[0]}.mp4").exists()]

    table1 = match_videos(video_folder_1)
    table2 = match_videos(video_folder_2)

    # Helper function to write a CSV
    def write_csv(rows, output_csv):
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Gloss", "Description", "Comment"])
            for filnavn, visningsord, beskrivelse, kommentar in rows:
                if filnavn == "null":
                    writer.writerow([f"{filnavn}.mp4", "null", beskrivelse, kommentar])
                else:
                    writer.writerow(
                        [f"{filnavn}.mp4", visningsord, beskrivelse, kommentar]
                    )

    # Write both CSVs
    write_csv(table1, output_csv_1)
    write_csv(table2, output_csv_2)

    print(f"Saved {len(table1)} rows of single signs from Statped to {output_csv_1}")
    print(
        f"Saved {len(table2)} rows of continous videos from Statped to {output_csv_2}"
    )


def signpuddle_tab(output: Path):
    DB_FILE = "../signpuddle/sgn69.db"  # Change to your SQLite database filename
    output_file = output / "signpuddle_dict.csv"  # Output CSV file

    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Query to get term and sign
    query = """
    SELECT t.lower, e.sign
    FROM term t
    JOIN entry e ON e.id = t.id
    WHERE t.prime = 1
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Optional: clean the sign like your previous logic
    cleaned_rows = []
    for term, sign in rows:
        if sign and "M" in sign:
            parts = sign.split("M")
            sign = "M" + parts[-1]  # keep only the last 'M...' part
        else:
            sign = sign or ""
        cleaned_rows.append([term, sign])

    df = pd.DataFrame(cleaned_rows, columns=["Gloss", "Signwriting"])
    df["Gloss"] = df["Gloss"].apply(ascii_to_norwegian)
    df["Gloss"] = df["Gloss"].str.replace("-", " ", regex=False)
    df.drop_duplicates(inplace=True)

    df["modified"] = df["Gloss"]
    df["modified"] = df["modified"].apply(clean_modified)
    df["modified"] = df["modified"].str.strip()
    df.drop_duplicates(subset=["modified", "Signwriting"], inplace=True)
    # Save to CSV
    df.to_csv(output_file, index=False)

    print(f"Saved {len(df)} rows of Signpuddle entries to {output_file}")

    # Close connections
    cursor.close()
    conn.close()


def merged_tabs(output_path, table1, table2):
    output_file1 = output_path / "merged_single_signs.csv"
    output_file2 = output_path / "matched_single_signs.csv"

    # Load the CSVs
    df1 = pd.read_csv(table1)
    df2 = pd.read_csv(table2)

    # Step 1: Replace '-' with ' '
    df1["modified"] = df1["Gloss"].str.replace("-", " ", regex=False)
    df1["modified"] = df1["modified"].apply(clean_modified)
    df1["modified"] = df1["modified"].str.strip()
    df1["modified"] = df1["modified"].str.lower()

    merged_df = pd.merge(df1, df2, on="modified", how="outer")
    # Save to a new CSV if needed
    merged_df.to_csv(output_file1, index=False)

    # Inner join
    match_df = pd.merge(df1, df2, on="modified", how="inner")
    match_df.to_csv(output_file2, index=False)

    print(
        f"Saved {len(merged_df)} rows of Signpuddle and single signs to {output_file1}"
    )
    print(
        f"Saved {len(match_df)} rows of matches of Signpuddle and single signs to {output_file2}"
    )


if __name__ == "__main__":
    output_path = Path("tables")
    output_path.mkdir(exist_ok=True)

    # Folder to iterate through
    video_folder_1 = Path("../videos")
    output_csv_1 = output_path / "statped_dict.csv"
    video_folder_2 = Path("../unexpected_vid")
    output_csv_2 = output_path / "unexpected_vid.csv"

    statped_dict_tabs(
        "https://www.minetegn.no/tegnordbok/xml/tegnordbok.php",
        video_folder_1,
        video_folder_2,
        output_csv_1,
        output_csv_2,
    )
    signpuddle_tab(output_path)

    merged_tabs(output_path, output_csv_1, output_path / "signpuddle_dict.csv")

"""
Saved 9119 rows of single signs from Statped to tables/statped_dict.csv
Saved 1033 rows of continous videos from Statped to tables/unexpected_vid.csv
Saved 6362 rows of Signpuddle entries to tables/signpuddle_dict.csv
Saved 15012 rows of Signpuddle and single signs to tables/merged_single_signs.csv
Saved 5694 rows of matches of Signpuddle and single signs to tables/matched_single_signs.csv
"""
