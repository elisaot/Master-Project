from pathlib import Path
import os
from segmentation import run_segmentation
from transcription import run_transcription
from pose import get_poses, visualize_pose, normalize_poses
from tqdm import tqdm


def only_contains_dirs_pathlib(directory_path):
    """Checks if a directory only contains subdirectories using pathlib."""
    return all(entry.is_dir() for entry in directory_path.iterdir())


if __name__ == "__main__":
    dir = "../data/processed_NRK"
    # directory containing your .pose and .mp4 files
    data_dir = Path(dir)
    # make .pose files in video directory
    if only_contains_dirs_pathlib(data_dir):
        subdirectories = list(data_dir.iterdir())
        for subdir in tqdm(subdirectories, desc="Processing subdirectories:"):
            tqdm.write(f"Processing subdirectory: {subdir}")
            if any(subdir.glob("*.eaf")) and any(
                subdir.glob("*.bak")
            ):  # Superficial check, does not guarantee processing of all files in subdir is done.
                tqdm.write(f"Skipping {subdir}: .eaf and .bak files found")
                continue
            else:
                # get_poses(subdir)
                # normalize_poses(subdir, subdir)
                # run_segmentation(subdir)
                run_transcription(subdir)

    else:
        get_poses(data_dir)
        # create visuals of the poses. Optional:
        # visualize_pose(data_dir, "pose_visuals/")
        # normalize the poses
        normalize_poses(data_dir, data_dir)

        # creating .eaf (segmentations) files for the poses
        run_segmentation(data_dir)

        # creating SignWriting annotations of the .pose files
        run_transcription(data_dir)
