# Changelog

## [1.2.0] - 2026-07-27

### Added
- **Plugin system** — `DownloadStrategy` protocol + `StrategyRegistry` для расширяемых стратегий скачивания
- **Event bus** — `EventBus` с типизированными событиями (`DownloadStarted`, `DownloadProgress`, `DownloadCompleted`, `DownloadFailed`, `FolderScanStarted`, `FolderScanCompleted`, `QueueProcessStarted`, `QueueProcessCompleted`, `ConversionStarted`, `ConversionCompleted`, `ConversionFailed`, `StateSaved`)
- **Pydantic Config** — `Settings` с валидацией, env vars (`YADISK_*`), JSON конфиг, `SecretStr` для OAuth токена
- **DI Container** — `Container` с автовайрингом, синглтонами, фабриками
- **OAuth token support** — `yadisk_oauth_token` в конфиге, авто-добавление в API URLs для приватных папок/увеличенных лимитов
- **Crash-resilient resume** — `DownloadState` с атомарным flush (tmp→rename) каждые 1MB + transaction context manager
- **Parallel folder download** — `FolderDownloader` с `asyncio.Semaphore` (max 4 папки параллельно)
- **Property-based tests** — Hypothesis тесты для cache, safety, parallel_hls (10 тестов)
- **CI pipeline** — GitHub Actions: ruff → mypy → pytest

### Changed
- **Architecture refactor** — core downloader переписан на plugin system + event bus
- **CLI** — использует `download_file()` с plugin system + event bus прогресс
- **GUI** — использует plugin system, event bus для прогресс-бара
- **Version sync** — все файлы теперь показывают 1.2.0
- **Config migration** — авто-миграция старого JSON конфига в новый формат

### Fixed
- Path traversal protection в `validate_output_path()`
- Credentials leak в логах (`sanitize_url_for_log()` убирает user:pass@)
- OAuth token leak — `SecretStr` маскируется в логах/конфиге

## [1.1.1] - 2026-07-27

### Added
- **Parallel HLS download** — `download_hls_parallel()` с ThreadPoolExecutor (3-5x быстрее для видео)
- **Atomic JSON cache** — `Cache` класс с TTL, атомарной записью (tmp→rename), автоочисткой просроченных записей
- **Safety utilities** — `sanitize_url_for_log`, `validate_output_path`, `parse_proxy_url`, `build_proxy_dict` (нет секретов в логах, нет path traversal)
- **Connection pooling** — `requests.Session` + `HTTPAdapter` в `download_from_api` (pool_size=10)
- **CLI flags** — `--version`, `--parallel-segments`, `--pool-size`, `--proxy-auth`
- **Tests** — pytest suite для parallel_hls, cache, safety (11 тестов)
- **CI pipeline** — GitHub Actions: ruff → mypy → pytest

### Changed
- `download_hls()` теперь использует параллельный HLS как фоллбэк (workers=4, макс 16)
- `download_from_api()` переписан на `requests` с retry/pooling вместо urllib

## [1.1.0] - 2026-07-23

### Added
- **Docviewer fallback** — скачивание документов, фото и других файлов даже когда владелец отключил скачивание. Файлы рендерятся через Яндекс Документы и сохраняются как PDF.
- **Предупреждение о формате PDF** — всплывающее окно при скачивании DOCX/XLSX/PPTX, сообщающее что файл будет сохранён как PDF.
- **HLS-скачивание видео** — intercept m3u8 → ffmpeg для видео даже когда API возвращает пустой `href`.
- **Иконка приложения** — синий круг с буквой Y и стрелкой скачивания.

### Changed
- Описание README обновлено: добавлен раздел "Как это работает?" с объяснением трёх стратегий скачивания.

## [1.0.0] - 2026-07-22

### Features
- CLI и GUI интерфейс для скачивания файлов из Яндекс Диска
- Скачивание видео через HLS (m3u8 + ffmpeg)
- Скачивание файлов через API Яндекс Диска
- Выбор разрешения: 240p, 360p, 480p, 720p, 1080p
- 9 пресетов конвертации: best, balanced, compact, youtube, mobile, mp3, mp3-small, aac, remux
- Фильтрация по типам файлов: video, audio, image, document, archive, executable
- Фильтрация по папкам
- Возобновление прерванных скачиваний (HTTP Range)
- Проверка целостности (MD5)
- Очередь ссылок
- Расписание скачиваний (cron)
- Поддержка HTTP/SOCKS прокси
- Сохранение конфигурации
- Системные уведомления
- Пропуск уже скачанных файлов
- Сборка через PyInstaller (exe, portable, installer)
- GitHub Actions для автоматической сборки
- README на 6 языках (RU, EN, DE, FR, JA, ZH-TW)
