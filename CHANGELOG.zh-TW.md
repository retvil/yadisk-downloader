# Changelog

## [1.1.1] - 2026-07-27

### 新增
- **並行 HLS 下載** — ThreadPoolExecutor 實現 3-5 倍加速（預設 4 workers，上限 16）
- **原子性 JSON 快取** — m3u8 播放列表快取帶 TTL、原子寫入、損壞檢測
- **輸入清理** — URL/代理憑證從日誌移除、路徑遍歷防護、安全代理解析
- **連線池** — API 下載複用 HTTP Session（池大小 10）
- **`--version` 旗標** — CLI 版本顯示

### 變更
- 所有檔案版本統一為 1.1.1
- 內部下載器重構使用新模組（parallel_hls, cache, safety）

### 基礎設施
- 測試: parallel_hls, cache, safety 模組 pytest 測試套件
- CI: GitHub Actions workflow (ruff → mypy strict → pytest)
- 程式碼品質: pyproject.toml (mypy strict, ruff 設定)

## [1.1.0] - 2026-07-23

### 新增
- **Docviewer 回退** — 即使擁有者禁用了下載，也能下載文件、照片和其他文件。文件通過 Yandex Documents 渲染並保存為 PDF。
- **PDF 格式警告** — 下載 DOCX/XLSX/PPTX 文件時顯示彈出通知，告知文件將以 PDF 格式保存。
- **HLS 影片下載** — 即使 API 返回空的 `href`，也能通過 intercept m3u8 → ffmpeg 下載影片。
- **應用程式圖示** — 藍色圓圈帶有 Y 字母和下載箭頭。

### 變更
- 更新 README 說明：新增「運作方式」章節，說明三種下載策略。

## [1.0.0] - 2026-07-22

### 功能
- CLI 和 GUI 介面用於從 Yandex Disk 下載文件
- 通過 HLS 下載影片（m3u8 + ffmpeg）
- 通過 Yandex Disk API 下載文件
- 解析度選擇：240p、360p、480p、720p、1080p
- 9 種轉換預設：best、balanced、compact、youtube、mobile、mp3、mp3-small、aac、remux
- 文件類型篩選：video、audio、image、document、archive、executable
- 資料夾篩選
- 繼續中斷的下載（HTTP Range）
- 完整性檢查（MD5）
- 下載佇列
- 排程下載（cron）
- HTTP/SOCKS 代理支援
- 設定儲存
- 系統通知
- 跳過已下載的文件
- 通過 PyInstaller 打包（exe、portable、installer）
- GitHub Actions 自動化打包
- 6 語言的 README（RU、EN、DE、FR、JA、ZH-TW）
