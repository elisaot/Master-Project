import os
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from moviepy.editor import VideoFileClip, vfx
from tqdm import tqdm
import pandas as pd


def process_single_video(input_path, output_folder, operation, speed_factor, cut_seconds, keep_original=False):
    """Process a single video and save result(s). Handles 'all' mode for multiple copies."""
    try:
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)

        if keep_original:
            orig_folder = os.path.join(output_folder, "originals")
            os.makedirs(orig_folder, exist_ok=True)
            shutil.copy2(input_path, os.path.join(orig_folder, base_name))

        ops_to_apply = []
        if operation == "all":
            ops_to_apply = ["speed", "cut", "both"]
        else:
            ops_to_apply = [operation]

        results = []

        for op in ops_to_apply:
            clip = VideoFileClip(input_path)
            duration = clip.duration

            if op == "speed":
                clip = clip.fx(vfx.speedx, speed_factor)
            elif op == "cut":
                start = min(cut_seconds, duration / 2)
                end = max(duration - cut_seconds, start)
                clip = clip.subclip(start, end)
            elif op == "both":
                start = min(cut_seconds, duration / 2)
                end = max(duration - cut_seconds, start)
                clip = clip.subclip(start, end)
                clip = clip.fx(vfx.speedx, speed_factor)

            out_name = f"{op}_{name}{ext}"
            out_path = os.path.join(output_folder, out_name)
            clip.write_videofile(
                out_path,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )
            clip.close()
            results.append(f"{out_name} processed")

        return "\n".join(results)

    except Exception as e:
        return f"Error processing {base_name}: {e}"


def process_videos_from_df(
    source_folder: str,
    output_folder: str,
    df: pd.DataFrame,
    filename_column: str = "filename",
    operation: str = "speed",
    speed_factor: float = 1.25,
    cut_seconds: float = 0.5,
    max_workers: int = None,
    keep_original: bool = False
):
    """Process only videos listed in a DataFrame."""
    os.makedirs(output_folder, exist_ok=True)

    selected_videos = df[filename_column].unique().tolist()
    print(f"Processing {len(selected_videos)} videos ({operation.upper()})...")

    tasks = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for filename in selected_videos:
            input_path = os.path.join(source_folder, filename)
            if not os.path.exists(input_path):
                print(f"Warning: {filename} not found in source folder.")
                continue
            tasks.append(
                executor.submit(
                    process_single_video,
                    input_path,
                    output_folder,
                    operation,
                    speed_factor,
                    cut_seconds,
                    keep_original
                )
            )

        for future in tqdm(as_completed(tasks), total=len(tasks), desc="Processing videos", ncols=90):
            tqdm.write(future.result())

    print("All videos processed!")


# === Example usage ===
if __name__ == "__main__":
    df_videos = pd.read_csv("../data_collection/tables/matched_single_signs.csv")

    process_videos_from_df(
        source_folder="../data_collection/scrape-SL/videos",
        output_folder="./results",
        df=df_videos,
        filename_column="Filename",
        operation="all",  # "speed", "cut", "both", or "all"
        speed_factor=1.25,
        cut_seconds=0.5,
        max_workers=4,
        keep_original=True
    )
