# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Télécharger des fichiers depuis des liens Yandex Disk où le téléchargement direct est désactivé.**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## Qu'est-ce que c'est ?

Yandex Disk est utilisé pour partager des enregistrements, des cours et d'autres fichiers. Mais les auteurs désactivent souvent complètement le téléchargement — pas de bouton télécharger, pas de moyen de sauvegarder les fichiers.

**yadisk-downloader** résout ce problème : collez un lien public, et l'outil télécharge tous les fichiers en une fois.

## Fonctionnalités

- **Téléchargement en masse en une commande**
- **Tous types de fichiers** — vidéo, audio, images, documents, archives
- **Contrôle de résolution** — 240p à 1080p
- **9 presets de conversion**
- **CLI + GUI**
- **Reprise des téléchargements interrompus**
- **Support proxy**

## Démarrage rapide

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## Licence

MIT License — voir [LICENSE](LICENSE).
