# yadisk-downloader

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

**Скачивание файлов из Яндекс Диска по ссылкам, где прямое скачивание запрещено.**

[🇬🇧 English](README.en.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇯🇵 日本語](README.ja.md) | [🇹🇼 繁體中文](README.zh-TW.md)

## Что это?

Яндекс Диск широко используется для обмена записями конференций, лекциями, онлайн-курсами и другими файлами. Но часто авторы запрещают прямое скачивание — приходится кликать на каждый файл отдельно, выбирать качество вручную и ждать.

**yadisk-downloader** решает эту проблему: вставьте публичную ссылку, и инструмент скачает все файлы за один раз с выбором разрешения, умными пресетами конвертации и современным графическим интерфейсом.

## Возможности

- **Массовое скачивание одной командой** — вставьте ссылку, получите все файлы
- **Все типы файлов** — видео, аудио, изображения, документы, архивы, исполняемые файлы
- **Выбор разрешения** — 240p, 360p, 480p, 720p или 1080p
- **9 пресетов конвертации** — H.265, H.264, MP3, AAC и другие
- **CLI + GUI** — автоматизация через командную строку или графический интерфейс
- **Фильтрация по папкам** — скачивание только определённых папок
- **Фильтрация по типам** — скачивание только определённых типов файлов
- **Отслеживание прогресса** — скорость, ETA и процент для каждого файла
- **Возобновление скачивания** — продолжение прерванных загрузок
- **Проверка целостности** — верификация файлов через MD5
- **Очередь ссылок** — управление несколькими URL
- **Расписание** — скачивание по расписанию (cron)
- **Поддержка прокси** — HTTP/SOCKS прокси для скачивания
- **Конфигурация** — сохранение настроек для повторного использования
- **Уведомления** — системные уведомления по завершении
- **Пропуск существующих** — не скачивает файлы заново
- **Кроссплатформенность** — работает на Windows, macOS и Linux

## Готовые сборки

Скачайте готовую сборку для вашей ОС из [Releases](https://github.com/retvil/yadisk-downloader/releases):

- **Windows** — `yadisk-downloader-windows.zip` (portable)
- **macOS** — `yadisk-downloader-macos.zip`
- **Linux** — `yadisk-downloader-linux.zip`

При первом запуске программа предложит скачать Chromium (~200MB) — это нужно для скачивания файлов.

## Быстрый старт

```bash
# Установка
pip install -r requirements.txt
playwright install chromium

# Скачивание всех файлов по публичной ссылке
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

Готово. Файлы появятся в `./downloads/`, организованные по папкам.

## Установка

### Требования

- **Python 3.10+** — [python.org](https://python.org)
- **ffmpeg** — нужен для скачивания и конвертации видео

### Установка ffmpeg

**Windows (winget):**
```bash
winget install Gyan.FFmpeg
```

**Windows (Chocolatey):**
```bash
choco install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

Альтернативно, `imageio-ffmpeg` устанавливается автоматически и предоставляет встроенный ffmpeg.

### Установка yadisk-downloader

```bash
# Клонирование репозитория
git clone https://github.com/retvil/yadisk-downloader.git
cd yadisk-downloader

# Установка зависимостей
pip install -r requirements.txt

# Установка браузера Playwright (Chromium)
playwright install chromium
```

Или установка как пакета:

```bash
pip install -e .
playwright install chromium
```

## Использование

### CLI

#### Базовое скачивание

```bash
# Скачать все файлы (по умолчанию: 720p)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX
```

#### Выбор разрешения

```bash
# Скачать в 1080p
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 1080p

# Скачать в 240p (минимальный размер, экономия трафика)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -r 240p
```

#### Фильтрация по папкам

```bash
# Скачать только одну папку
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -f "Главный зал"
```

#### Конвертация после скачивания

```bash
# Конвертация в H.265 (лучшее качество, ~60% от оригинала)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset best

# Оптимизация для YouTube (1080p H.264)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset youtube

# Извлечение только аудио (MP3 320kbps)
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset mp3

# Конвертация и удаление оригиналов
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --preset compact --delete-original
```

#### Просмотр файлов

```bash
# Показать все файлы без скачивания
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --list

# Показать доступные пресеты конвертации
python -m yadisk_downloader --preset-list

# Показать доступные типы файлов
python -m yadisk_downloader --type-list
```

#### Фильтрация по типам файлов

```bash
# Скачать только видео
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video

# Скачать видео и документы
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type video,document

# Скачать всё кроме архивов и исполняемых файлов
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --exclude archive,executable

# Скачать только изображения
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --type image
```

Доступные типы файлов: `video`, `audio`, `image`, `document`, `archive`, `executable`, `other`

#### Произвольная папка вывода

```bash
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX -o ./my_files
```

#### Поддержка прокси

```bash
# Использовать HTTP прокси
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --proxy http://proxy:8080

# Использовать SOCKS прокси
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --proxy socks5://proxy:1080
```

#### Уведомления

```bash
# Системное уведомление по завершении скачивания
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --notify
```

#### Файл конфигурации

```bash
# Сохранить текущие настройки
python -m yadisk_downloader --save-config -r 1080p --notify --proxy http://proxy:8080

# Показать текущую конфигурацию
python -m yadisk_downloader --show-config

# Использовать произвольный конфиг
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --config ./my-config.json
```

Расположение файла конфигурации: `~/.yadisk-downloader/config.json`

#### Возобновление прерванных скачиваний

```bash
# Отключить возобновление
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --no-resume

# Очистить состояние для URL
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --clear-state
```

#### Проверка целостности

```bash
# Скачивание с проверкой целостности
python -m yadisk_downloader https://disk.yandex.ru/d/XXXXX --checksum
```

#### Очередь ссылок

```bash
# Добавить URL в очередь
python -m yadisk_downloader --queue-add https://disk.yandex.ru/d/XXXXX
python -m yadisk_downloader --queue-add https://disk.yandex.ru/d/YYYYY

# Показать очередь
python -m yadisk_downloader --queue-show

# Обработать все элементы очереди
python -m yadisk_downloader --queue-process
```

#### Расписание скачиваний

```bash
# Добавить запланированное скачивание (каждый день в 9:00)
python -m yadisk_downloader --schedule-add https://disk.yandex.ru/d/XXXXX --cron "0 9 * * *"

# Показать запланированные скачивания
python -m yadisk_downloader --schedule-show

# Запустить планировщик
python -m yadisk_downloader --schedule-run
```

### GUI режим

```bash
python -m yadisk_downloader --gui
```

## Пресеты конвертации

| Пресет | Кодек | Разрешение | Аудио | Размер | Назначение |
|--------|-------|------------|-------|--------|------------|
| `best` | H.265 | Оригинал | AAC 192k | ~60% | Архивирование, максимальное качество |
| `balanced` | H.264 | Оригинал | AAC 128k | ~70% | Общее использование |
| `compact` | H.264 | 480p | AAC 96k | ~30% | Мобильные устройства |
| `youtube` | H.264 | 1080p | AAC 192k | ~80% | YouTube/соцсети |
| `mobile` | H.264 | 360p | AAC 64k | ~20% | Телефоны |
| `mp3` | — | — | MP3 320k | ~5% | Подкасты |
| `mp3-small` | — | — | MP3 128k | ~3% | Голос |
| `aac` | — | — | AAC 256k | ~5% | Современный аудиоформат |
| `remux` | Copy | Copy | Copy | ~100% | Смена формата |

## Сборка

Для разработчиков — сборка самостоятельно:

```bash
# Установить зависимости для сборки
pip install pyinstaller imageio-ffmpeg

# Собрать для текущей ОС
python build.py

# Собрать для конкретной платформы
python build.py --platform windows
python build.py --platform macos
python build.py --platform linux
```

Результаты сборки появятся в папке `releases/`.

Автоматическая сборка также настроена через GitHub Actions — при пуше тега `v*` сборки создаются автоматически.

## Лицензия

MIT License — см. файл [LICENSE](LICENSE).
