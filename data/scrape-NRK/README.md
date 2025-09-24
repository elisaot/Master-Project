# NRK Tegnspråknytt Downloader

A Python script that downloads videos and Norwegian subtitles from NRK's Tegnspråknytt (Sign Language News) series. The script only downloads videos that have matching Norwegian subtitles available.

## Features

- 🔍 **Smart filtering**: Only downloads videos with Norwegian subtitles
- 📥 **Batch downloading**: Processes up to 100 latest videos
- 🎯 **Quality control**: Downloads best quality up to 720p
- 📝 **Subtitle support**: Downloads Norwegian subtitles (manual and automatic)
- 📊 **Progress tracking**: Real-time progress with detailed feedback
- 📁 **Organized output**: Separates videos and subtitles into folders
- 📋 **Detailed logging**: Creates summary of downloaded content

## Requirements

- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Python 3.8+ (handled automatically by uv)

## Installation

### Install uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (any OS):**
```bash
pip install uv
```

### Download the Project

1. Save all the files in the same directory:
   - `nrk_downloader.py` (main script)
   - `pyproject.toml` (dependencies)
   - `run.sh` (Linux/macOS runner)
   - `run.bat` (Windows runner)
   - `README.md` (this file)

## Usage

### Easy Method (Recommended)

# Linux/macOS:
```bash
bashchmod +x run.sh
./run.sh
```


### Manual Method

```bash
uv run nrk_downloader.py
```

## How It Works

1. **Scanning Phase**: The script first scans all videos in the series to identify which ones have Norwegian subtitles
2. **Confirmation**: Shows you how many videos will be downloaded and waits for confirmation
3. **Download Phase**: Downloads only the videos that have subtitles
4. **Organization**: Moves subtitle files to a separate folder
5. **Logging**: Creates a detailed log of what was downloaded

## Output Structure

```
nrk_tegnspraaknytt/
├── videos/               # Downloaded video files
│   ├── Video1.mp4
│   ├── Video2.webm
│   └── ...
├── subtitles/           # Subtitle files
│   ├── Video1.no.vtt
│   ├── Video2.nb.vtt
│   └── ...
└── download_log.txt     # Detailed download summary
```

## Sample Output

```
NRK Tegnspråknytt Video Downloader (Subtitles Required)
=======================================================

Checking for videos with available subtitles...
Found 45 videos in playlist
✓ [  1/ 45] Tegnspråknytt 15.09.2024... (Subtitles: no)
✗ [  2/ 45] Tegnspråknytt 14.09.2024... (No Norwegian subtitles)
✓ [  3/ 45] Tegnspråknytt 13.09.2024... (Subtitles: nb, no (auto))
...
Found 32 videos with Norwegian subtitles

Proceeding to download 32 videos with subtitles...
Press Enter to continue or Ctrl+C to cancel...
```

## Configuration

You can modify the following settings in `nrk_downloader.py`:

- `max_videos = 100`: Maximum number of videos to check (latest first) NOTE: the NRK-page only contain the news broadcasts for August (about 20 videos), if more videos are needed several urls needs to be used.
- `'format': 'mp4'`: Video quality (change 720 to desired resolution)
- `'subtitleslangs': ['nb-ttv', 'no', 'nb', 'nn']'`: Norwegian language codes to look for

## Troubleshooting

### "uv is not installed"
Install uv using the commands in the Installation section above.

### "Missing required files"
Make sure all files are in the same directory and you're running the script from that directory.

### "No videos with subtitles found"
This might mean:
- The website structure has changed
- No recent videos have Norwegian subtitles
- Network connectivity issues

### "Module not found for yt-dlp"
Solved by running this line: 
```bash
uv pip install yt-dlp
```

## Notes

- The script respects NRK's content and is intended for educational/accessibility purposes
- Downloads are limited to reasonable quality to be respectful of bandwidth
- The script includes error handling to continue if some videos are unavailable
- Subtitles are downloaded in VTT format, which is widely supported

## License

MIT License - Feel free to modify and distribute as needed.