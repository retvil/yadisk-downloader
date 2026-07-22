# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Download files from Yandex Disk links where direct download is disabled.**

[🇷🇺 Русский](README.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## What is this?

Yandex Disk is widely used for sharing conference recordings, lectures, online courses, and other files. But often authors disable direct download — you have to click each file individually, choose quality manually, and wait.

**yadisk-downloader** solves this: paste a public link, and the tool downloads all files at once with resolution control, smart conversion presets, and a modern GUI.

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

## Installation

### Prerequisites

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — needed for video download and conversion

### Install ffmpeg

**Windows (winget):**
```bash
winget install Gyan.FFmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

### Install yadisk-downloader

```bash
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader
pip install -r requirements.txt
playwright install chromium
```

## Usage

### CLI

```bash
# Download all files
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX

# Download at 1080p
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# Download only video
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# Download with conversion
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# List files
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list

# Show presets
python -m yadisk_downloader --preset-list
```

### GUI Mode

```bash
python -m yadisk_downloader --gui
```

## Conversion Presets

| Preset | Codec | Resolution | Audio | Size | Best for |
|--------|-------|------------|-------|------|----------|
| `best` | H.265 | Original | AAC 192k | ~60% | Archiving, maximum quality |
| `balanced` | H.264 | Original | AAC 128k | ~70% | General use |
| `compact` | H.264 | 480p | AAC 96k | ~30% | Mobile |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTube upload |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | Phones |
| `mp3` | — | — | MP3 320k | ~5% | Audio extraction |
| `remux` | Copy | Copy | Copy | ~100% | Format change |

## License

MIT License — see [LICENSE](LICENSE).
