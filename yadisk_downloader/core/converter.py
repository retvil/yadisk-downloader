"""Post-download video conversion with named presets."""

import os
import subprocess
from dataclasses import dataclass


@dataclass
class Preset:
    """Conversion preset definition."""
    name: str
    description: str
    video_codec: str | None  # None for audio-only
    audio_codec: str | None
    resolution: str | None  # None = keep original
    crf: int | None
    audio_bitrate: str | None
    output_ext: str
    extra_args: list[str] | None = None


PRESETS: dict[str, Preset] = {
    "best": Preset(
        name="best",
        description="Maximum quality, H.265, ~60% of original size",
        video_codec="libx265",
        audio_codec="aac",
        resolution=None,
        crf=20,
        audio_bitrate="192k",
        output_ext=".mp4",
    ),
    "balanced": Preset(
        name="balanced",
        description="Good quality/size balance, H.264",
        video_codec="libx264",
        audio_codec="aac",
        resolution=None,
        crf=23,
        audio_bitrate="128k",
        output_ext=".mp4",
    ),
    "compact": Preset(
        name="compact",
        description="Small file, 480p, for mobile/storage",
        video_codec="libx264",
        audio_codec="aac",
        resolution="480",
        crf=26,
        audio_bitrate="96k",
        output_ext=".mp4",
    ),
    "youtube": Preset(
        name="youtube",
        description="Optimized for YouTube upload, 1080p",
        video_codec="libx264",
        audio_codec="aac",
        resolution="1080",
        crf=20,
        audio_bitrate="192k",
        output_ext=".mp4",
    ),
    "mobile": Preset(
        name="mobile",
        description="Tiny file, 360p, for phones",
        video_codec="libx264",
        audio_codec="aac",
        resolution="360",
        crf=28,
        audio_bitrate="64k",
        output_ext=".mp4",
    ),
    "mp3": Preset(
        name="mp3",
        description="Extract audio as MP3 320kbps",
        video_codec=None,
        audio_codec="libmp3lame",
        resolution=None,
        crf=None,
        audio_bitrate="320k",
        output_ext=".mp3",
        extra_args=["-vn"],
    ),
    "mp3-small": Preset(
        name="mp3-small",
        description="Extract audio as MP3 128kbps",
        video_codec=None,
        audio_codec="libmp3lame",
        resolution=None,
        crf=None,
        audio_bitrate="128k",
        output_ext=".mp3",
        extra_args=["-vn"],
    ),
    "aac": Preset(
        name="aac",
        description="Extract audio as AAC 256kbps",
        video_codec=None,
        audio_codec="aac",
        resolution=None,
        crf=None,
        audio_bitrate="256k",
        output_ext=".m4a",
        extra_args=["-vn"],
    ),
    "remux": Preset(
        name="remux",
        description="Copy streams to MP4 container (fast, no re-encode)",
        video_codec=None,
        audio_codec=None,
        resolution=None,
        crf=None,
        audio_bitrate=None,
        output_ext=".mp4",
        extra_args=["-c", "copy"],
    ),
}


def list_presets() -> str:
    """Return formatted string of all available presets."""
    lines = ["Available presets:\n"]
    for name, preset in PRESETS.items():
        lines.append(f"  {name:12s} — {preset.description}")
    return "\n".join(lines)


def get_output_path(input_path: str, preset_name: str) -> str:
    """Generate output filename for a preset.

    Example: video.mp4 → video_balanced.mp4 / video.mp3
    """
    preset = PRESETS[preset_name]
    base, _ = os.path.splitext(input_path)
    return f"{base}_{preset.name}{preset.output_ext}"


def convert(
    ffmpeg_path: str,
    input_path: str,
    output_path: str,
    preset_name: str,
) -> tuple[bool, int]:
    """Convert a video file using a named preset.

    Args:
        ffmpeg_path: Path to ffmpeg binary.
        input_path: Source video file.
        output_path: Destination file path.
        preset_name: Name of the conversion preset.

    Returns:
        Tuple of (success, output_file_size_bytes).
    """
    if preset_name not in PRESETS:
        return False, 0

    preset = PRESETS[preset_name]
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    cmd = [ffmpeg_path, "-i", input_path]

    # Video codec
    if preset.video_codec:
        cmd.extend(["-c:v", preset.video_codec])

    # Resolution
    if preset.resolution:
        cmd.extend(["-vf", f"scale=-2:{preset.resolution}"])

    # CRF
    if preset.crf is not None:
        cmd.extend(["-crf", str(preset.crf)])

    # Audio codec
    if preset.audio_codec:
        cmd.extend(["-c:a", preset.audio_codec])

    # Audio bitrate
    if preset.audio_bitrate:
        cmd.extend(["-b:a", preset.audio_bitrate])

    # Extra args
    if preset.extra_args:
        cmd.extend(preset.extra_args)

    cmd.extend(["-y", output_path])

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=7200)
        if result.returncode == 0 and os.path.exists(output_path):
            return True, os.path.getsize(output_path)
        return False, 0
    except Exception:
        return False, 0
