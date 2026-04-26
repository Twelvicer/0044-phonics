"""Audio processing module stubs."""

from __future__ import annotations

from pathlib import Path


def stretch_audio_to_interval(
    raw_audio_map: dict[str, Path],
    timestamps: list[tuple[float, float]],
    beat_info: dict,
    output_dir: Path,
) -> None:
    """Time-stretch character audio to target intervals (stub)."""
    _ = raw_audio_map
    _ = timestamps
    _ = beat_info
    output_dir.mkdir(parents=True, exist_ok=True)
