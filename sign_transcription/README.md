# Sign Language Transcription

Project for first anynomizing Sign Language dictionary videos, and the transcribing to glosses.

## Overview

This project utilizes pose-format(https://github.com/sign-language-processing/pose) and TODO: select transcription tool to perform the mentioned task.

## Requirements
Python version 3.9?
numpy < 2.0.0: pip install numpy==1.23  

```bash
pip install mediapipe==0.10.5
pip install psutil
```

```bash
# installing pose-format
pip install pose-format
```
Note: the pose-format dependencies are not handeled internally.

```bash
pip install opencv-python
```

### Installation of Transcription Package
```bash
# installing package
git clone https://github.com/sign-language-processing/signwriting-transcription.git
```

```bash
# downloading dependencies
cd signwriting-transcription
pip install .
```

This package utilizes Joey NMT(https://github.com/joeynmt/joeynmt)
```bash
# installing Joey NMT
pip install joeynmt
```
```bash
# installing syntethic SignWriting package
pip install git+https://github.com/sign-language-processing/synthetic-signwriting
```
```bash
# installing pose anonymization
pip install git+https://github.com/sign-language-processing/pose-anonymization.git
```

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

### Segmentation and .eaf-files

```bash
pip install git+https://github.com/sign-language-processing/segmentation
pose_to_segments --pose="sign.pose" --elan="sign.eaf" [--video="sign.mp4"]
```
test for this in segmentation.py did not work...

before segmentation: 
pip install numpy==1.23  

before trancription:
- NOT pip install numpy==2.0.1
pip install torch==1.12.0
(pip install torchaudio==0.12.0 for compatibility)


run: python3.9 main.py !!