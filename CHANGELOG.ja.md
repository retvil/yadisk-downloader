# Changelog

## [1.3.0] - 2026-10-20

### 追加
- **ttkbootstrap製GUI** — customtkinterの代わりに軽量モダンなツールキット（依存関係減、ネイティブ外観）
- **10言語インターフェース** — ロシア語、英語、ウクライナ語、カザフ語、ドイツ語、フランス語、スペイン語、ポーランド語、トルコ語、中国語。GUI内の言語セレクター、選択はセッション間で保持（`~/.yadisk-downloader/gui.json`）
- **キャンセルボタン** — ファイル間およびファイル内でダウンロードを中断
- **2段階プログレス** — 「ファイル 3/17: 名前 — 45.2%」+ ジャンプしない全体プログレスバー
- **GUI内ファイルタイプフィルター** — コンボボックス「タイプ: すべて / video / audio / ...」
- **プレースホルダー** — 空のファイルリストとリンク入力欄のヒント
- **ツールチップ** — 「元ファイルを削除」と変換プリセット用
- **翻訳モジュール** — `translations.py`：37キー × 10言語、英語フォールバック、システム言語自動検出

### 修正
- **TLS検証** — すべてのHTTPリクエストで証明書チェックを有効化
- **API再帰とページネーション** — 深いフォルダと大きなファイルリストの正しい走査
- **通知のエスケープ** — ファイル名の特殊文字が通知を壊さなくなった
- **HLSセグメントのディスク書き込み** — セグメントをRAMの代わりにpartファイルへ書き込み（大型動画でOOMなし）
- **非ブロッキングフォルダダウンロード** — `FolderDownloader`を`asyncio.to_thread`に移行
- **GUI** — 14項目の修正：ボタン順序、スクロールバー非表示、messageboxでのエラー表示、リスト上のみのホイールスクロール、言語変更時の選択保持、他

### 変更
- **requirements.txt** — `customtkinter` → `ttkbootstrap`
- **build.py** — PyInstallerがttkbootstrapをビルド、バージョンを1.3.0に同期

## [1.1.1] - 2026-07-27

### 追加
- **並列HLSダウンロード** — ThreadPoolExecutorで3-5倍高速化（デフォルト4ワーカー、最大16）
- **アトミックJSONキャッシュ** — TTL付きm3u8プレイリストキャッシュ、アトミック書き込み、破損検知
- **入力サニタイズ** — URL/プロキシ認証情報をログから除去、パストラバーサル防止、安全なプロキシ解析
- **接続プーリング** — APIダウンロードでHTTPセッション再利用（プールサイズ10）
- **`--version`フラグ** — CLIバージョン表示

### 変更
- 全ファイルでバージョン統一：1.1.1
- 内部ダウンローダーを新モジュール（parallel_hls, cache, safety）使用にリファクタ

### インフラ
- テスト: parallel_hls, cache, safetyモジュールのpytestスイート
- CI: GitHub Actionsワークフロー (ruff → mypy strict → pytest)
- コード品質: pyproject.toml (mypy strict, ruff設定)

## [1.1.0] - 2026-07-23

### 追加
- **Docviewerフォールバック** — 所有者がダウンロードを無効にしても、ドキュメント、写真、その他のファイルをダウンロード可能。ファイルはYandex Documentsでレンダリングされ、PDFとして保存。
- **PDF形式の警告** — DOCX/XLSX/PPTXファイルのダウンロード時にポップアップ通知を表示し、ファイルがPDFとして保存されることを通知。
- **HLS動画ダウンロード** — APIが空の`href`を返しても、intercept m3u8 → ffmpegで動画をダウンロード。
- **アプリアイコン** — Y文字とダウンロード矢印の青い円。

### 変更
- READMEの説明を更新：3つのダウンロード戦略を説明する「どのように機能するか？」セクションを追加。

## [1.0.0] - 2026-07-22

### 機能
- Yandex Diskからのファイルダウンロード用CLIおよびGUIインターフース
- HLS経由の動画ダウンロード（m3u8 + ffmpeg）
- Yandex Disk API経由のファイルダウンロード
- 解像度選択：240p、360p、480p、720p、1080p
- 9つの変換プリセット：best、balanced、compact、youtube、mobile、mp3、mp3-small、aac、remux
- ファイルタイプフィルタ：video、audio、image、document、archive、executable
- フォルダフィルタ
- 中断されたダウンロードの再開（HTTP Range）
- 整数性検証（MD5）
- ダウンロードキュー
- スケジュールダウンロード（cron）
- HTTP/SOCKSプロキシサポート
- 設定の保存
- システム通知
- 既存ファイルのスキップ
- PyInstaller経由のビルド（exe、portable、installer）
- GitHub Actionsによる自動ビルド
- 6か国語のREADME（RU、EN、DE、FR、JA、ZH-TW）
