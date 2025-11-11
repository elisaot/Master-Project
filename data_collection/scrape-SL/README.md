# Minetegn.no Video Scraper

A Python scraper for downloading Norwegian sign language videos from minetegn.no.

## Overview

This scraper downloads all available sign language videos from the minetegn.no website. It fetches video metadata from their XML API and downloads videos in parallel using multiprocessing for efficiency.

## Features

- **Parallel downloads** using multiprocessing (configurable worker count)
- **Progress tracking** with detailed logging
- **Error handling** for network issues and file conflicts
- **Rate limiting** to respect server resources
- **Resume capability** - skips already downloaded files
- **Test mode** for safe development
- **Comprehensive logging** to both console and file

## Requirements

- [uv](https://docs.astral.sh/uv/) package manager

## Installation

No installation required! Just use `uv` to run the project:

```bash
# uv will automatically handle dependencies
uv run main.py --test
```

## Usage

### Test Mode (Recommended First)
Download only the first 5 videos to test the setup:

```bash
uv run main.py --test
```

### Full Scraping
Download all available videos (~10,171 videos):

```bash
uv run main.py
```

## Output

- **Videos**: Downloaded to `videos/` directory as `.mp4` files
- **Logs**: Saved to `scraping.log` with detailed progress information
- **Console**: Real-time progress updates

## Configuration

The scraper can be configured by modifying the `VideoScraper` class initialization:

```python
scraper = VideoScraper(
    base_url="https://www.minetegn.no",
    xml_endpoint="/tegnordbok/xml/tegnordbok.php", 
    video_path="/Tegnordbok-HTML/video_/",
    output_dir="videos",
    max_workers=8  # Adjust based on your system
)
```

## Data Source

- **XML API**: `https://www.minetegn.no/tegnordbok/xml/tegnordbok.php`
- **Video URL Pattern**: `https://www.minetegn.no/Tegnordbok-HTML/video_/[filename].mp4`
- **Total Videos**: ~10,171 (as of last check)

## Technical Details

### XML Structure
The XML API returns elements like:
```xml
<leksem visningsord="asfalt 1" filnavn="asfalt" kommetarviss="">
```

Where:
- `visningsord`: Display word/term
- `filnavn`: Video filename (used to construct download URL)
- `kommetarviss`: Comment field

### Download Process
1. Fetch XML from API endpoint
2. Parse XML to extract `filnavn` attributes
3. Construct video URLs using pattern
4. Download videos in parallel using multiprocessing
5. Skip existing files automatically

### Rate Limiting
- 0.1 second delay between requests
- Configurable worker count (default: 8)
- Respectful of server resources

## Error Handling

The scraper handles:
- Network timeouts and connection errors
- HTTP 404 errors for missing videos
- File system errors
- Partial file cleanup on failed downloads

## Logging

Detailed logging includes:
- Download progress every 10 files
- Individual file success/failure
- File sizes and error messages
- Final summary statistics

## Legal Considerations

- **No robots.txt** found on minetegn.no
- **Public API** endpoint used for metadata
- **Educational/Research** purpose assumed
- **Rate limiting** implemented to be respectful

## Example Output

```
2025-07-17 23:41:26,415 - INFO - Starting parallel download of 5 videos using 8 workers
2025-07-17 23:41:29,220 - INFO - Downloaded a-tak.mp4 (347,990 bytes)
2025-07-17 23:41:30,233 - INFO - Scraping complete!
2025-07-17 23:41:30,234 - INFO - Successfully downloaded: 5
2025-07-17 23:41:30,234 - INFO - Failed downloads: 0
2025-07-17 23:41:30,234 - INFO - Skipped (already exist): 0
```

## Troubleshooting

### Common Issues

1. **Module not found**: Use `uv run main.py` to automatically handle dependencies
2. **Permission errors**: Ensure write permissions to current directory
3. **Network timeouts**: Check internet connection and retry
4. **uv installation**: Install uv from https://docs.astral.sh/uv/

### Performance Tips

- Adjust `max_workers` based on your system and network capacity
- Monitor disk space (videos total several GB)
- Use SSD storage for better I/O performance

## File Structure

```
scrape-tegnspraak/
├── main.py              # Main scraper script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── scraping.log        # Detailed logs
└── videos/             # Downloaded video files
    ├── a-tak.mp4
    ├── asfalt.mp4
    └── ...
```

## License

This scraper is provided as-is for educational and research purposes. Ensure compliance with minetegn.no's terms of service and applicable laws.