# Changelog

## [1.1.0] - 2026-07-23

### Hinzugefügt
- **Docviewer-Fallback** — Download von Dokumenten, Fotos und anderen Dateien auch wenn der Besitzer das Herunterladen deaktiviert hat. Dateien werden über Yandex Documents gerendert und als PDF gespeichert.
- **PDF-Format-Warnung** — Popup-Benachrichtigung beim Download von DOCX/XLSX/PPTX-Dateien, die mitteilt, dass die Datei als PDF gespeichert wird.
- **HLS-Video-Download** — intercept m3u8 → ffmpeg für Video auch wenn die API leeres `href` zurückgibt.
- **App-Symbol** — blauer Kreis mit Y-Buchstabe und Download-Pfeil.

### Geändert
- README-Beschreibung aktualisiert: Abschnitt "Wie funktioniert es?" mit Erklärung der drei Download-Strategien hinzugefügt.

## [1.0.0] - 2026-07-22

### Funktionen
- CLI- und GUI-Schnittstelle für Download von Yandex Disk Dateien
- Video-Download über HLS (m3u8 + ffmpeg)
- Datei-Download über Yandex Disk API
- Auflösungsauswahl: 240p, 360p, 480p, 720p, 1080p
- 9 Konvertierungsvoreinstellungen: best, balanced, compact, youtube, mobile, mp3, mp3-small, aac, remux
- Dateitypfilter: video, audio, image, document, archive, executable
- Ordnerfilter
- Fortsetzen unterbrochener Downloads (HTTP Range)
- Integritätsprüfung (MD5)
- Download-Warteschlange
- Geplante Downloads (cron)
- HTTP/SOCKS Proxy-Unterstützung
- Konfigurationsspeicherung
- Systembenachrichtigungen
- Bestehende überspringen
- Build über PyInstaller (exe, portable, installer)
- GitHub Actions für automatische Builds
- README in 6 Sprachen (RU, EN, DE, FR, JA, ZH-TW)
