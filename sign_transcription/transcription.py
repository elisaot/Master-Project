import subprocess, sys, os
import importlib.util
import importlib.metadata
from pathlib import Path


def run_transcription(data_dir: Path):
    # install dependencies
    if importlib.util.find_spec("mediapipe") is None:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mediapipe", "protobuf==3.20.3"]
        )
    else:
        # Check the installed version
        version = importlib.metadata.version("mediapipe")
        if version != "0.10.11":
            print(f"Found mediapipe {version}, upgrading to 0.10.11...")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "mediapipe",
                    "protobuf==3.20.3",
                ]
            )
        else:
            print("Mediapipe 0.10.11 already installed.")

    # clone repo if it doesn't already exist
    if not os.path.exists("signwriting-transcription"):
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/sign-language-processing/signwriting-transcription.git",
            ]
        )
    else:
        print("Repo already exists — skipping clone.")

    # install the pose_to_signwriting extra
    if importlib.util.find_spec("signwriting_transcription") is not None:
        print("Signwriting_transcription already installed.")
    else:
        print("Installing signwriting_transcription...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", ".[pose_to_signwriting]"],
            cwd="signwriting-transcription",
        )

    # Find all .pose files
    pose_files = sorted(data_dir.glob("*.pose"))

    output_lines = []

    for i, pose_path in enumerate(pose_files):
        base_name = pose_path.stem  # e.g. "alarm" from "alarm.pose"
        elan_path = data_dir / f"{base_name}.eaf"

        if not elan_path.exists():
            print(f"Skipping {pose_path.name} (missing {elan_path.name})")
            continue

        print(f"Processing {base_name} (ID={i})")

        # Run the pose_to_signwriting command
        process = subprocess.run(
            [
                "pose_to_signwriting",
                "--pose",
                str(pose_path),
                "--elan",
                str(elan_path),
            ],
            capture_output=True,
            text=True,
        )

        # Filter only lines starting with 'M' (SignWriting symbols)
        predictions = [
            line.strip() for line in process.stdout.splitlines() if line.startswith("M")
        ]

        if not predictions:
            print(f"No predicted SignWriting for {base_name}")
            continue

        # Assign the same ID to all predictions from this file
        for pred in predictions:
            output_lines.append(f"{i} {pred}")

    # Write all predictions to a single file
    with open(data_dir / "prediction.txt", "w") as f:
        f.write("\n".join(output_lines))
