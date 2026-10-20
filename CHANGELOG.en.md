# Changelog

## [1.3.0] - 2026-10-20

### Added
- **GUI on ttkbootstrap** — lightweight modern toolkit instead of customtkinter (fewer dependencies, native look)
- **10 interface languages** — Russian, English, Ukrainian, Kazakh, German, French, Spanish, Polish, Turkish, Chinese; language selector in GUI, choice persisted across runs (`~/.yadisk-downloader/gui.json`)
- **Cancel button** — aborts download between files and within a file
- **Two-level progress** — "File 3/17: name — 45.2%" + overall progress bar without jumps
- **File type filter in GUI** — combobox "Type: All types / video / audio / ..."
- **Placeholders** — hints in the empty file list and link entry
- **Tooltips** — for "Delete original" and conversion preset
- **Translations module** — `translations.py`: 37 keys × 10 languages, English fallback, system language auto-detection

### Fixed
- **TLS verification** — certificate checking enabled in all HTTP requests
- **API recursion and pagination** — correct traversal of deep folders and large file lists
- **Notification escaping** — special characters in file names no longer break notifications
- **HLS segments to disk** — segments written to part files instead of RAM (no OOM on large videos)
- **Non-blocking folder download** — `FolderDownloader` moved to `asyncio.to_thread`
- **GUI** — 14 fixes: button order, scrollbar hiding, errors in messagebox, wheel scroll only over the list, selection preserved on language change, and others

### Changed
- **requirements.txt** — `customtkinter` → `ttkbootstrap`
- **build.py** — PyInstaller builds ttkbootstrap, version synced to 1.3.0

## [1.1.1] - 2026-07-27

### Added
- **Parallel HLS download** — 3-5x faster video download via ThreadPoolExecutor (4 workers default, max 16)
- **Atomic JSON cache** — m3u8 playlist cache with TTL, atomic writes, corruption detection
- **Input sanitization** — URL/proxy credential stripping from logs, path traversal prevention, safe proxy parsing
- **Connection pooling** — HTTP session reuse in API downloads (pool size 10)
- **`--version` flag** — CLI version display

### Changed
- Version synchronised across all files: 1.1.1
- Internal downloader refactored to use new parallel HLS, cache, and safety modules

### Infrastructure
- Tests: pytest suite for parallel_hls, cache, safety modules
- CI: GitHub Actions workflow (ruff → mypy strict → pytest)
- Code quality: pyproject.toml with mypy strict, ruff config

## [1.1.0] - 2026-07-23

### Added
- **Docviewer fallback** — download documents, photos, and other files even when the owner disabled downloading. Files are rendered via Yandex Documents and saved as PDF.
- **PDF format warning** — popup notification when downloading DOCX/XLSX/PPTX files, informing that the file will be saved as PDF.
- **HLS video download** — intercept m3u8 → ffmpeg for video even when the API returns empty `href`.
- **App icon** — blue circle with Y letter and download arrow.

### Changed
- Updated README description: added "How does it work?" section explaining three download strategies.

## [1.0.0] - 2026-07-22

### Features
- CLI and GUI interface for downloading files from Yandex Disk
- Video download via HLS (m3u8 + ffmpeg)
- File download via Yandex Disk API
- Resolution selection: 240p, 360p, 480p, 720p, 1080p
- 9 conversion presets: best, balanced, compact, youtube, mobile, mp3, mp3-small, aac, remux
- File type filtering: video, audio, image, document, archive, executable
- Folder filtering
- Resume interrupted downloads (HTTP Range)
- Checksum verification (MD5)
- Download queue
- Scheduled downloads (cron)
- HTTP/SOCKS proxy support
- Configuration saving
- System notifications
- Skip already downloaded files
- Build via PyInstaller (exe, portable, installer)
- GitHub Actions for automatic builds
- README in 6 languages (RU, EN, DE, FR, JA, ZH-TW)
