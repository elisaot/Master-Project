# TODO: not functional
import subprocess, sys, os
import importlib.util

# installing
if importlib.util.find_spec("sign_language_recognition") is not None:
    print("Single sign recognition already installed.")
else:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "git+https://github.com/sign-language-processing/recognition",
        ]
    )


# testing for a single sign.
subprocess.run(
    [
        "sign_language_recognition",
        "--model='kaggle_asl_signs'",
        "--pose='signdict_examples/alarm.pose'",
        "--elan='example.eaf'",
    ],
    stdout=open("prediction.txt", "w"),
)
