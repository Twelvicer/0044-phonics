"""Alignment helpers."""

from __future__ import annotations

import logging
from typing import Any


def log_alignment_stats(logger: logging.Logger, stats: dict[str, Any]) -> None:
    """Log per-line alignment and speed-change statistics."""
    logger.info(
        (
            "句子对齐统计 | line=%s | text=%s | speed_ratio=%.3f "
            "| target_duration=%.3fs | actual_duration=%.3fs"
        ),
        stats.get("line_index", "-"),
        stats.get("text", ""),
        float(stats.get("speed_ratio", 1.0)),
        float(stats.get("target_duration", 0.0)),
        float(stats.get("actual_duration", 0.0)),
    )
