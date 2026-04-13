"""
Técnicas de ofuscação de áudio - SignalCut 7 camadas
"""

import random
import subprocess
import shutil

class AudioEvasion:
    """Técnicas de evasão de fingerprint de áudio."""

    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)

    def apply(self, input_path: str, output_path: str):
        """Aplica pitch shift ±1%."""
        self.pitch_shift(input_path, output_path)

    def pitch_shift(self, input_path: str, output_path: str):
        """Reamostragem de áudio: pitch/tempo ±1%."""
        pitch = random.uniform(0.99, 1.01)

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-af", f"asetrate=44100*{pitch},atempo={1/pitch}",
            "-c:v", "copy", output_path
        ]

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(input_path, output_path)
