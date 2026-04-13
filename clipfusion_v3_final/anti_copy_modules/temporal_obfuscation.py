"""
Ofuscação temporal - SignalCut style
"""

import random
import subprocess
import shutil

class TemporalObfuscation:
    """Técnicas temporais de ofuscação."""

    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)

    def apply(self, input_path: str, output_path: str):
        """Aplica variação temporal (ghost mode)."""
        self.micro_speed_variation(input_path, output_path)

    def micro_speed_variation(self, input_path: str, output_path: str,
                             speed_range=(0.98, 1.02)):
        """Variação de velocidade ±2% - imperceptível."""
        speed = random.uniform(*speed_range)

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"setpts=PTS/{speed}",
            "-af", f"atempo={speed}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            output_path
        ]

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(input_path, output_path)
