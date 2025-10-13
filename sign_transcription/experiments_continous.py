import subprocess, sys, os
import importlib.util

# install dependencies
subprocess.run(
    [sys.executable, "-m", "pip", "install", "mediapipe", "protobuf==3.20.3"]
)

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

# testing for a single sign.
subprocess.run(
    [
        "pose_to_signwriting",
        "--pose",
        "signdict_examples/alarm.pose",
        "--elan",
        "sign.eaf",
    ],
    stdout=open("prediction.txt", "w"),
)
