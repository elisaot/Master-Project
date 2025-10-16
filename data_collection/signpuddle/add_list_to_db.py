import sqlite3


def load_words_from_txt(txt_filename):
    with open(txt_filename, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    return words


def save_words_to_db(words, db_filename="sgn69.db"):
    # Remove duplicates by converting to set
    unique_words = set(words)

    # Connect to local SQLite DB (creates file if not exists)
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS statped_dict (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE
    )
    """
    )

    # Insert unique words, ignore duplicates due to UNIQUE constraint
    for word in unique_words:
        cursor.execute("INSERT OR IGNORE INTO statped_dict (word) VALUES (?)", (word,))

    # Commit and close connection
    conn.commit()
    conn.close()

    print(f"Inserted {len(unique_words)} unique words into database.")


if __name__ == "__main__":
    txt_file = "words_list.txt"  # change this to your actual filename
    words = load_words_from_txt(txt_file)
    save_words_to_db(words)
