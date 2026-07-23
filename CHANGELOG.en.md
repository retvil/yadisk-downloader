# Changelog

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
