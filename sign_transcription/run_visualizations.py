import os
from pose_format.pose import Pose
from pose_format.pose_visualizer import PoseVisualizer

# Make sure output folder exists
os.makedirs("poses", exist_ok=True)

paths = [
    "signdict_examples/alarm.pose",
    "signdict_examples/bestemme-2.pose",
    "signdict_examples/hus.pose",
    "signdict_examples/jeg.pose",
]

i = 1

for path in paths:
    # Read the .pose file
    with open(path, "rb") as f:
        data_buffer = f.read()

    pose = Pose.read(data_buffer)  # , TorchPoseBody)

    # Visualize and save as video
    v = PoseVisualizer(pose)
    output_path = f"poses/example{i}.mp4"
    v.save_video(output_path, v.draw())

    i += 1
