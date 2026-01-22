import os
import glob
import pysrt
from moviepy.editor import VideoFileClip
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# === CONFIG ===
video_folder = "../data/nrk_tegnspraaknytt"  # folder containing multiple video files
output_base_dir = "../data/processed_nrk"  # base folder for all clips
max_workers = 4  # number of videos to process in parallel

# Create base output folder
os.makedirs(output_base_dir, exist_ok=True)

# Supported video extensions
video_extensions = ("*.mp4", "*.mov", "*.mkv", "*.avi")

# Gather all video files
video_files = []
for ext in video_extensions:
    video_files.extend(glob.glob(os.path.join(video_folder, ext)))


def process_video(video_path):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(output_base_dir, video_name)
    os.makedirs(output_dir, exist_ok=True)

    ttv_path = os.path.join(video_folder, video_name + ".nb-ttv.vtt")
    if not os.path.exists(ttv_path):
        print(f"Warning: No subtitle found for {video_name}, skipping.")
        return f"Skipped {video_name}"

    print(f"\nProcessing video: {video_name}")

    # Load subtitles and video
    subs = pysrt.open(ttv_path, encoding="utf-8")
    video = VideoFileClip(video_path)

    for i, sub in enumerate(tqdm(subs, desc=f"{video_name}", unit="clip"), start=1):
        start = sub.start.ordinal / 1000.0
        end = sub.end.ordinal / 1000.0

        clip = video.subclip(start, end)
        output_file = os.path.join(output_dir, f"clip_{i:03d}.mp4")
        clip.write_videofile(
            output_file, codec="libx264", audio_codec="aac", logger=None
        )

    video.close()
    return f"Finished {video_name}"


results = []
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(process_video, vf) for vf in video_files]

    for f in tqdm(
        as_completed(futures), total=len(futures), desc="Videos", unit="video"
    ):
        results.append(f.result())

# Print final summary
print("\nAll videos processed. Clips saved in:", output_base_dir)
for r in results:
    print(r)
