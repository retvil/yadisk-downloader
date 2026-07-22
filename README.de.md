# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Dateien von Yandex-Disk-Links herunterladen, bei denen der direkte Download deaktiviert ist.**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## Was ist das?

Yandex Disk wird zum Teilen von Konferenzaufzeichnungen, Vorlesungen und anderen Dateien verwendet. Aber oft deaktivieren Autoren den Download vollständig — kein Download-Button, keine Möglichkeit, Dateien zu speichern.

**yadisk-downloader** löst das Problem: Fügen Sie einen öffentlichen Link ein, und das Tool lädt alle Dateien auf einmal herunter.

## Funktionen

- **Massen-Download mit einem Befehl**
- **Alle Dateitypen** — Video, Audio, Bilder, Dokumente, Archive
- **Auflösungskontrolle** — 240p bis 1080p
- **9 Konvertierungsvoreinstellungen**
- **CLI + GUI**
- **Fortsetzung unterbrochener Downloads**
- **Proxy-Unterstützung**

## Schnellstart

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## Lizenz

MIT License — siehe [LICENSE](LICENSE).
