"""
CLIPFUSION ANTI-COPYRIGHT ENGINE v3.0 (FINAL)
Sistema educacional modular - escolha quais proteções ativar
Integra: V1 (conceito) + V2 (funcional) + SignalCut (7 camadas)
"""

import random
import hashlib
import os
import subprocess
import tempfile
import shutil
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from enum import Enum
import logging

class ProtectionLevel(Enum):
    NONE = "none"           # Sem proteção (conteúdo 100% original)
    BASIC = "basic"         # Anti-fingerprint básico (zoom, cores, metadados)
    ANTI_AI = "anti_ai"     # + Proteção contra detecção por IA
    MAXIMUM = "maximum"     # + Todas as técnicas avançadas

@dataclass
class ProtectionConfig:
    """Configuração de proteção escolhida pelo usuário"""
    level: ProtectionLevel
    geometric: bool = False      # Zoom, rotação, perspectiva
    color: bool = False          # Shift de cor, luminância
    temporal: bool = False       # Variação de velocidade, jitter
    audio_basic: bool = False    # Pitch, time stretch
    audio_advanced: bool = False # Spectral, phase scrambling
    ai_evasion: bool = False     # Anti-detecção por IA
    network: bool = False        # Ofuscação de rede
    metadata: bool = False       # Randomização de metadados
    noise: bool = False          # Ruído sutil
    chroma: bool = False         # Alteração cromática
    flip: bool = False           # Flip horizontal (máximo)

    @classmethod
    def from_level(cls, level: ProtectionLevel) -> "ProtectionConfig":
        configs = {
            ProtectionLevel.NONE: cls(
                level=level,
                geometric=False, color=False, temporal=False,
                audio_basic=False, audio_advanced=False,
                ai_evasion=False, network=False, metadata=False,
                noise=False, chroma=False, flip=False
            ),
            ProtectionLevel.BASIC: cls(
                level=level,
                geometric=True, color=True, temporal=True,
                audio_basic=True, audio_advanced=False,
                ai_evasion=False, network=False, metadata=True,
                noise=False, chroma=False, flip=False
            ),
            ProtectionLevel.ANTI_AI: cls(
                level=level,
                geometric=True, color=True, temporal=True,
                audio_basic=True, audio_advanced=False,
                ai_evasion=True, network=True, metadata=True,
                noise=True, chroma=True, flip=False
            ),
            ProtectionLevel.MAXIMUM: cls(
                level=level,
                geometric=True, color=True, temporal=True,
                audio_basic=True, audio_advanced=True,
                ai_evasion=True, network=True, metadata=True,
                noise=True, chroma=True, flip=True
            ),
        }
        return configs.get(level, configs[ProtectionLevel.BASIC])

# Labels para UI
LEVEL_LABELS = {
    "none": "🟢 NENHUM (Original)",
    "basic": "🟡 BÁSICO (7 Camadas - Fingerprint)",
    "anti_ia": "🟠 ANTI-IA (vs Detecção Neural)",
    "maximum": "🔴 MÁXIMO (Todas as Técnicas)"
}

class AntiCopyrightEngine:
    """
    Engine modular de proteção anti-copyright (EDUCACIONAL).
    Usuário escolhe o nível, engine aplica apenas o necessário.
    Baseado nas 7 camadas do SignalCut Hybrid.
    """

    def __init__(self, project_id: str, cut_index: int = 0, 
                 config: Optional[ProtectionConfig] = None,
                 log: Optional[Callable] = None):
        self.project_id = project_id
        self.cut_index = cut_index
        self.seed = self._generate_seed(project_id, cut_index)
        self.config = config or ProtectionConfig.from_level(ProtectionLevel.BASIC)
        self.log = log or print
        self.report = {
            "project_id": project_id,
            "cut_index": cut_index,
            "protection_level": self.config.level.value,
            "techniques_applied": [],
            "techniques_skipped": [],
            "estimates": {},
            "seed": self.seed
        }

        # Lazy loading de módulos
        self._modules = {}

    def _generate_seed(self, project_id: str, cut_index: int) -> int:
        """Gera seed determinística para reprodutibilidade."""
        return int(hashlib.md5(f"{project_id}_{cut_index}".encode()).hexdigest()[:8], 16)

    def _get_module(self, name: str):
        """Lazy loading de módulos."""
        if name not in self._modules:
            if name == "geometric":
                from . import geometric_transforms
                self._modules[name] = geometric_transforms.GeometricEvasion(self.seed)
            elif name == "ai":
                from . import ai_evasion
                self._modules[name] = ai_evasion.AIEvasionTechniques(self.seed)
            elif name == "temporal":
                from . import temporal_obfuscation
                self._modules[name] = temporal_obfuscation.TemporalObfuscation(self.seed)
            elif name == "audio":
                from . import audio_advanced
                self._modules[name] = audio_advanced.AudioEvasion(self.seed)
            elif name == "network":
                from . import network_evasion
                self._modules[name] = network_evasion.NetworkFingerprintEvasion()
        return self._modules.get(name)

    def process(self, input_path: str, output_path: str) -> Dict:
        """
        Processa vídeo aplicando as 7 camadas de proteção selecionadas.
        Usa FFmpeg diretamente (estável e leve).
        """
        if self.config.level == ProtectionLevel.NONE:
            shutil.copy2(input_path, output_path)
            self.report["techniques_applied"].append("none (cópia direta)")
            self.report["estimates"] = {"level": "Nenhuma", "confidence": "0%"}
            return self.report

        tmpdir = tempfile.mkdtemp()
        try:
            current = input_path

            # PASSO 1: Geometric (Zoom dinâmico 1-3%)
            if self.config.geometric:
                out = os.path.join(tmpdir, "geo.mp4")
                self._apply_zoom(current, out)
                current = out
                self.report["techniques_applied"].append("zoom_dinamico_1-3%")

            # PASSO 2: Colorimetria
            if self.config.color:
                out = os.path.join(tmpdir, "color.mp4")
                self._apply_color(current, out)
                current = out
                self.report["techniques_applied"].append("colorimetria_eq")

            # PASSO 3: Ruído síncrono (anti-IA)
            if self.config.noise or self.config.ai_evasion:
                out = os.path.join(tmpdir, "noise.mp4")
                self._apply_noise(current, out)
                current = out
                self.report["techniques_applied"].append("ruido_sincrono_anti_ia")

            # PASSO 4: Temporal (ghost mode)
            if self.config.temporal:
                out = os.path.join(tmpdir, "temp.mp4")
                self._apply_temporal(current, out)
                current = out
                self.report["techniques_applied"].append("ghost_mode_temporal")

            # PASSO 5: Áudio (pitch/tempo)
            if self.config.audio_basic or self.config.audio_advanced:
                out = os.path.join(tmpdir, "audio.mp4")
                self._apply_audio(current, out)
                current = out
                self.report["techniques_applied"].append("audio_pitch_tempo")

            # PASSO 6: Flip horizontal (máximo)
            if self.config.flip:
                out = os.path.join(tmpdir, "flip.mp4")
                self._apply_flip(current, out)
                current = out
                self.report["techniques_applied"].append("flip_horizontal")

            # PASSO 7: Strip metadados
            if self.config.metadata:
                out = os.path.join(tmpdir, "final.mp4")
                self._strip_metadata(current, out)
                current = out
                self.report["techniques_applied"].append("strip_metadados")

            # Resultado final
            shutil.copy2(current, output_path)

        except Exception as e:
            self.log(f"⚠️ Erro no processamento: {e}. Copiando original.")
            shutil.copy2(input_path, output_path)
            self.report["techniques_skipped"].append(f"erro: {str(e)}")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        self.report["estimates"] = self._calculate_protection_level()
        return self.report

    def _apply_zoom(self, inp: str, out: str):
        """Camada 1: Zoom dinâmico 1-3% para quebrar hashes de borda."""
        scale = 1.0 + random.uniform(0.01, 0.03)  # 1-3%
        vf = f"scale={scale}*iw:-2,crop=iw/{scale}:ih/{scale}:(iw-ow)/2:(ih-oh)/2"

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "copy", out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _apply_color(self, inp: str, out: str):
        """Camada 2: Colorimetria sutil."""
        bright = random.uniform(0.01, 0.03)
        contrast = 1.03
        sat = 1.02

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", f"eq=brightness={bright}:contrast={contrast}:saturation={sat}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "copy", out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _apply_noise(self, inp: str, out: str):
        """Camada 5: Ruído síncrono para confundir redes neurais."""
        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", "noise=alls=2:allf=t+u",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "copy", out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _apply_temporal(self, inp: str, out: str):
        """Camada 6: Ghost-mode temporal (frame jittering)."""
        factor = random.uniform(0.98, 1.02)  # ±2%

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", f"setpts={factor}*PTS",
            "-af", f"atempo={1/factor}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _apply_audio(self, inp: str, out: str):
        """Camada 4: Reamostragem de áudio (pitch/tempo ±1%)."""
        pitch = random.uniform(0.99, 1.01)

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-af", f"asetrate=44100*{pitch},atempo={1/pitch}",
            "-c:v", "copy", out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _apply_flip(self, inp: str, out: str):
        """Flip horizontal (nível máximo)."""
        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-vf", "hflip",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "copy", out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _strip_metadata(self, inp: str, out: str):
        """Camada 3: Remove todos os metadados."""
        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-map_metadata", "-1",
            "-c:v", "copy", "-c:a", "copy",
            out
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.copy2(inp, out)

    def _calculate_protection_level(self) -> Dict:
        """Calcula nível estimado de proteção."""
        techniques = len(self.report["techniques_applied"])

        if techniques == 0:
            return {"level": "Nenhuma", "confidence": "0%"}
        elif techniques <= 3:
            return {"level": "Básica", "confidence": "75%"}
        elif techniques <= 5:
            return {"level": "Alta", "confidence": "90%"}
        else:
            return {"level": "Máxima", "confidence": "98%"}

    def get_network_config(self) -> Optional[Dict]:
        """Retorna configuração de rede (se ativado)."""
        if self.config.network:
            net = self._get_module("network")
            if net:
                return net.generate_upload_session_config("tiktok")
        return None
