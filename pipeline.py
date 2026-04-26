"""Core pipeline with unified logging for synthesis/alignment workflow."""

from __future__ import annotations

import logging
from typing import Iterable

from tqdm import tqdm

from utils.alignment import log_alignment_stats
from utils.beat import log_beat_analysis

LOGGER_NAME = "phonics.pipeline"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure consistent logging format for the whole pipeline."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        logger.setLevel(level)
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def synthesize_chars(chars: Iterable[str], logger: logging.Logger | None = None) -> None:
    """Example synthesis loop with tqdm + logging progress output."""
    logger = logger or setup_logging()
    char_list = list(chars)
    total = len(char_list)

    for idx, ch in enumerate(tqdm(char_list, desc="字符合成", unit="char"), start=1):
        logger.info("正在合成第 %s/%s 个字: %s", idx, total, ch)
        # TODO: call real synthesizer here.


def run_pipeline(chars: Iterable[str], bpm: float, beat_count: int, alignment_stats: dict) -> None:
    """Run a minimal pipeline and emit unified logs for key checkpoints."""
    logger = setup_logging()
    logger.info("开始执行音频处理流水线")

    synthesize_chars(chars, logger=logger)

    log_beat_analysis(logger=logger, bpm=bpm, beat_count=beat_count)
    log_alignment_stats(logger=logger, stats=alignment_stats)

    logger.info("流水线执行完成")


if __name__ == "__main__":
    sample_chars = list("海阔天空")
    sample_alignment_stats = {
        "line_index": 1,
        "text": "今天我寒夜里看雪飘过",
        "speed_ratio": 1.04,
        "target_duration": 3.12,
        "actual_duration": 3.01,
    }
    run_pipeline(sample_chars, bpm=74.5, beat_count=128, alignment_stats=sample_alignment_stats)
