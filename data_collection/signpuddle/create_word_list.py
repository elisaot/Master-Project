import re
import unicodedata
import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from urllib.parse import urljoin
import requests
import sys


def clean_word(word):
    word = unicodedata.normalize("NFC", word)
    match = re.match(r"^[a-zA-ZæøåÆØÅ\s]+", word)
    if match:
        return match.group(0).strip()
    else:
        return word.strip()


class WordListScraper:
    def __init__(
        self,
        base_url="https://www.minetegn.no",
        xml_endpoint="/tegnordbok/xml/tegnordbok.php",
        output_file="words_list.txt",
    ):
        self.base_url = base_url
        self.xml_endpoint = xml_endpoint
        self.output_file = Path(output_file)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def fetch_xml_data(self):
        """Fetch and parse XML data from the API endpoint"""
        url = urljoin(self.base_url, self.xml_endpoint)
        logging.info(f"Fetching XML data from: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            logging.info(
                f"XML data fetched successfully. Size: {len(response.content)} bytes"
            )
            return response.content
        except requests.RequestException as e:
            logging.error(f"Failed to fetch XML data: {e}")
            return None

    def parse_xml_and_extract_words(self, xml_data):
        try:
            root = ET.fromstring(xml_data)
            words = []

            for elem in root.iter():
                filnavn = elem.get("filnavn")
                if filnavn:
                    cleaned = clean_word(filnavn)
                    if cleaned:
                        words.append(cleaned)

            logging.info(f"Found {len(words)} cleaned words")
            return words
        except ET.ParseError as e:
            logging.error(f"Failed to parse XML: {e}")
            return []

    def save_words_to_file(self, words):
        """Save the list of words to a file"""
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for word in words:
                    f.write(word + "\n")
            logging.info(f"Saved {len(words)} words to {self.output_file}")
        except Exception as e:
            logging.error(f"Failed to save words to file: {e}")

    def run(self):
        """Main workflow"""
        logging.info("Starting word list scraping process")

        xml_data = self.fetch_xml_data()
        if not xml_data:
            logging.error("Failed to fetch XML data. Exiting.")
            return False

        words = self.parse_xml_and_extract_words(xml_data)
        if not words:
            logging.error("No words found in XML. Exiting.")
            return False

        self.save_words_to_file(words)
        logging.info("Scraping complete!")
        return True


def main():
    scraper = WordListScraper()

    try:
        success = scraper.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
