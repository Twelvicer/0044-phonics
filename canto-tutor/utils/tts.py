"""Text-to-speech helpers.

Supports:
- Local placeholder fallback (no network, deterministic).
- Aliyun DashScope `qwen3-tts-flash-realtime` in commit mode.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
import threading
import wave


VOICE_BY_GENDER = {
    "male": "Rocky",
    "female": "kiki",
}


def _safe_token(token: str, fallback: str) -> str:
    """Sanitize token for file names."""
    clean = "".join(ch if ch.isalnum() else "_" for ch in token).strip("_")
    return clean or fallback


def _write_placeholder_wav(path: Path, duration_s: float = 0.18, sample_rate: int = 22050) -> None:
    """Create a short silent WAV as placeholder audio."""
    frame_count = int(duration_s * sample_rate)
    silence = b"\x00\x00" * frame_count  # 16-bit mono PCM silence

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(silence)


def _write_pcm_as_wav(path: Path, pcm_bytes: bytes, sample_rate: int = 24000) -> None:
    """Persist 16-bit mono PCM bytes to WAV container."""
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)


def _resolve_voice(voice_gender: str | None) -> str:
    if not voice_gender:
        return VOICE_BY_GENDER["female"]
    normalized = voice_gender.strip().lower()
    if normalized not in VOICE_BY_GENDER:
        raise ValueError(f"Unsupported voice_gender={voice_gender!r}, expected one of {sorted(VOICE_BY_GENDER)}")
    return VOICE_BY_GENDER[normalized]


def _synthesize_with_qwen_realtime(
    text: str,
    *,
    api_key: str,
    voice: str,
    model: str,
    url: str,
    timeout_s: float,
) -> bytes:
    """Synthesize one text fragment with DashScope realtime TTS (commit mode)."""
    import dashscope
    from dashscope.audio.qwen_tts_realtime import AudioFormat, QwenTtsRealtime, QwenTtsRealtimeCallback

    class _Callback(QwenTtsRealtimeCallback):
        def __init__(self) -> None:
            self.audio_chunks = bytearray()
            self.done_event = threading.Event()
            self.error: str | None = None

        def on_event(self, response) -> None:  # SDK callback signature
            event_type = response.get("type", "") if isinstance(response, dict) else ""
            if event_type == "response.audio.delta":
                delta_b64 = response.get("delta")
                if delta_b64:
                    self.audio_chunks.extend(base64.b64decode(delta_b64))
            elif event_type == "error":
                self.error = str(response)
                self.done_event.set()
            elif event_type == "response.done":
                self.done_event.set()

        def on_close(self, close_status_code, close_msg) -> None:
            _ = close_status_code
            _ = close_msg
            self.done_event.set()

    dashscope.api_key = api_key
    callback = _Callback()
    client = QwenTtsRealtime(model=model, callback=callback, url=url)

    try:
        client.connect()
        client.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode="commit",
        )
        client.append_text(text)
        client.commit()

        if not callback.done_event.wait(timeout=timeout_s):
            raise TimeoutError(f"Qwen realtime TTS timeout after {timeout_s}s")
        if callback.error:
            raise RuntimeError(f"Qwen realtime TTS error: {callback.error}")
        return bytes(callback.audio_chunks)
    finally:
        try:
            client.finish()
        except Exception:
            pass


def synthesize_char_audio(
    jyutping_seq: list[list[str]],
    output_dir: Path,
    *,
    provider: str = "placeholder",
    voice_gender: str | None = None,
    dashscope_api_key: str | None = None,
    timeout_s: float = 20.0,
    dashscope_url: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime",
) -> dict[str, Path]:
    """Synthesize per-character audio files and return token->path mapping.

    Args:
        provider: `placeholder` or `qwen3-tts-flash-realtime`.
        voice_gender: `male` or `female`, mapped to Rocky/kiki.
        dashscope_api_key: optional; falls back to DASHSCOPE_API_KEY env.
        dashscope_url: websocket endpoint; default uses China mainland (Beijing).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    voice = _resolve_voice(voice_gender)

    audio_map: dict[str, Path] = {}
    for line_idx, line in enumerate(jyutping_seq, start=1):
        for token_idx, token in enumerate(line, start=1):
            token = token.strip()
            if not token or token in audio_map:
                continue

            file_name = f"{_safe_token(token, fallback=f'line{line_idx}_tok{token_idx}')}.wav"
            file_path = output_dir / file_name

            if provider == "qwen3-tts-flash-realtime":
                api_key = dashscope_api_key or os.getenv("DASHSCOPE_API_KEY", "")
                if not api_key:
                    raise RuntimeError("Missing DashScope API key. Set DASHSCOPE_API_KEY or pass --dashscope-api-key.")
                pcm_audio = _synthesize_with_qwen_realtime(
                    token,
                    api_key=api_key,
                    voice=voice,
                    model="qwen3-tts-flash-realtime",
                    url=dashscope_url,
                    timeout_s=timeout_s,
                )
                _write_pcm_as_wav(file_path, pcm_audio)
            elif provider == "placeholder":
                _write_placeholder_wav(file_path)
            else:
                raise ValueError("Unsupported provider. Use 'placeholder' or 'qwen3-tts-flash-realtime'.")

            audio_map[token] = file_path

    return audio_map
