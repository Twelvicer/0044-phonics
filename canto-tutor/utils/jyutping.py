"""Jyutping conversion helpers."""

from __future__ import annotations


def lyrics_to_jyutping(lyrics_lines: list[str], pronunciation_dict: dict[str, str]) -> list[list[str]]:
    """Convert Chinese lyrics into Jyutping sequence (stub)."""
    converted: list[list[str]] = []
    for line in lyrics_lines:
        converted.append([pronunciation_dict.get(char, "") for char in line])
    return converted
