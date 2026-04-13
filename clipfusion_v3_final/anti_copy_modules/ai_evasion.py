"""
Técnicas anti-detecção por IA - SignalCut style
"""

import random
import subprocess
import shutil

class AIEvasionTechniques:
    """Técnicas de evasão contra detecção por IA."""

    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)

    def apply(self, input_path: str, output_path: str):
        """Aplica ruído anti-IA."""
        self.semantic_jitter(input_path, output_path)

    def semantic_jitter(self, input_path: str, output_path: str):
        """Ruído imperceptível que confunde redes neurais."""
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "noise=alls=2:allf=t+u",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy", output_path
        ]

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(input_path, output_path)
