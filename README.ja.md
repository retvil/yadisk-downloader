# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**直接ダウンロードが無効にされたYandex Diskリンクからファイルをダウンロードします。**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## これは何ですか？

Yandex Diskは、会議の録画、講義、オンラインコースを共有するために広く使われています。しかし、多くの場合、投稿者はダウンロードを完全に無効にしています — ダウンロードボタンがなく、ファイルを保存する方法がありません。

**yadisk-downloader**はこの問題を解決します：パブリックリンクを貼り付けるだけで、すべてのファイルを一度にダウンロードします。

### どのように機能するか？

- **動画** — HLSストリーム経由でダウンロード（intercept m3u8 → ffmpeg）元の品質で
- **ドキュメント、画像、その他のファイル** — 所有者がダウンロードを無効にした場合、ツールはYandex Documents（docviewer）でファイルを開き、レンダリングされた内容をPDFとして保存
- **通常のリンク** — Yandex Disk API経由で直接ダウンロード

> **注意：** 所有者がダウンロードを無効にした場合、ドキュメントと画像はPDFとして保存されます（ポップアップ警告が表示されます）。Yandex Diskサーバーの制限により、元のフォーマットは利用できません。

## 機能

- **ダウンロード無効時のダウンロード** — 所有者がダウンロードをブロックしても動作
- **コマンド一括ダウンロード** — リンクを貼り付けて、すべてのファイルを取得
- **すべてのファイルタイプ** — 映像、音声、画像、ドキュメント、アーカイブ、実行ファイル
- **HLS動画ダウンロード** — intercept m3u8 → ffmpeg、最高品質
- **Docviewerフォールバック** — Yandex Documents経由でドキュメント/画像をレンダリング
- **解像度制御** — 240p、360p、480p、720p、1080p
- **9つの変換プリセット** — H.265、H.264、MP3、AACなど
- **CLI + GUI** — コマンドラインまたはビジュアルインターフェースで自動化
- **フォルダフィルタ** — 特定のフォルダのみダウンロード
- **タイプフィルタ** — 特定のファイルタイプのみダウンロード
- **進捗追跡** — 各ファイルの速度、ETA、パーセンテージを表示
- **再開サポート** — 中断されたダウンロードを自動的に再開
- **整合性チェック** — MD5検証
- **ダウンロードキュー** — 複数URL管理
- **スケジュールダウンロード** — cronによるスケジュール実行
- **プロキシサポート** — HTTP/SOCKSプロキシ
- **設定ファイル** — 設定の保存と再利用
- **通知** — システム通知 + ポップアップ警告
- **既存をスキップ** — 既に持っているファイルは再ダウンロードしない
- **クロスプラットフォーム** — Windows、macOS、Linuxで動作

## クイックスタート

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## インストール

### 前提条件

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — 動画のダウンロードと変換に必要

### ffmpegのインストール

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

### yadisk-downloaderのインストール

```bash
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader
pip install -r requirements.txt
playwright install chromium
```

## 使い方

### CLI

```bash
# すべてのファイルをダウンロード
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX

# 1080pでダウンロード
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# 動画のみダウンロード
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# 変換付きダウンロード
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# ファイル一覧
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list
```

### GUIモード

```bash
python -m yadisk_downloader --gui
```

## 変換プリセット

| プリセット | コードック | 解像度 | オーディオ | サイズ | 用途 |
|-----------|-----------|--------|-----------|--------|------|
| `best` | H.265 | オリジナル | AAC 192k | ~60% | アーカイブ、最高品質 |
| `balanced` | H.264 | オリジナル | AAC 128k | ~70% | 一般利用 |
| `compact` | H.264 | 480p | AAC 96k | ~30% | モバイル |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTubeアップロード |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | 携帯電話 |
| `mp3` | — | — | MP3 320k | ~5% | オーディオ抽出 |
| `remux` | Copy | Copy | Copy | ~100% | フォーマット変更 |

## ライセンス

MIT License — [LICENSE](LICENSE)参照。
