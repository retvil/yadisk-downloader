# Changelog

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
