from pathlib import Path
from segmentation import run_segmentation
from transcription import run_transcription
from pose import get_poses, visualize_pose

if __name__ == "__main__":
    dir = "../preprocess_news/clips"
    # directory containing your .pose and .mp4 files
    data_dir = Path(dir)
    # make .pose files in video directory
    get_poses(data_dir)
    # create visuals of the poses. Optional:
    # visualize_pose(data_dir, "pose_visuals/")

    # creating .eaf (segmentations) files for the poses
    run_segmentation(data_dir)
    # creating SignWriting annotations of the .pose files
    run_transcription(data_dir)
