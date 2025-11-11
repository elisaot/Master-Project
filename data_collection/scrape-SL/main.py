#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import time
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from urllib.parse import urljoin
import sys
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraping.log"), logging.StreamHandler()],
)


class VideoScraper:
    def __init__(
        self,
        base_url="https://www.minetegn.no",
        xml_endpoint="/tegnordbok/xml/tegnordbok.php",
        video_path="/Tegnordbok-HTML/video_/",
        output_dir="videos",
        alt_output ="unexpected_vid",
        max_workers=None,
    ):
        self.base_url = base_url
        self.xml_endpoint = xml_endpoint
        self.video_path = video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.alt_output = Path(alt_output)
        self.alt_output.mkdir(exist_ok=True)
        self.max_workers = max_workers or min(8, cpu_count())
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

    def parse_xml_and_extract_filenames(self, xml_data):
        """Parse XML and extract filnavn attributes"""
        try:
            root = ET.fromstring(xml_data)
            filenames = []

            # Find all elements with filnavn attribute
            for elem in root.iter():
                filnavn = elem.get("filnavn")
                if filnavn:
                    filenames.append(filnavn)

            logging.info(f"Found {len(filenames)} video filenames")
            return filenames
        except ET.ParseError as e:
            logging.error(f"Failed to parse XML: {e}")
            return []

    def construct_video_url(self, filename):
        """Construct video URL from filename"""
        return f"{self.base_url}{self.video_path}{filename}.mp4"

    def download_video(self, filename):
        """Download a single video file"""
        url = self.construct_video_url(filename)

        # Pattern for unexpected videos
        pattern = r"^M\d+_\d+"
        if re.match(pattern, filename):
            output_path = self.alt_output / f"{filename}.mp4"
        else:
            output_path = self.output_dir / f"{filename}.mp4"

        # Skip if file already exists
        if output_path.exists():
            logging.info(f"Skipping {filename}.mp4 - already exists")
            return {
                "filename": filename,
                "status": "skipped",
                "message": "File already exists",
            }

        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = output_path.stat().st_size
            logging.info(f"Downloaded {filename}.mp4 ({file_size:,} bytes)")
            return {"filename": filename, "status": "success", "size": file_size}

        except requests.RequestException as e:
            logging.error(f"Failed to download {filename}.mp4: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial file
            return {"filename": filename, "status": "failed", "error": str(e)}
        except Exception as e:
            logging.error(f"Unexpected error downloading {filename}.mp4: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial file
            return {"filename": filename, "status": "failed", "error": str(e)}

    def download_videos_parallel(self, filenames, test_mode=False):
        """Download videos in parallel using multiprocessing"""
        if test_mode:
            logging.info("TEST MODE: Only downloading first 5 videos")
            filenames = filenames[:5]

        logging.info(
            f"Starting parallel download of {len(filenames)} videos using {self.max_workers} workers"
        )

        results = {"success": 0, "failed": 0, "skipped": 0}

        with Pool(processes=self.max_workers) as pool:
            # Use tqdm for progress bar
            with tqdm(total=len(filenames), desc="Downloading videos") as pbar:
                for result in pool.imap_unordered(self.download_video, filenames):
                    results[result["status"]] += 1
                    pbar.set_postfix(
                        Success=results["success"],
                        Failed=results["failed"],
                        Skipped=results["skipped"],
                    )
                    pbar.update(1)

                    # Add small delay to be respectful
                    time.sleep(0.1)

        logging.info(f"Download complete. Results: {results}")
        return results

    def run(self, test_mode=False):
        """Main scraping workflow"""
        logging.info("Starting video scraping process")

        # Fetch XML data
        xml_data = self.fetch_xml_data()
        if not xml_data:
            logging.error("Failed to fetch XML data. Exiting.")
            return False

        # Parse XML and extract filenames
        filenames = self.parse_xml_and_extract_filenames(xml_data)
        if not filenames:
            logging.error("No filenames found in XML. Exiting.")
            return False

        # Download videos
        results = self.download_videos_parallel(filenames, test_mode)

        # Summary
        total_files = len(filenames)
        logging.info(f"Scraping complete!")
        logging.info(f"Total files: {total_files}")
        logging.info(f"Successfully downloaded: {results['success']}")
        logging.info(f"Failed downloads: {results['failed']}")
        logging.info(f"Skipped (already exist): {results['skipped']}")

        return True


def main():
    """Main entry point"""
    scraper = VideoScraper()

    # Check if test mode is requested
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"

    try:
        success = scraper.run(test_mode=test_mode)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
