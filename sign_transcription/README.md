# Sign Language Transcription

Project for first anynomizing Sign Language dictionary videos, and the transcribing to glosses.

## Overview

This project utilizes pose-format(https://github.com/sign-language-processing/pose) and TODO: select transcription tool to perform the mentioned task.

## Requirements

### Installation 

```bash
# installing pose-format
pip install pose-format
```
Note: the pose-format dependencies are not handeled internally.



## Usage

### Bash command for creating .pose files

```bash
videos_to_poses --format mediapipe --directory directory_of_videos/
```

### Visualizing poses

run_visuazlizations.py takes the list of generated .pose-files and creates poses directory with pose vidoes renamed.

```bash
python3 run_visuazlizations.py
```
Note: The paths for the signed videos are manually written into the script. Will edit for taking command line argument of folder with .pose files later.