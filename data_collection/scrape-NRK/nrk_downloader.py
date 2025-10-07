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


def create_download_directory():
    """Create download directory structure"""
    base_dir = Path("nrk_tegnspraaknytt")
    videos_dir = base_dir / "videos"
    subtitles_dir = base_dir / "subtitles"

    videos_dir.mkdir(parents=True, exist_ok=True)
    subtitles_dir.mkdir(parents=True, exist_ok=True)

    return base_dir, videos_dir, subtitles_dir


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

                    # Check for subtitles
                    has_subtitles = False
                    subtitle_langs = []

                    # Check manual subtitles
                    if video_info.get("subtitles"):
                        keys = list(video_info.get("subtitles").keys())
                        for lang in ["nb-ttv", "no", "nb", "nn"]:
                            if lang == keys[0]:
                                has_subtitles = True

                                subtitle_langs.append(lang)
                                break

                    # Check automatic subtitles if no manual ones found
                    if not has_subtitles and video_info.get("automatic_captions"):
                        for lang in ["nb-ttv", "no", "nb", "nn"]:
                            if lang in video_info["automatic_captions"]:
                                has_subtitles = True
                                subtitle_langs.append(f"{lang} (auto)")
                                break

                    if has_subtitles:
                        videos_with_subtitles.append(
                            {
                                "url": url + "episode" + str(video_id),
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


def download_videos(videos_with_subtitles, base_dir, videos_dir, subtitles_dir):
    """Download only videos that have subtitles available"""

    if not videos_with_subtitles:
        print("No videos with subtitles found to download")
        return False

    # yt-dlp options for downloading
    ydl_opts = {
        "format": "mp4",
        "outtmpl": str(videos_dir / "%(title)s-%(id)s.%(ext)s"),
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
            print(f"Subtitles directory: {subtitles_dir}")
            print("-" * 50)

            successful_downloads = 0
            failed_downloads = 0

            for i, video in enumerate(videos_with_subtitles, 1):
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


def organize_subtitles(base_dir, subtitles_dir):
    """Move subtitle files to subtitles directory"""
    videos_dir = base_dir / "videos"

    # Find all subtitle files in videos directory
    subtitle_files = list(videos_dir.glob("*.vtt")) + list(videos_dir.glob("*.srt"))

    if subtitle_files:
        print(f"\nOrganizing {len(subtitle_files)} subtitle files...")
        for subtitle_file in subtitle_files:
            try:
                destination = subtitles_dir / subtitle_file.name
                subtitle_file.rename(destination)
                print(f"Moved: {subtitle_file.name}")
            except Exception as e:
                print(f"Error moving {subtitle_file.name}: {str(e)}")


def create_download_log(base_dir, videos_with_subtitles):
    """Create a log file with download information"""
    log_file = base_dir / "download_log.txt"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"NRK Tegnspråknytt Download Log\n")
        f.write(f"{'='*40}\n")
        f.write(f"Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source URL: https://tv.nrk.no/serie/tegnspraaknytt\n")
        f.write(f"Filter: Only videos with Norwegian subtitles\n")
        f.write(f"Videos with subtitles found: {len(videos_with_subtitles)}\n\n")

        # Count downloaded files
        videos_dir = base_dir / "videos"
        subtitles_dir = base_dir / "subtitles"

        video_files = (
            list(videos_dir.glob("*.mp4"))
            + list(videos_dir.glob("*.mkv"))
            + list(videos_dir.glob("*.webm"))
        )
        subtitle_files = list(subtitles_dir.glob("*.vtt")) + list(
            subtitles_dir.glob("*.srt")
        )

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

    # URL to download from
    url = "https://tv.nrk.no/serie/tegnspraaknytt/sesong/202508"
    max_videos = 5  # Change this to limit the number of videos to check

    # Create directory structure
    print("Creating download directories...")
    base_dir, videos_dir, subtitles_dir = create_download_directory()

    # First pass: Check which videos have subtitles
    videos_with_subtitles = check_subtitles_availability(url, max_videos)

    if not videos_with_subtitles:
        print("\nNo videos with Norwegian subtitles found!")
        return 1

    print(
        f"\nProceeding to download {len(videos_with_subtitles)} videos with subtitles..."
    )
    input("Press Enter to continue or Ctrl+C to cancel...")

    # Second pass: Download only videos with subtitles
    success = download_videos(
        videos_with_subtitles, base_dir, videos_dir, subtitles_dir
    )

    if success:
        # Organize subtitle files
        organize_subtitles(base_dir, subtitles_dir)

        # Create download log
        create_download_log(base_dir, videos_with_subtitles)

        print("\n" + "=" * 50)
        print("Download completed!")
        print(f"Downloaded videos with subtitles: {len(videos_with_subtitles)}")
        print(f"Files saved to: {base_dir.absolute()}")
        print(f"Check download_log.txt for details.")
    else:
        print("Download failed or completed with errors.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
