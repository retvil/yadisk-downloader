# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Télécharger des fichiers depuis des liens Yandex Disk où le téléchargement direct est désactivé.**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## Qu'est-ce que c'est ?

Yandex Disk est largement utilisé pour partager des enregistrements de conférences, des cours et d'autres fichiers. Mais les auteurs désactivent souvent complètement le téléchargement — pas de bouton télécharger, pas de moyen de sauvegarder les fichiers.

**yadisk-downloader** résout ce problème : collez un lien public, et l'outil télécharge tous les fichiers en une fois.

### Comment ça marche ?

- **Vidéo** — téléchargée via les flux HLS (intercept m3u8 → ffmpeg) en qualité originale
- **Documents, images et autres fichiers** — quand le propriétaire a désactivé le téléchargement, l'ouvre le fichier dans Yandex Documents (docviewer) et sauvegarde le contenu rendu en PDF
- **Liens normaux** — téléchargés directement via l'API Yandex Disk

> **Remarque :** Si le propriétaire a désactivé le téléchargement, les documents et images sont sauvegardés en PDF (un avertissement popup est affiché). Le format original n'est pas disponible en raison des restrictions serveur de Yandex Disk.

## Fonctionnalités

- **Téléchargement avec téléchargement désactivé** — fonctionne même quand le propriétaire a bloqué le téléchargement
- **Téléchargement en masse en une commande** — collez un lien, obtenez tous les fichiers
- **Tous types de fichiers** — vidéo, audio, images, documents, archives, exécutables
- **Téléchargement vidéo HLS** — intercept m3u8 → ffmpeg, meilleure qualité
- **Fallback docviewer** — rendu des documents/photos via Yandex Documents
- **Contrôle de résolution** — 240p, 360p, 480p, 720p ou 1080p
- **9 presets de conversion** — H.265, H.264, MP3, AAC et plus
- **CLI + GUI** — automatisation en ligne de commande ou interface graphique
- **Filtrage par dossiers** — téléchargement de dossiers spécifiques uniquement
- **Filtrage par type** — téléchargement de types de fichiers spécifiques uniquement
- **Suivi de progression** — vitesse, ETA et pourcentage pour chaque fichier
- **Reprise** — continuation automatique des téléchargements interrompus
- **Vérification d'intégrité** — vérification MD5
- **File d'attente** — gestion de plusieurs URLs
- **Téléchargements planifiés** — téléchargements programmés (cron)
- **Support proxy** — proxy HTTP/SOCKS
- **Fichier de configuration** — sauvegarde des paramètres
- **Notifications** — notifications système + avertissements popup
- **Ignorer existants** — ne re-télécharge pas les fichiers déjà présents
- **Multiplateforme** — Windows, macOS et Linux

## Démarrage rapide

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## Installation

### Prérequis

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — nécessaire pour le téléchargement et la conversion vidéo

### Installer ffmpeg

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

### Installer yadisk-downloader

```bash
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader
pip install -r requirements.txt
playwright install chromium
```

## Utilisation

### CLI

```bash
# Télécharger tous les fichiers
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX

# Télécharger en 1080p
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# Télécharger uniquement la vidéo
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# Télécharger avec conversion
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# Lister les fichiers
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list
```

### Mode GUI

```bash
python -m yadisk_downloader --gui
```

## Presets de conversion

| Preset | Codec | Résolution | Audio | Taille | Idéal pour |
|--------|-------|------------|-------|--------|------------|
| `best` | H.265 | Original | AAC 192k | ~60% | Archivage, qualité maximale |
| `balanced` | H.264 | Original | AAC 128k | ~70% | Usage général |
| `compact` | H.264 | 480p | AAC 96k | ~30% | Mobile |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | Upload YouTube |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | Téléphone |
| `mp3` | — | — | MP3 320k | ~5% | Extraction audio |
| `remux` | Copy | Copy | Copy | ~100% | Changement de format |

## Licence

MIT License — voir [LICENSE](LICENSE).
