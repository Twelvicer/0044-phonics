"""Canto tutor pipeline entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from utils.audio_process import stretch_audio_to_interval
from utils.beat_analysis import analyze_beats
from utils.dictionary import load_pronunciation_dictionary
from utils.jyutping import lyrics_to_jyutping
from utils.time_align import align_chars_to_timestamps
from utils.tts import synthesize_char_audio


def run_pipeline(
    lyrics_path: Path,
    song_path: Path,
    timestamps_path: Path,
    char_audio_dir: Path,
    stretched_audio_dir: Path,
) -> None:
    """Run end-to-end canto tutor generation pipeline.

    Current implementation is a scaffold and will be filled in iteratively.
    """
    pronunciation_dict = load_pronunciation_dictionary()
    lyrics_lines = lyrics_path.read_text(encoding="utf-8").splitlines()
    timestamps = align_chars_to_timestamps(lyrics_lines, timestamps_path)
    jyutping_seq = lyrics_to_jyutping(lyrics_lines, pronunciation_dict)
    beat_info = analyze_beats(song_path)

    raw_audio_map = synthesize_char_audio(
        jyutping_seq=jyutping_seq,
        output_dir=char_audio_dir,
    )

    stretch_audio_to_interval(
        raw_audio_map=raw_audio_map,
        timestamps=timestamps,
        beat_info=beat_info,
        output_dir=stretched_audio_dir,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cantonese tutor pipeline")
    parser.add_argument("--lyrics", type=Path, default=Path("input/lyrics.txt"))
    parser.add_argument("--song", type=Path, default=Path("input/song.mp3"))
    parser.add_argument("--timestamps", type=Path, default=Path("input/timestamps.txt"))
    parser.add_argument("--char-audio-dir", type=Path, default=Path("output/char_audio"))
    parser.add_argument(
        "--char-audio-stretched-dir",
        type=Path,
        default=Path("output/char_audio_stretched"),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    run_pipeline(
        lyrics_path=args.lyrics,
        song_path=args.song,
        timestamps_path=args.timestamps,
        char_audio_dir=args.char_audio_dir,
        stretched_audio_dir=args.char_audio_stretched_dir,
    )


if __name__ == "__main__":
    main()
