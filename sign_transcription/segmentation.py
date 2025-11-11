import subprocess, sys
import importlib.util
from pathlib import Path


def run_segmentation(data_dir: Path):
    # installing
    if importlib.util.find_spec("segmentation") is not None:
        print("Sign segmentation already exists.")
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "git+https://github.com/sign-language-processing/segmentation",
            ]
        )

    # Find all .pose files
    pose_files = sorted(data_dir.glob("*.pose"))

    for pose_path in pose_files:
        base_name = pose_path.stem  # e.g. "alarm" from "alarm.pose"
        elan_path = data_dir / f"{base_name}.eaf"
        video_path = data_dir / f"{base_name}.mp4"

        print(f"Processing {base_name}")

        # Run the segmentation command
        subprocess.run(
            [
                "pose_to_segments",
                "--pose",
                str(pose_path),
                "--elan",
                str(elan_path),
                "--video",
                str(video_path),
            ]
        )


if __name__ == "__main__":
    dir = "signdict_examples/"
    # directory containing your .pose and .mp4 files
    data_dir = Path(dir)
    run_segmentation(data_dir)
