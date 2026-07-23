# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Dateien von Yandex-Disk-Links herunterladen, bei denen der direkte Download deaktiviert ist.**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## Was ist das?

Yandex Disk wird weit verbreitet zum Teilen von Konferenzaufzeichnungen, Vorlesungen, Online-Kursen und anderen Dateien verwendet. Aber oft deaktivieren Autoren den Download vollständig — kein Download-Button, keine Möglichkeit, Dateien zu speichern.

**yadisk-downloader** löst das Problem: Fügen Sie einen öffentlichen Link ein, und das Tool lädt alle Dateien auf einmal herunter.

### Wie funktioniert es?

- **Video** — wird über HLS-Streams heruntergeladen (intercept m3u8 → ffmpeg) in Originalqualität
- **Dokumente, Bilder und andere Dateien** — wenn der Besitzer das Herunterladen deaktiviert hat, öffnet das Tool die Datei in Yandex Documents (docviewer) und speichert den gerenderten Inhalt als PDF
- **Normale Links** — werden direkt über die Yandex Disk API heruntergeladen

> **Hinweis:** Wenn der Besitzer das Herunterladen deaktiviert hat, werden Dokumente und Bilder als PDF gespeichert (eine Popup-Warnung wird angezeigt). Das Originalformat ist aufgrund von Serverbeschränkungen von Yandex Disk nicht verfügbar.

## Funktionen

- **Download mit deaktiviertem Download** — funktioniert auch wenn der Besitzer das Herunterladen blockiert hat
- **Massen-Download mit einem Befehl** — Link einfügen, alle Dateien erhalten
- **Alle Dateitypen** — Video, Audio, Bilder, Dokumente, Archive, ausführbare Dateien
- **HLS-Video-Download** — intercept m3u8 → ffmpeg, beste Qualität
- **Docviewer-Fallback** — rendert Dokumente/Bilder über Yandex Documents
- **Auflösungskontrolle** — 240p, 360p, 480p, 720p oder 1080p
- **9 Konvertierungsvoreinstellungen** — H.265, H.264, MP3, AAC und mehr
- **CLI + GUI** — Automatisierung über Kommandozeile oder grafische Oberfläche
- **Ordnerfilter** — Nur bestimmte Ordner herunterladen
- **Typfilter** — Nur bestimmte Dateitypen herunterladen
- **Fortschrittsanzeige** — Geschwindigkeit, ETA und Prozent für jede Datei
- **Fortsetzen** — Automatisches Fortsetzen unterbrochener Downloads
- **Integritätsprüfung** — MD5-Verifizierung
- **Download-Warteschlange** — Mehrere URL-Verwaltung
- **Geplante Downloads** — Downloads nach Zeitplan (cron)
- **Proxy-Unterstützung** — HTTP/SOCKS Proxy
- **Konfigurationsdatei** — Einstellungen speichern
- **Benachrichtigungen** — Systembenachrichtigungen + Popup-Warnungen
- **Bestehende überspringen** — Kein erneuter Download vorhandener Dateien
- ** plattformübergreifend** — Windows, macOS und Linux

## Schnellstart

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## Installation

### Voraussetzungen

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — für Video-Download und -Konvertierung benötigt

### ffmpeg installieren

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

### yadisk-downloader installieren

```bash
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader
pip install -r requirements.txt
playwright install chromium
```

## Verwendung

### CLI

```bash
# Alle Dateien herunterladen
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX

# In 1080p herunterladen
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# Nur Video herunterladen
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# Mit Konvertierung herunterladen
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# Dateien auflisten
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list
```

### GUI-Modus

```bash
python -m yadisk_downloader --gui
```

## Konvertierungsvoreinstellungen

| Voreinstellung | Codec | Auflösung | Audio | Größe | Beste für |
|----------------|-------|-----------|-------|-------|-----------|
| `best` | H.265 | Original | AAC 192k | ~60% | Archivierung, maximale Qualität |
| `balanced` | H.264 | Original | AAC 128k | ~70% | Allgemeine Nutzung |
| `compact` | H.264 | 480p | AAC 96k | ~30% | Mobil |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTube-Upload |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | Telefon |
| `mp3` | — | — | MP3 320k | ~5% | Audioextraktion |
| `remux` | Copy | Copy | Copy | ~100% | Formatwechsel |

## Lizenz

MIT License — siehe [LICENSE](LICENSE).
