# TODO: not functional
import subprocess, sys
import importlib.util

if importlib.util.find_spec("signwriting_animation") is not None:
    print("Signwriting-animation already installed.")
else:
    print("Installing signwriting-animation...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "git+https://github.com/sign-language-processing/signwriting-animation",
        ]
    )

# testing for a single sign.
subprocess.run(
    [
        "signwriting_to_pose",
        "--signwriting=M500x500S15330473x514S15338473x514S2ff00473x464S36520486x482S20500473x464S26a04473x464S1ed30473x464S1ed36473x464",
        "--pose=example.pose",
    ],
    capture_output=True,
    text=True,
)
