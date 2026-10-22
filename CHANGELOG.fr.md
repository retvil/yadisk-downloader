# Changelog

## [1.3.0] - 2026-10-20

### Ajouté
- **GUI sur ttkbootstrap** — toolkit moderne léger à la place de customtkinter (moins de dépendances, apparence native)
- **10 langues d'interface** — russe, anglais, ukrainien, kazakh, allemand, français, espagnol, polonais, turc, chinois ; sélecteur de langue dans la GUI, choix conservé entre les sessions (`~/.yadisk-downloader/gui.json`)
- **Bouton Annuler** — interrompt le téléchargement entre les fichiers et au sein d'un fichier
- **Progression à deux niveaux** — « Fichier 3/17 : nom — 45,2 % » + barre de progression globale sans sauts
- **Filtre par type de fichier dans la GUI** — combobox « Type : Tous les types / video / audio / ... »
- **Placeholders** — indications dans la liste de fichiers vide et le champ de lien
- **Infobulles** — pour « Supprimer l'original » et le preset de conversion
- **Module de traductions** — `translations.py` : 37 clés × 10 langues, repli sur l'anglais, détection automatique de la langue système
- **Programme d'installation Windows** — Inno Setup (`yadisk-downloader-1.3.0-windows-setup.exe`) : raccourcis, désinstalleur, choix par utilisateur/par machine
- **Build Windows onefile** — un seul exe sans le dossier `_internal` (`yadisk-downloader-1.3.0-windows-onefile.exe`)

### Corrigé
- **Vérification TLS** — contrôle des certificats activé dans toutes les requêtes HTTP
- **Récursion et pagination API** — parcours correct des dossiers profonds et des grandes listes de fichiers
- **Échappement dans les notifications** — les caractères spéciaux des noms de fichiers ne cassent plus les notifications
- **Segments HLS sur disque** — segments écrits dans des fichiers part au lieu de la RAM (pas d'OOM sur les grandes vidéos)
- **Téléchargement de dossiers non bloquant** — `FolderDownloader` migré vers `asyncio.to_thread`
- **GUI** — 14 corrections : ordre des boutons, masquage de la barre de défilement, erreurs dans messagebox, molette uniquement sur la liste, sélection conservée au changement de langue, etc.

### Modifié
- **requirements.txt** — `customtkinter` → `ttkbootstrap`
- **build.py** — PyInstaller compile ttkbootstrap, version synchronisée à 1.3.0

## [1.1.1] - 2026-07-27

### Ajouté
- **Téléchargement HLS parallèle** — 3-5x plus rapide via ThreadPoolExecutor (4 workers par défaut, max 16)
- **Cache JSON atomique** — cache m3u8 avec TTL, écritures atomiques, détection de corruption
- **Sanitisation des entrées** — suppression credentials URL/proxy des logs, prévention path traversal, parsing proxy sécurisé
- **Pool de connexions** — réutilisation session HTTP dans téléchargements API (taille pool 10)
- **Flag `--version`** — affichage version CLI

### Modifié
- Version synchronisée sur tous fichiers : 1.1.1
- Downloader interne refactorisé pour utiliser nouveaux modules parallel_hls, cache, safety

### Infrastructure
- Tests: suite pytest pour modules parallel_hls, cache, safety
- CI: GitHub Actions workflow (ruff → mypy strict → pytest)
- Qualité code: pyproject.toml avec mypy strict, config ruff

## [1.1.0] - 2026-07-23

### Ajouté
- **Fallback docviewer** — téléchargement de documents, photos et autres fichiers même quand le propriétaire a désactivé le téléchargement. Les fichiers sont rendus via Yandex Documents et sauvegardés en PDF.
- **Avertissement format PDF** — notification popup lors du téléchargement de fichiers DOCX/XLSX/PPTX, indiquant que le fichier sera sauvegardé en PDF.
- **Téléchargement vidéo HLS** — intercept m3u8 → ffmpeg pour la vidéo même quand l'API retourne un `href` vide.
- **Icône de l'application** — cercle bleu avec lettre Y et flèche de téléchargement.

### Changé
- Description README mise à jour : ajout de la section "Comment ça marche ?" expliquant les trois stratégies de téléchargement.

## [1.0.0] - 2026-07-22

### Fonctionnalités
- Interface CLI et GUI pour télécharger des fichiers depuis Yandex Disk
- Téléchargement vidéo via HLS (m3u8 + ffmpeg)
- Téléchargement de fichiers via l'API Yandex Disk
- Sélection de résolution : 240p, 360p, 480p, 720p, 1080p
- 9 presets de conversion : best, balanced, compact, youtube, mobile, mp3, mp3-small, aac, remux
- Filtrage par type de fichier : video, audio, image, document, archive, executable
- Filtrage par dossier
- Reprise des téléchargements interrompus (HTTP Range)
- Vérification d'intégrité (MD5)
- File d'attente de téléchargement
- Téléchargements planifiés (cron)
- Support proxy HTTP/SOCKS
- Sauvegarde de configuration
- Notifications système
- Ignorer les fichiers déjà téléchargés
- Build via PyInstaller (exe, portable, installer)
- GitHub Actions pour les builds automatiques
- README en 6 langues (RU, EN, DE, FR, JA, ZH-TW)
