# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Bulk download files from public Yandex Disk folders with one command.**

## What is this?

Yandex Disk is widely used for sharing conference recordings, lecture videos, online courses, and other large files. But there's no built-in way to download entire folders — you have to click each file individually, choose quality manually, and wait.

**yadisk-downloader** solves this: paste a public link, and it downloads all files at once with resolution control, smart conversion presets, and a modern GUI.

## Features

- **One-command bulk download** — paste a link, get all files
- **All file types** — video, audio, images, documents, archives, executables
- **Resolution control** — choose 240p, 360p, 480p, 720p, or 1080p
- **9 conversion presets** — H.265, H.264, MP3, AAC, and more
- **CLI + GUI** — automate with command line, or use the visual interface
- **Folder filtering** — download specific folders only
- **Type filtering** — download only specific file types
- **Progress tracking** — see speed, ETA, and percentage for each file
- **Resume support** — continue interrupted downloads automatically
- **Checksum verification** — verify file integrity with MD5
- **Download queue** — manage multiple URLs
- **Scheduled downloads** — run downloads on a schedule (cron)
- **Proxy support** — use HTTP/SOCKS proxy for downloads
- **Config file** — save your settings for reuse
- **Notifications** — system notification when download completes
- **Skip existing** — won't re-download files you already have
- **Cross-platform** — works on Windows, macOS, and Linux

## Quick Start

```bash
# Install
pip install -r requirements.txt
playwright install chromium

# Download all files from a public link
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

That's it. Files will appear in `./downloads/` organized by folder.

## Installation

### Prerequisites

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — needed for video download and conversion

### Install ffmpeg

**Windows (winget):**
```bash
winget install Gyan.FFmpeg
```

**Windows (Chocolatey):**
```bash
choco install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

Alternatively, `imageio-ffmpeg` will be installed automatically and provides a bundled ffmpeg.

### Install yadisk-downloader

```bash
# Clone the repository
git clone https://github.com/your-username/yadisk-downloader.git
cd yadisk-downloader

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (Chromium)
playwright install chromium
```

Or install as a package:

```bash
pip install -e .
playwright install chromium
```

## Usage

### CLI

#### Basic download

```bash
# Download all files (default: 720p)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

#### Choose resolution

```bash
# Download at 1080p
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# Download at 240p (smallest files, save bandwidth)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 240p
```

If the selected resolution isn't available, the tool automatically falls back to 720p, then to the best available quality.

#### Filter by folder

```bash
# Download only one folder
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -f "Главный зал"
```

#### Convert after download

```bash
# Convert to H.265 (best quality, ~60% of original size)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# Optimize for YouTube upload (1080p H.264)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset youtube

# Extract audio only (MP3 320kbps)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset mp3

# Convert and delete original files
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset compact --delete-original
```

#### List files

```bash
# Show all files without downloading
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list

# Show available conversion presets
python -m yadisk_downloader --preset-list

# Show available file types
python -m yadisk_downloader --type-list
```

#### Filter by file type

```bash
# Download only video files
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# Download video and documents
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video,document

# Download everything except archives and executables
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --exclude archive,executable

# Download only images
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type image
```

Available file types: `video`, `audio`, `image`, `document`, `archive`, `executable`, `other`

#### Custom output directory

```bash
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -o ./my_files
```

#### Proxy support

```bash
# Use HTTP proxy
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --proxy http://proxy:8080

# Use SOCKS proxy
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --proxy socks5://proxy:1080
```

#### Notifications

```bash
# Get system notification when download completes
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --notify
```

#### Configuration file

```bash
# Save current settings as defaults
python -m yadisk_downloader --save-config -r 1080p --notify --proxy http://proxy:8080

# Show current configuration
python -m yadisk_downloader --show-config

# Use custom config file
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --config ./my-config.json
```

Config file location: `~/.yadisk-downloader/config.json`

#### Resume interrupted downloads

Downloads are automatically resumed if interrupted. The tool tracks download state and continues from where it left off.

```bash
# Disable resume (re-download from scratch)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --no-resume

# Clear download state for a URL
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --clear-state

# Clear all download states
python -m yadisk_downloader --clear-state
```

#### Checksum verification

Verify file integrity after download using MD5 checksums.

```bash
# Download with checksum verification
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --checksum
```

#### Download queue

Manage multiple URLs in a queue.

```bash
# Add URLs to queue
python -m yadisk_downloader --queue-add https://disk.yandex.ru/d/XXXXX
python -m yadisk_downloader --queue-add https://disk.yandex.ru/d/YYYYY

# Show queue
python -m yadisk_downloader --queue-show

# Process all items in queue
python -m yadisk_downloader --queue-process

# Remove from queue
python -m yadisk_downloader --queue-remove https://disk.yandex.ru/d/XXXXX

# Clear queue
python -m yadisk_downloader --queue-clear
```

#### Scheduled downloads

Run downloads on a schedule using cron expressions.

```bash
# Add scheduled download (every day at 9 AM)
python -m yadisk_downloader --schedule-add https://disk.yandex.ru/d/XXXXX --cron "0 9 * * *"

# Add scheduled download (every Monday at 10 AM)
python -m yadisk_downloader --schedule-add https://disk.yandex.ru/d/XXXXX --cron "0 10 * * 1"

# Show scheduled downloads
python -m yadisk_downloader --schedule-show

# Run scheduler (processes due downloads)
python -m yadisk_downloader --schedule-run

# Remove schedule
python -m yadisk_downloader --schedule-remove https://disk.yandex.ru/d/XXXXX
```

Cron format: `minute hour day month weekday`

### GUI Mode

Launch the modern visual interface:

```bash
python -m yadisk_downloader --gui
```

**How it works:**
1. Paste the public Yandex Disk link
2. Click **Scan** to load the file list
3. Select resolution, folder, and conversion preset
4. Check/uncheck individual files
5. Click **Download Selected**

The GUI features:
- Modern dark/light theme (auto-detects system settings)
- Progress bar with status updates
- Checkbox list for selective download
- Folder dropdown (populated after scan)
- Resolution radio buttons
- Conversion preset selector

## Conversion Presets

| Preset | Codec | Resolution | Audio | Size | Best for |
|--------|-------|------------|-------|------|----------|
| `best` | H.265 | Original | AAC 192k | ~60% | Archiving, maximum quality |
| `balanced` | H.264 | Original | AAC 128k | ~70% | General use, good compatibility |
| `compact` | H.264 | 480p | AAC 96k | ~30% | Mobile, limited storage |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTube/social media upload |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | Phones, slow connections |
| `mp3` | — | — | MP3 320k | ~5% | Podcasts, music extraction |
| `mp3-small` | — | — | MP3 128k | ~3% | Voice, small audio files |
| `aac` | — | — | AAC 256k | ~5% | Modern audio format |
| `remux` | Copy | Copy | Copy | ~100% | Format change (MKV→MP4), no re-encode |

**Note:** "Size" shows approximate output size relative to the original file.

## CLI Reference

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `url` | — | Yandex Disk public link | *(required)* |
| `--resolution` | `-r` | Video download resolution: 240p, 360p, 480p, 720p, 1080p | `720p` |
| `--folder` | `-f` | Download specific folder only | All folders |
| `--output` | `-o` | Output directory | `./downloads` |
| `--workers` | `-w` | Parallel download workers | `4` |
| `--type` | `-t` | File types to download (comma-separated) | All types |
| `--exclude` | — | File types to exclude (comma-separated) | None |
| `--proxy` | — | Proxy URL (HTTP/SOCKS) | None |
| `--notify` | — | Send system notification on completion | `false` |
| `--config` | — | Path to config file | `~/.yadisk-downloader/config.json` |
| `--preset` | — | Conversion preset for video | *(no conversion)* |
| `--preset-list` | — | Show available presets | — |
| `--type-list` | — | Show available file types | — |
| `--show-config` | — | Show current configuration | — |
| `--save-config` | — | Save current CLI args as defaults | — |
| `--delete-original` | — | Delete original video after conversion | `false` |
| `--no-resume` | — | Disable resume support | `false` |
| `--checksum` | — | Compute MD5 checksum after download | `false` |
| `--clear-state` | — | Clear download state | — |
| `--queue-add` | — | Add URL to download queue | — |
| `--queue-remove` | — | Remove URL from queue | — |
| `--queue-show` | — | Show download queue | — |
| `--queue-clear` | — | Clear download queue | — |
| `--queue-process` | — | Process all items in queue | — |
| `--schedule-add` | — | Add scheduled download | — |
| `--cron` | — | Cron expression for schedule | — |
| `--schedule-remove` | — | Remove scheduled download | — |
| `--schedule-show` | — | Show scheduled downloads | — |
| `--schedule-run` | — | Run scheduler | — |
| `--list` | — | List files without downloading | `false` |
| `--gui` | — | Launch GUI mode | `false` |

## How It Works

1. **File discovery** — Uses the Yandex Disk public API to list all files in the shared folder (no authentication needed for public links)
2. **Download strategy** — Tries API direct download first (fast, reliable), falls back to Playwright browser download if API fails
3. **Video optimization** — For video files, intercepts HLS m3u8 streams and downloads via ffmpeg for best quality
4. **Conversion** (optional) — Re-encodes video files using ffmpeg with the selected preset

## Troubleshooting

### "ffmpeg not found"

ffmpeg must be in your system PATH. Install it using the instructions in [Installation](#install-ffmpeg), or install `imageio-ffmpeg`:

```bash
pip install imageio-ffmpeg
```

### "Playwright browser not installed"

Run:
```bash
playwright install chromium
```

### Network errors / timeouts

- Check your internet connection
- The Yandex Disk public link may have expired
- Try again later — Yandex may rate-limit heavy usage

### Low disk space

Files can be large (1-4 GB each). Use `-r 240p` to download smaller versions, or `--preset compact` to convert after download.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
