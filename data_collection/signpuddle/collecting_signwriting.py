import sqlite3
import csv

DB_FILE = "sgn69.db"  # change to your sqlite db filename
OUTPUT_FILE = "signpuddle_results.csv"


def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create a temporary view or perform a join in SQL that lowercases both sides for matching
    query = """
    SELECT DISTINCT t.id,
        t.term,
        e.sign,
        e.text AS description,
        t.lower AS cue
    FROM
        term t
    JOIN
        statped_dict s ON LOWER(s.word) = LOWER(t.term)
    JOIN
        entry e ON e.id = t.id;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Save to CSV file
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "term", "signwriting", "description", "cue"])  # header
        cleaned_rows = []
        for row in rows:
            id_, term, signwriting, description, cue = row

            # --- Split and keep only 'M' + last part if possible ---
            if signwriting and "M" in signwriting:
                parts = signwriting.split("M")
                # the last part after the final 'M'
                signwriting = "M" + parts[-1]
            else:
                # leave as-is if it doesn't contain 'M'
                signwriting = signwriting or ""

            cleaned_rows.append([id_, term, signwriting, description, cue])

        # --- Write cleaned rows ---
        writer.writerows(cleaned_rows)

    print(f"Saved {len(rows)} matched rows to {OUTPUT_FILE}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
