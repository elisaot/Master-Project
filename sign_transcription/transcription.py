import subprocess, sys, os
import importlib.util
import importlib.metadata
from pathlib import Path
from tqdm import tqdm


def run_transcription(data_dir: Path):
    # install dependencies
    if importlib.util.find_spec("mediapipe") is None:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mediapipe", "protobuf==3.20.3"]
        )
    else:
        # Check the installed version
        version = importlib.metadata.version("mediapipe")
        if not version.startswith("0.10."):
            print(f"Found mediapipe {version}, upgrading to 0.10.5...")
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
            print("Mediapipe 0.10.* already installed.")

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
    
    subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "numpy==1.24.4",
                "torch==1.12.0",
                "torchaudio==0.12.0",
            ]
        )

    # Find all .pose files
    pose_files = sorted(data_dir.glob("*.pose"))

    output_lines = []

    for pose_path in tqdm(pose_files, desc="Processing files"):
        base_name = pose_path.stem  # e.g. "alarm" from "alarm.pose"
        elan_path = data_dir / f"{base_name}.eaf"

        if not elan_path.exists():
            tqdm.write(f"Skipping {pose_path.name} (missing {elan_path.name})")
            continue

        tqdm.write(f"Processing {base_name}")

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
            tqdm.write(f"No predicted SignWriting for {base_name}")
            predictions = ["None"] 

        # Add predictions using base_name instead of a numeric ID
        for pred in predictions:
            output_lines.append(f"{base_name} {pred}")

    # Write all predictions to a single file
    with open(data_dir / "prediction.txt", "w") as f:
        f.write("\n".join(output_lines))


if __name__ == "__main__":
    dir = "signdict_examples/"
    # directory containing your .pose and .mp4 files
    data_dir = Path(dir)
    run_transcription(data_dir)
