"""
Transformações geométricas - OpenCV (do V1)
Mais preciso que FFmpeg puro para rotações complexas
"""

import random
import numpy as np
import cv2
import subprocess
import os
import shutil

class GeometricEvasion:
    """Técnicas geométricas de ofuscação via OpenCV."""

    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def apply(self, input_path: str, output_path: str):
        """Aplica zoom + rotação + perspectiva."""
        # Usa FFmpeg para extrair frames, processa com OpenCV, remonta
        tmpdir = tempfile.mkdtemp()
        try:
            # Extrai frames
            frames_dir = os.path.join(tmpdir, "frames")
            os.makedirs(frames_dir)

            cmd = [
                "ffmpeg", "-i", input_path,
                "-vf", "fps=30,scale=1080:-2",
                os.path.join(frames_dir, "frame_%04d.png")
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            # Processa frames
            frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
            processed_dir = os.path.join(tmpdir, "processed")
            os.makedirs(processed_dir)

            for i, frame_name in enumerate(frames):
                frame = cv2.imread(os.path.join(frames_dir, frame_name))
                if frame is None:
                    continue

                # Aplica transformações
                frame = self._zoom_and_crop(frame)
                frame = self._micro_rotation(frame)

                cv2.imwrite(os.path.join(processed_dir, frame_name), frame)

            # Remonta vídeo
            cmd = [
                "ffmpeg", "-y", "-i", os.path.join(processed_dir, "frame_%04d.png"),
                "-vf", "fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-i", input_path,  # Áudio original
                "-c:a", "copy", "-shortest",
                output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        except Exception as e:
            print(f"Erro em geometric: {e}")
            shutil.copy2(input_path, output_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _zoom_and_crop(self, frame: np.ndarray, scale_range=(1.03, 1.06)) -> np.ndarray:
        """Zoom de 3-6% com crop central."""
        scale = random.uniform(*scale_range)
        h, w = frame.shape[:2]

        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Crop central
        x1 = (new_w - w) // 2
        y1 = (new_h - h) // 2
        return resized[y1:y1+h, x1:x1+w]

    def _micro_rotation(self, frame: np.ndarray, angle_range=(-0.3, 0.3)) -> np.ndarray:
        """Rotação de ±0.3°."""
        angle = random.uniform(*angle_range)
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    def perspective_micro_warp(self, frame: np.ndarray) -> np.ndarray:
        """Distorção de perspectiva sutil."""
        h, w = frame.shape[:2]

        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst = np.float32([
            [random.randint(0, 3), random.randint(0, 3)],
            [w - random.randint(0, 3), random.randint(0, 3)],
            [w - random.randint(0, 3), h - random.randint(0, 3)],
            [random.randint(0, 3), h - random.randint(0, 3)]
        ])

        matrix = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(frame, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
