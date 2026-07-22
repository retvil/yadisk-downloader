# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**從禁止直接下載的 Yandex Disk 連結下載檔案。**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md)

## 這是什麼？

Yandex Disk 被廣泛用於分享會議錄影、講座和其他檔案。但通常作者會禁止直接下載。

**yadisk-downloader** 解決了這個問題：貼上公開連結，工具就會一次性下載所有檔案。

## 功能

- **一鍵批量下載**
- **所有檔案類型** — 影片、音訊、圖片、文件、壓縮檔
- **解析度控制** — 240p 到 1080p
- **9 種轉換預設**
- **CLI + GUI**
- **中斷下載的續傳**
- **代理支援**

## 快速開始

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## 授權條款

MIT License — 詳見 [LICENSE](LICENSE)。
