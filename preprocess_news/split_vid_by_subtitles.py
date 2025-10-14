import os
import pysrt
from moviepy import VideoFileClip

# === CONFIG ===
video_path = "data/Tegnspråknytt - 18. august-NNFA91081825-kopi.mp4"  # your input video
ttv_path = (
    "data/Tegnspråknytt - 18. august-NNFA91081825.nb-ttv.vtt"  # your .ttv subtitle file
)
output_dir = "clips"  # folder for the output clips

# === SETUP ===
os.makedirs(output_dir, exist_ok=True)

# pysrt can parse .ttv just like .srt
subs = pysrt.open(ttv_path, encoding="utf-8")
video = VideoFileClip(video_path)

# === SPLIT LOOP ===
for i, sub in enumerate(subs, start=1):
    start = sub.start.ordinal / 1000.0  # milliseconds → seconds
    end = sub.end.ordinal / 1000.0
    text = sub.text.strip().replace("\n", " ")

    # create subclip
    clip = video.subclipped(start, end)
    output_file = os.path.join(output_dir, f"clip_{i:03d}.mp4")

    print(f"Saving clip {i}: {start:.2f}s → {end:.2f}s — “{text[:40]}”")
    clip.write_videofile(output_file, codec="libx264", audio_codec="aac", logger=None)

print("\nDone! All clips saved in:", output_dir)
