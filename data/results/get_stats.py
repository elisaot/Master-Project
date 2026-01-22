import argparse
import csv
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
from tqdm import tqdm


def get_video_info(video_path: Path):
    """Return (filename, duration_sec, frame_count) for a given video."""
    video = cv2.VideoCapture(str(video_path))
    if not video.isOpened():
        return (str(video_path.name), None, None)

    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps if fps and fps > 0 else 0

    video.release()
    return (str(video_path.name), duration, frame_count)


def process_videos_fast(videos_dir: Path, output_csv: Path, stats_txt: Path, workers=8):
    mp4_files = list(videos_dir.rglob("*.mp4"))
    if not mp4_files:
        print(f"No .mp4 files found in {videos_dir}")
        return

    print(f"Found {len(mp4_files)} video(s) in {videos_dir}")
    results = []
    failed = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(get_video_info, f): f for f in mp4_files}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing", unit="video"
        ):
            file_path = futures[future]
            try:
                filename, duration, frames = future.result()
                if duration is None:
                    failed.append(file_path)
                else:
                    results.append((filename, duration, frames))
            except Exception as e:
                failed.append(file_path)
                print(f"Error processing {file_path}: {e}")

    # Write CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Duration_sec", "Frame_Count"])
        writer.writerows(results)

    print(f"Wrote {len(results)} video stats to {output_csv}")

    # Write stats
    if results:
        durations = [r[1] for r in results]
        min_dur, max_dur = min(durations), max(durations)
        avg_dur = sum(durations) / len(durations)
        with open(stats_txt, "w", encoding="utf-8") as f:
            f.write(f"Video Duration Statistics (seconds):\n")
            f.write(f"Number of videos: {len(durations)}\n")
            f.write(f"Minimum duration: {min_dur:.2f}\n")
            f.write(f"Maximum duration: {max_dur:.2f}\n")
            f.write(f"Average duration: {avg_dur:.2f}\n")

        print(f"Stats saved to {stats_txt}")

    # Log failures
    if failed:
        failed_log = output_csv.with_name("failed_videos.txt")
        with open(failed_log, "w", encoding="utf-8") as f:
            f.write("\n".join(str(f) for f in failed))
        print(f"{len(failed)} video(s) failed. See {failed_log}")


def main():
    parser = argparse.ArgumentParser(
        description="Fast local video stats extractor using OpenCV."
    )
    parser.add_argument(
        "--videos_dir", type=Path, required=True, help="Directory with .mp4 files"
    )
    parser.add_argument(
        "--output_dir", type=Path, default=Path.cwd(), help="Output directory"
    )
    parser.add_argument(
        "--filename", type=str, required=True, help="Base filename for output"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="Number of parallel workers"
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = args.output_dir / f"{args.filename}.csv"
    stats_txt = args.output_dir / f"{args.filename}_stats.txt"

    process_videos_fast(args.videos_dir, output_csv, stats_txt, workers=args.workers)


if __name__ == "__main__":
    main()
