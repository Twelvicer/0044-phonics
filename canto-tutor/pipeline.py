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


def _ask_voice_gender() -> str:
    """Ask user whether to use male/female voice and return normalized value."""
    try:
        selected = input("请选择音色（male/female）：").strip().lower()
    except EOFError:
        selected = "female"

    if selected not in {"male", "female"}:
        selected = "female"
    return selected


def run_pipeline(
    lyrics_path: Path,
    song_path: Path,
    timestamps_path: Path,
    char_audio_dir: Path,
    stretched_audio_dir: Path,
    tts_provider: str,
    voice_gender: str,
    dashscope_api_key: str | None,
    dashscope_url: str,
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
        provider=tts_provider,
        voice_gender=voice_gender,
        dashscope_api_key=dashscope_api_key,
        dashscope_url=dashscope_url,
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
    parser.add_argument(
        "--tts-provider",
        choices=["placeholder", "qwen3-tts-flash-realtime"],
        default="placeholder",
        help="TTS provider. Use qwen3-tts-flash-realtime to call DashScope realtime API.",
    )
    parser.add_argument(
        "--voice-gender",
        choices=["male", "female"],
        default=None,
        help="Voice gender; mapped to Rocky (male) / kiki (female).",
    )
    parser.add_argument(
        "--dashscope-api-key",
        default=None,
        help="DashScope API key. If omitted, use DASHSCOPE_API_KEY env var.",
    )
    parser.add_argument(
        "--dashscope-url",
        default="wss://dashscope.aliyuncs.com/api-ws/v1/realtime",
        help="DashScope websocket endpoint; default is China mainland (Beijing) route.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    voice_gender = args.voice_gender or _ask_voice_gender()

    run_pipeline(
        lyrics_path=args.lyrics,
        song_path=args.song,
        timestamps_path=args.timestamps,
        char_audio_dir=args.char_audio_dir,
        stretched_audio_dir=args.char_audio_stretched_dir,
        tts_provider=args.tts_provider,
        voice_gender=voice_gender,
        dashscope_api_key=args.dashscope_api_key,
        dashscope_url=args.dashscope_url,
    )


if __name__ == "__main__":
    main()
