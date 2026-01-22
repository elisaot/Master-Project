# pip install pose-format
# videos_to_poses --format mediapipe --directory directory_of_videos/
import subprocess, sys
import importlib.util
import os
from pathlib import Path
from pose_format.pose import Pose
from pose_format.pose_visualizer import PoseVisualizer


def get_poses(dir: Path):
    # installing
    if importlib.util.find_spec("pose-format") is not None:
        print("Pose format already exists.")
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pose-format",
            ]
        )

    # testing for a single sign.
    subprocess.run(
        ["videos_to_poses", "--format", "mediapipe", "--directory", str(dir)]
    )


def visualize_pose(pose_dir: Path, output_dir: str):
    # Make output folder
    os.makedirs(str(output_dir), exist_ok=True)

    # Find all .pose files
    pose_files = sorted(pose_dir.glob("*.pose"))

    for pose_path in pose_files:
        # Read the .pose file
        with open(pose_path, "rb") as f:
            data_buffer = f.read()

        pose = Pose.read(data_buffer)  # , TorchPoseBody)

        # Visualize and save as video
        v = PoseVisualizer(pose)
        output_path = output_dir + f"{pose_path.stem}.mp4"
        v.save_video(output_path, v.draw())


def normalize_poses(input_dir: Path, output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)
    for pose_file in input_dir.glob("*.pose"):
        out_path = output_dir / pose_file.name

        # ---- SKIP IF ALREADY NORMALIZED (FILE EXISTS) ----
        if output_dir != input_dir:
            if out_path.exists():
                continue

        # ---- OTHERWISE NORMALIZE ----
        buf = pose_file.read_bytes()
        pose = Pose.read(buf)

        pose.normalize()  # apply repo’s built-in normalization

        with open(out_path, "wb") as f:
            pose.write(f)
    print("Normalization complete.")
