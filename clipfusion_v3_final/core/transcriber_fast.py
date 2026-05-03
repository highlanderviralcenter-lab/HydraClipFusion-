from __future__ import annotations

import os
import subprocess
import tempfile


def fmt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h >= 1:
        return f"{int(h):02d}:{int(m):02d}:{s:05.2f}"
    return f"{int(m):02d}:{s:05.2f}"


class FastWhisperTranscriber:
    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8") -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def _extract_audio(self, video_path: str, wav_path: str) -> None:
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
            wav_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def transcribe(self, video_path: str, language: str = "pt"):
        if not os.path.exists(video_path):
            raise FileNotFoundError(video_path)

        try:
            from faster_whisper import WhisperModel
        except Exception as e:
            raise RuntimeError(
                "faster-whisper não está instalado no ambiente. "
                "Instale com: pip install faster-whisper soundfile ctranslate2"
            ) from e

        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "audio.wav")
            self._extract_audio(video_path, wav_path)

            model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

            segments_iter, info = model.transcribe(
                wav_path,
                language=language,
                vad_filter=True,
                beam_size=1,
                best_of=1,
                condition_on_previous_text=False,
                word_timestamps=True,
                vad_parameters={"min_silence_duration_ms": 300},
            )

            segments = []
            full_text = []

            for seg in segments_iter:
                text = (seg.text or "").strip()
                if not text:
                    continue
                item = {
                    "start": float(seg.start),
                    "end": float(seg.end),
                    "text": text,
                }
                segments.append(item)
                full_text.append(text)

            return {
                "text": " ".join(full_text).strip(),
                "segments": segments,
                "engine": "faster_whisper",
                "language": getattr(info, "language", language),
            }
