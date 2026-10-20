# Changelog

## [1.3.0] - 2026-10-20

### Hinzugefügt
- **GUI auf ttkbootstrap** — leichtes modernes Toolkit statt customtkinter (weniger Abhängigkeiten, natives Aussehen)
- **10 Oberflächensprachen** — Russisch, Englisch, Ukrainisch, Kasachisch, Deutsch, Französisch, Spanisch, Polnisch, Türkisch, Chinesisch; Sprachauswahl in der GUI, Auswahl wird zwischen Sitzungen gespeichert (`~/.yadisk-downloader/gui.json`)
- **Abbrechen-Button** — bricht den Download zwischen Dateien und innerhalb einer Datei ab
- **Zweistufiger Fortschritt** — „Datei 3/17: Name — 45,2 %" + Gesamtfortschrittsbalken ohne Sprünge
- **Dateityp-Filter in der GUI** — Kombobox „Typ: Alle Typen / video / audio / ..."
- **Platzhalter** — Hinweise in der leeren Dateiliste und im Link-Eingabefeld
- **Tooltips** — für „Original löschen" und Konvertierungspreset
- **Übersetzungsmodul** — `translations.py`: 37 Schlüssel × 10 Sprachen, Englisch-Fallback, automatische Spracherkennung

### Behoben
- **TLS-Verifizierung** — Zertifikatsprüfung in allen HTTP-Anfragen aktiviert
- **API-Rekursion und Paginierung** — korrektes Durchlaufen tiefer Ordner und großer Dateilisten
- **Escaping in Benachrichtigungen** — Sonderzeichen in Dateinamen beschädigen Benachrichtigungen nicht mehr
- **HLS-Segmente auf Festplatte** — Segmente werden in Part-Dateien statt RAM geschrieben (kein OOM bei großen Videos)
- **Nicht-blockierender Ordner-Download** — `FolderDownloader` auf `asyncio.to_thread` umgestellt
- **GUI** — 14 Korrekturen: Button-Reihenfolge, Scrollbar-Ausblendung, Fehler in messagebox, Wheel-Scroll nur über der Liste, Auswahl bleibt beim Sprachwechsel erhalten, u.a.

### Geändert
- **requirements.txt** — `customtkinter` → `ttkbootstrap`
- **build.py** — PyInstaller baut ttkbootstrap, Version auf 1.3.0 synchronisiert

## [1.1.1] - 2026-07-27

### Hinzugefügt
- **Paralleler HLS-Download** — 3-5x schnellerer Video-Download via ThreadPoolExecutor (4 Worker Standard, max 16)
- **Atomarer JSON-Cache** — m3u8-Playlist-Cache mit TTL, atomaren Schreibvorgängen, Korruptionserkennung
- **Eingabe-Sanitisierung** — URL/Proxy-Credentials aus Logs entfernt, Pfad-Traversal-Schutz, sicheres Proxy-Parsing
- **Connection Pooling** — HTTP-Session-Wiederverwendung bei API-Downloads (Pool-Größe 10)
- **`--version` Flag** — CLI-Version anzeigen

### Geändert
- Version in allen Dateien synchronisiert: 1.1.1
- Interner Downloader refactored für neue parallel_hls, cache, safety Module

### Infrastruktur
- Tests: pytest Suite für parallel_hls, cache, safety Module
- CI: GitHub Actions Workflow (ruff → mypy strict → pytest)
- Code-Qualität: pyproject.toml mit mypy strict, ruff config

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
