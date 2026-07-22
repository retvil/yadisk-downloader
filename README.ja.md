# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**直接ダウンロードが無効にされたYandex Diskリンクからファイルをダウンロードします。**

[🇷🇺 Русский](README.md) | [🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## これは何ですか？

Yandex Diskは、会議の録画、講義、オンラインコースを共有するために広く使われています。しかし、多くの場合、投稿者はダウンロードを完全に無効にしています — ダウンロードボタンがなく、ファイルを保存する方法がありません。

**yadisk-downloader**はこの問題を解決します：パブリックリンクを貼り付けるだけで、すべてのファイルを一度にダウンロードします。

## 機能

- **コマンド一括ダウンロード**
- **すべてのファイルタイプ** — 映像、音声、画像、ドキュメント、アーカイブ
- **解像度制御** — 240pから1080p
- **9つの変換プリセット**
- **CLI + GUI**
- **中断されたダウンロードの再開**
- **プロキシサポート**

## クイックスタート

```bash
pip install -r requirements.txt
playwright install chromium
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

## ライセンス

MIT License — [LICENSE](LICENSE)参照。
