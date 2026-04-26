"""Text-to-speech module stubs."""

from __future__ import annotations

from pathlib import Path


def synthesize_char_audio(jyutping_seq: list[list[str]], output_dir: Path) -> dict[str, Path]:
    """Synthesize per-character audio files (stub)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return {}
