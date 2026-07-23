# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**從禁止直接下載的 Yandex Disk 連結下載檔案。**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md)

## 這是什麼？

Yandex Disk 被廣泛用於分享會議錄影、講座和其他檔案。但通常作者會完全禁止下載 — 沒有下載按鈕，沒有儲存檔案的方法。

**yadisk-downloader** 解決了這個問題：貼上公開連結，工具就會一次性下載所有檔案。

### 運作方式？

- **影片** — 通過 HLS 串流下載（intercept m3u8 → ffmpeg）原始品質
- **文件、圖片和其他檔案** — 當擁有者禁用下載時，工具會在 Yandex Documents（docviewer）中打開檔案，並將渲染的內容保存為 PDF
- **一般連結** — 通過 Yandex Disk API 直接下載

> **注意：** 如果擁有者禁用下載，文件和圖片將保存為 PDF（會顯示彈出警告）。由於 Yandex Disk 伺服器限制，無法取得原始格式。

## 功能

- **禁用下載時仍可下載** — 即使擁有者封鎖下載也能運作
- **一鍵批量下載** — 貼上連結，取得所有檔案
- **所有檔案類型** — 影片、音訊、圖片、文件、壓縮檔、執行檔
- **HLS 影片下載** — intercept m3u8 → ffmpeg，最佳品質
- **Docviewer 回退** — 通過 Yandex Documents 渲染文件/圖片
- **解析度控制** — 240p、360p、480p、720p、1080p
- **9 種轉換預設** — H.265、H.264、MP3、AAC 等
- **CLI + GUI** — 通過命令列或圖形介面自動化
- **資料夾篩選** — 僅下載特定資料夾
- **類型篩選** — 僅下載特定檔案類型
- **進度追蹤** — 顯示每個檔案的速度、ETA 和百分比
- **續傳支援** — 自動繼續中斷的下載
- **完整性檢查** — MD5 驗證
- **下載佇列** — 管理多個 URL
- **排程下載** — 按排程下載（cron）
- **代理支援** — HTTP/SOCKS 代理
- **設定檔** — 儲存設定以供重用
- **通知** — 系統通知 + 彈出警告
- **跳過已下載** — 不會重新下載已有的檔案
- **跨平台** — 支援 Windows、macOS 和 Linux

## 快速開始

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## 安裝

### 前置要求

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — 影片下載和轉換所需

### 安裝 ffmpeg

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

### 安裝 yadisk-downloader

```bash
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### CLI

```bash
# 下載所有檔案
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX

# 以 1080p 下載
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# 僅下載影片
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# 帶轉換的下載
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# 列出檔案
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list
```

### GUI 模式

```bash
python -m yadisk_downloader --gui
```

## 轉換預設

| 預設 | 編碼器 | 解析度 | 音訊 | 大小 | 用途 |
|------|--------|--------|------|------|------|
| `best` | H.265 | 原始 | AAC 192k | ~60% | 歸檔、最高品質 |
| `balanced` | H.264 | 原始 | AAC 128k | ~70% | 一般用途 |
| `compact` | H.264 | 480p | AAC 96k | ~30% | 行動裝置 |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTube 上傳 |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | 手機 |
| `mp3` | — | — | MP3 320k | ~5% | 音訊擷取 |
| `remux` | Copy | Copy | Copy | ~100% | 格式轉換 |

## 授權條款

MIT License — 詳見 [LICENSE](LICENSE)。
