# Changelog

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
