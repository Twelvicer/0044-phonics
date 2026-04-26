"""Beat analysis helpers."""

from __future__ import annotations

import logging


def log_beat_analysis(logger: logging.Logger, bpm: float, beat_count: int) -> None:
    """Log summary of beat analysis in a consistent format."""
    logger.info("Beat 分析结果: BPM=%.2f, beats=%s", bpm, beat_count)
