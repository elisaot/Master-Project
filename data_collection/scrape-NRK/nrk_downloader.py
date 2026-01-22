#!/usr/bin/env python3
"""
NRK Tegnspråknytt Video Downloader
Downloads videos and subtitles from NRK's sign language news program with Norwegian subtitles.
Designed to work with uv for automatic dependency management.
"""

import sys
from pathlib import Path
from datetime import datetime
import yt_dlp
from tqdm import tqdm


def create_download_directory():
    """Create download directory structure"""
    videos_dir = Path("../data/nrk_tegnspraaknytt")
    videos_dir.mkdir(parents=True, exist_ok=True)

    return videos_dir


def get_norwegian_subtitles(video_info, preferred_langs=None):
    """
    Check a video's subtitles and return whether it has Norwegian subtitles
    and which languages are available.

    Args:
        video_info (dict): Video info dictionary from yt-dlp.
        preferred_langs (list): List of preferred Norwegian subtitle codes.

    Returns:
        has_subtitles (bool): True if any preferred Norwegian subtitles exist.
        subtitle_langs (list): List of matched subtitle languages.
    """
    if preferred_langs is None:
        preferred_langs = ["nb-ttv", "no", "nb", "nn"]

    subtitle_langs = []
    has_subtitles = False

    # Manual subtitles
    subtitles = video_info.get("subtitles") or {}
    for lang in preferred_langs:
        if lang in subtitles:
            has_subtitles = True
            subtitle_langs.append(lang)
            break

    # Automatic subtitles if no manual ones found
    if not has_subtitles:
        automatic_captions = video_info.get("automatic_captions") or {}
        for lang in preferred_langs:
            if lang in automatic_captions:
                has_subtitles = True
                subtitle_langs.append(f"{lang} (auto)")
                break

    return has_subtitles, subtitle_langs


def check_subtitles_availability(url, max_videos=5):
    """Check which videos have subtitles available"""
    # Options for extracting video info only
    info_opts = {
        "quiet": True,
        "extract_flat": False,
        "playlist_end": max_videos,
        "ignoreerrors": True,
    }

    videos_with_subtitles = []

    try:
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            print("Checking for videos with available subtitles...")

            # Extract playlist info
            playlist_info = ydl.extract_info(url, download=False)

            if "entries" not in playlist_info:
                print("No playlist entries found")
                return videos_with_subtitles

            total_videos = len(playlist_info["entries"])
            print(f"Found {total_videos} videos in playlist")
            used_videos = playlist_info["entries"][:max_videos]

            for i, entry in enumerate(used_videos, 1):
                if entry is None:
                    continue
                # video_info = ydl.extract_info(entry["url"], download=False)
                try:
                    # Extract detailed info for each video
                    video_info = entry  # ydl.extract_info(entry["url"], download=False)

                    if video_info is None:
                        continue

                    title = video_info.get("title", "Unknown")
                    video_id = video_info.get("id", "unknown")

                    # Use helper function
                    has_subtitles, subtitle_langs = get_norwegian_subtitles(video_info)

                    if has_subtitles:
                        videos_with_subtitles.append(
                            {
                                "url": video_info.get("webpage_url")
                                or video_info.get("url"),
                                "title": title,
                                "id": video_id,
                                "subtitle_langs": subtitle_langs,
                            }
                        )
                        print(
                            f"✓ [{i:3d}/{total_videos}] {title[:60]}... (Subtitles: {', '.join(subtitle_langs)})"
                        )

                    else:
                        print(
                            f"✗ [{i:3d}/{total_videos}] {title[:60]}... (No Norwegian subtitles)"
                        )

                except Exception as e:
                    print(f"✗ [{i:3d}/{total_videos}] Error checking video: {str(e)}")
                    continue

    except Exception as e:
        print(f"Error extracting playlist info: {str(e)}")
        return videos_with_subtitles

    print(f"\nFound {len(videos_with_subtitles)} videos with Norwegian subtitles")
    return videos_with_subtitles


def download_videos(videos_with_subtitles, videos_dir):
    """Download only videos that have subtitles available"""

    # yt-dlp options for downloading
    ydl_opts = {
        "format": "mp4",  # Download best quality up to 720p
        "outtmpl": str(videos_dir / "%(title)s.%(ext)s"),
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["nb-ttv", "no", "nb", "nn"],  # Norwegian language subtitles
        "subtitlesformat": "vtt",
        "ignoreerrors": True,  # Continue on errors
        "writethumbnail": False,
        "writeinfojson": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(
                f"\nStarting download of {len(videos_with_subtitles)} videos with subtitles"
            )
            print(f"Download directory: {videos_dir}")
            print("-" * 50)

            successful_downloads = 0
            skipped_downloads = 0
            failed_downloads = 0

            for i, video in enumerate(videos_with_subtitles, 1):
                title = video["title"]

                # Expected filenames
                video_file = videos_dir / f"{title}.mp4"

                # Subtitle files may have one of several suffix patterns
                subtitle_patterns = [
                    videos_dir / f"{title}.*.vtt",
                    videos_dir / f"{title}.vtt",
                ]

                # Check if video and subtitles already exist
                subtitle_exists = any(
                    list(videos_dir.glob(p.name)) for p in subtitle_patterns
                )
                video_exists = video_file.exists()

                if video_exists and subtitle_exists:
                    print(
                        f"[{i:3d}/{len(videos_with_subtitles)}] Skipping (already downloaded): {title[:50]}"
                    )
                    skipped_downloads += 1
                    continue

                # Otherwise, download
                try:
                    print(
                        f"[{i:3d}/{len(videos_with_subtitles)}] Downloading: {video['title'][:50]}..."
                    )
                    ydl.download([video["url"]])
                    successful_downloads += 1
                    print(f"✓ Successfully downloaded: {video['title'][:50]}...")
                except Exception as e:
                    print(f"✗ Failed to download {video['title'][:50]}...: {str(e)}")
                    failed_downloads += 1
                    continue

            print("\n" + "=" * 50)
            print(f"Download Summary:")
            print(f"- Successful: {successful_downloads}")
            print(f"- Failed: {failed_downloads}")
            print(f"- Total attempted: {len(videos_with_subtitles)}")

    except Exception as e:
        print(f"Error during download: {str(e)}")
        return False

    return True


def create_download_log(videos_with_subtitles, videos_dir):
    """Create a log file with download information"""
    log_file = "download_log.txt"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"NRK Tegnspråknytt Download Log\n")
        f.write(f"{'='*40}\n")
        f.write(f"Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source URL: https://tv.nrk.no/serie/tegnspraaknytt\n")
        f.write(f"Filter: Only videos with Norwegian subtitles\n")
        f.write(f"Videos with subtitles found: {len(videos_with_subtitles)}\n\n")

        video_files = (
            list(videos_dir.glob("*.mp4"))
            + list(videos_dir.glob("*.mkv"))
            + list(videos_dir.glob("*.webm"))
        )
        subtitle_files = list(videos_dir.glob("*.vtt")) + list(videos_dir.glob("*.srt"))

        f.write(f"Actually Downloaded Files:\n")
        f.write(f"- Videos: {len(video_files)}\n")
        f.write(f"- Subtitles: {len(subtitle_files)}\n\n")

        # List videos that were identified as having subtitles
        f.write(f"Videos with Subtitles (identified for download):\n")
        f.write(f"{'-'*60}\n")
        for i, video in enumerate(videos_with_subtitles, 1):
            f.write(f"{i:3d}. {video['title']}\n")
            f.write(f"     ID: {video['id']}\n")
            f.write(f"     Subtitles: {', '.join(video['subtitle_langs'])}\n")
            f.write(f"     URL: {video['url']}\n\n")

        if video_files:
            f.write(f"Downloaded Video Files:\n")
            f.write(f"{'-'*30}\n")
            for video_file in sorted(video_files):
                f.write(f"- {video_file.name}\n")

        if subtitle_files:
            f.write(f"\nDownloaded Subtitle Files:\n")
            f.write(f"{'-'*35}\n")
            for subtitle_file in sorted(subtitle_files):
                f.write(f"- {subtitle_file.name}\n")


def main():
    """Main function"""
    print("NRK Tegnspråknytt Video Downloader (Subtitles Required)")
    print("=" * 55)

    # List of NRK URLs to process
    urls = [
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202510",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202509",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202508",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202507",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202506",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202505",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202504",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202503",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202502",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202501",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202412",
        "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202411",
    ]

    max_videos = 30  # Limit number of videos per URL

    # Create directory structure once
    print("Creating download directories...")
    videos_dir = create_download_directory()

    try:
        # Loop through each URL with progress bar
        for url in tqdm(urls, desc="Processing URLs", unit="url"):
            print(f"\n\nChecking for videos with subtitles at: {url}")

            # First pass: check which videos have subtitles
            videos_with_subtitles = check_subtitles_availability(url, max_videos)

            if not videos_with_subtitles:
                print(f"No videos with subtitles found for {url}")
                continue

            print(f"Found {len(videos_with_subtitles)} videos with subtitles.")

            try:
                input("Press Enter to continue or Ctrl+C to skip...")
            except KeyboardInterrupt:
                print("\nSkipping this URL...")
                continue

            # Second pass: download only videos with subtitles
            success = download_videos(videos_with_subtitles, videos_dir)

            if success:
                create_download_log(videos_with_subtitles, videos_dir)
                print(f"Download completed for {url}")
            else:
                print(f"Download failed for {url}")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Exiting...")
        return 1

    print("\n" + "=" * 55)
    print("All URLs processed!")
    print(f"Files saved to: {videos_dir.absolute()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
