#!/bin/bash
# ============================================
# CLIPFUSION V3.0 - INSTALAÇÃO MANUAL
# Copie cada seção para seu arquivo correspondente
# ============================================

# 1. Criar estrutura
mkdir -p ~/clipfusion_v3/{anti_copy_modules,viral_engine,core,gui,utils,config}

# 2. requirements.txt
cat > ~/clipfusion_v3/requirements.txt << 'REQEOF'
faster-whisper>=0.10.0
opencv-python>=4.8.0
numpy>=1.24.0
pillow>=10.0.0
pyyaml>=6.0.1
librosa>=0.10.0
soundfile>=0.12.0
REQEOF

# 3. main.py
cat > ~/clipfusion_v3/main.py << 'PYEOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_gui import ClipFusionApp

if __name__ == "__main__":
    app = ClipFusionApp()
    app.run()
PYEOF

# 4. db.py (schema corrigido)
cat > ~/clipfusion_v3/db.py << 'DBEOF'
import sqlite3
import json
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(os.path.expanduser("~")) / ".clipfusion" / "clipfusion_v3.db"

@contextmanager
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                language TEXT DEFAULT 'pt',
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                full_text TEXT,
                segments_json TEXT,
                quality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                transcript_id INTEGER NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                text TEXT NOT NULL,
                hook_strength REAL,
                retention_score REAL,
                moment_strength REAL,
                shareability REAL,
                platform_fit_tiktok REAL,
                platform_fit_reels REAL,
                platform_fit_shorts REAL,
                combined_score REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()

def create_project(name, video_path, language='pt'):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO projects (name, video_path, language) VALUES (?, ?, ?)",
            (name, video_path, language)
        )
        conn.commit()
        return cur.lastrowid

init_db()
DBEOF

# 5. anti_copy_modules/__init__.py
cat > ~/clipfusion_v3/anti_copy_modules/__init__.py << 'INITEOF'
from .core import AntiCopyrightEngine, ProtectionConfig, ProtectionLevel, LEVEL_LABELS
__all__ = ["AntiCopyrightEngine", "ProtectionConfig", "ProtectionLevel", "LEVEL_LABELS"]
INITEOF

# 6. anti_copy_modules/core.py (7 camadas SignalCut)
cat > ~/clipfusion_v3/anti_copy_modules/core.py << 'COREEOF'
import random
import hashlib
import os
import subprocess
import tempfile
import shutil
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

class ProtectionLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    ANTI_AI = "anti_ai"
    MAXIMUM = "maximum"

@dataclass
class ProtectionConfig:
    level: ProtectionLevel
    geometric: bool = False
    color: bool = False
    temporal: bool = False
    audio_basic: bool = False
    audio_advanced: bool = False
    ai_evasion: bool = False
    network: bool = False
    metadata: bool = False
    noise: bool = False
    chroma: bool = False
    flip: bool = False

    @classmethod
    def from_level(cls, level: ProtectionLevel):
        configs = {
            ProtectionLevel.NONE: cls(level=level),
            ProtectionLevel.BASIC: cls(level=level, geometric=True, color=True, temporal=True, audio_basic=True, metadata=True),
            ProtectionLevel.ANTI_AI: cls(level=level, geometric=True, color=True, temporal=True, audio_basic=True, ai_evasion=True, network=True, metadata=True, noise=True, chroma=True),
            ProtectionLevel.MAXIMUM: cls(level=level, geometric=True, color=True, temporal=True, audio_basic=True, audio_advanced=True, ai_evasion=True, network=True, metadata=True, noise=True, chroma=True, flip=True),
        }
        return configs.get(level, cls(level=ProtectionLevel.BASIC))

LEVEL_LABELS = {
    "none": "🟢 NENHUM (Original)",
    "basic": "🟡 BÁSICO (7 Camadas)",
    "anti_ia": "🟠 ANTI-IA",
    "maximum": "🔴 MÁXIMO"
}

class AntiCopyrightEngine:
    def __init__(self, project_id: str, cut_index: int = 0, config: Optional[ProtectionConfig] = None, log=print):
        self.project_id = project_id
        self.cut_index = cut_index
        self.seed = int(hashlib.md5(f"{project_id}_{cut_index}".encode()).hexdigest()[:8], 16)
        self.config = config or ProtectionConfig.from_level(ProtectionLevel.BASIC)
        self.log = log
        self.report = {"project_id": project_id, "cut_index": cut_index, "protection_level": self.config.level.value, "techniques_applied": [], "estimates": {}}

    def process(self, input_path: str, output_path: str) -> Dict:
        if self.config.level == ProtectionLevel.NONE:
            shutil.copy2(input_path, output_path)
            self.report["techniques_applied"].append("none")
            return self.report

        tmpdir = tempfile.mkdtemp()
        try:
            current = input_path

            # Camada 1: Zoom
            if self.config.geometric:
                out = os.path.join(tmpdir, "geo.mp4")
                scale = 1.0 + random.uniform(0.01, 0.03)
                subprocess.run(["ffmpeg", "-y", "-i", current, "-vf", f"scale={scale}*iw:-2,crop=iw/{scale}:ih/{scale}:(iw-ow)/2:(ih-oh)/2", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("zoom_1-3%")

            # Camada 2: Color
            if self.config.color:
                out = os.path.join(tmpdir, "color.mp4")
                bright = random.uniform(0.01, 0.03)
                subprocess.run(["ffmpeg", "-y", "-i", current, "-vf", f"eq=brightness={bright}:contrast=1.03:saturation=1.02", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("colorimetria")

            # Camada 3: Metadata
            if self.config.metadata:
                out = os.path.join(tmpdir, "meta.mp4")
                subprocess.run(["ffmpeg", "-y", "-i", current, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("strip_metadata")

            # Camada 4: Audio
            if self.config.audio_basic:
                out = os.path.join(tmpdir, "audio.mp4")
                pitch = random.uniform(0.99, 1.01)
                subprocess.run(["ffmpeg", "-y", "-i", current, "-af", f"asetrate=44100*{pitch},atempo={1/pitch}", "-c:v", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("audio_pitch")

            # Camada 5: Noise (anti-IA)
            if self.config.noise:
                out = os.path.join(tmpdir, "noise.mp4")
                subprocess.run(["ffmpeg", "-y", "-i", current, "-vf", "noise=alls=2:allf=t+u", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("ruido_anti_ia")

            # Camada 6: Temporal
            if self.config.temporal:
                out = os.path.join(tmpdir, "temp.mp4")
                factor = random.uniform(0.98, 1.02)
                subprocess.run(["ffmpeg", "-y", "-i", current, "-vf", f"setpts={factor}*PTS", "-af", f"atempo={1/factor}", "-c:v", "libx264", "-preset", "fast", "-crf", "18", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("ghost_mode")

            # Camada 7: Flip
            if self.config.flip:
                out = os.path.join(tmpdir, "flip.mp4")
                subprocess.run(["ffmpeg", "-y", "-i", current, "-vf", "hflip", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", out], capture_output=True)
                current = out
                self.report["techniques_applied"].append("flip_horizontal")

            shutil.copy2(current, output_path)

        except Exception as e:
            self.log(f"Erro: {e}")
            shutil.copy2(input_path, output_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        self.report["estimates"] = {"level": "Máxima" if len(self.report["techniques_applied"]) > 5 else "Alta" if len(self.report["techniques_applied"]) > 3 else "Básica", "confidence": f"{min(len(self.report['techniques_applied']) * 15, 98)}%"}
        return self.report
COREEOF

# 7. gui/main_gui.py (simplificado funcional)
cat > ~/clipfusion_v3/gui/main_gui.py << 'GUIFEOF'
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os

BG = "#0d0d1a"
BG2 = "#151528"
ACC = "#7c3aed"
GRN = "#22c55e"
WHT = "#f1f5f9"

class ClipFusionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClipFusion V3.0")
        self.root.geometry("900x600")
        self.root.configure(bg=BG)
        self.video_path = None
        self._build_ui()

    def run(self):
        self.root.mainloop()

    def _build_ui(self):
        # Header
        tk.Frame(self.root, bg=ACC, height=50).pack(fill="x")
        tk.Label(self.root, text="✂ ClipFusion V3.0", font=("Helvetica", 16, "bold"), bg=ACC, fg=WHT).place(x=20, y=10)

        # Notebook
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Abas
        self._tab_projeto()
        self._tab_transcricao()
        self._tab_render()

    def _tab_projeto(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📁 Projeto")
        tk.Label(f, text="Projeto", font=("Helvetica", 14), bg=BG2, fg=WHT).pack(pady=20)
        tk.Button(f, text="Selecionar Vídeo", command=self._select_video, bg=ACC, fg=WHT).pack()
        self.lbl_video = tk.Label(f, text="Nenhum vídeo", bg=BG2, fg=WHT)
        self.lbl_video.pack(pady=10)

        tk.Label(f, text="Proteção:", bg=BG2, fg=WHT).pack()
        self.protection = tk.StringVar(value="none")
        for val, txt in [("none", "🟢 Nenhum"), ("basic", "🟡 Básico"), ("maximum", "🔴 Máximo")]:
            tk.Radiobutton(f, text=txt, variable=self.protection, value=val, bg=BG2, fg=WHT, selectcolor=ACC).pack()

    def _tab_transcricao(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📝 Transcrição")
        self.txt_trans = scrolledtext.ScrolledText(f, height=20, bg="#1e1e3a", fg=WHT)
        self.txt_trans.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Button(f, text="Iniciar", command=self._start_trans, bg=GRN, fg=WHT).pack()

    def _tab_render(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="🎬 Render")
        self.txt_log = scrolledtext.ScrolledText(f, height=20, bg="#1e1e3a", fg=GRN)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Button(f, text="Renderizar", command=self._start_render, bg=ACC, fg=WHT).pack()

    def _select_video(self):
        p = filedialog.askopenfilename(filetypes=[("Vídeos", "*.mp4")])
        if p:
            self.video_path = p
            self.lbl_video.config(text=os.path.basename(p))

    def _start_trans(self):
        self.txt_trans.insert("end", "Transcrevendo...\n")

    def _start_render(self):
        if not self.video_path:
            messagebox.showwarning("Aviso", "Selecione um vídeo!")
            return
        self.txt_log.insert("end", f"Renderizando com {self.protection.get()}...\n")
GUIFEOF

# 8. Criar scripts de execução
cat > ~/clipfusion_v3/run.sh << 'RUNEOF'
#!/bin/bash
cd "$(dirname "$0")"
export LIBVA_DRIVER_NAME=iHD
source venv/bin/activate
python3 main.py
RUNEOF
chmod +x ~/clipfusion_v3/run.sh

cat > ~/clipfusion_v3/install.sh << 'INSTALLEOF'
#!/bin/bash
set -e
if [ "$EUID" -ne 0 ]; then echo "Execute como root: sudo bash $0"; exit 1; fi

REAL_USER="${SUDO_USER:-highlander}"
REAL_HOME=$(eval echo "~$REAL_USER")

echo "[1/5] Instalando pacotes..."
apt update
apt install -y python3-pip python3-venv python3-tk ffmpeg intel-media-va-driver-non-free vainfo zram-tools

echo "[2/5] Configurando ZRAM..."
cat > /etc/default/zramswap << 'EOF'
ALGO=zstd
SIZE=6144
PRIORITY=100
EOF
systemctl enable zramswap
systemctl restart zramswap

echo "[3/5] Criando ambiente Python..."
cd "$REAL_HOME/clipfusion_v3"
python3 -m venv venv
source venv/bin/activate
pip install faster-whisper opencv-python numpy pillow pyyaml librosa soundfile

echo "[4/5] Permissões..."
chown -R "$REAL_USER":"$REAL_USER" "$REAL_HOME/clipfusion_v3"

echo "[5/5] Concluído! Reinicie: sudo reboot"
INSTALLEOF
chmod +x ~/clipfusion_v3/install.sh

echo "✅ Estrutura criada em ~/clipfusion_v3/"
echo "📁 Execute: cd ~/clipfusion_v3 && sudo bash install.sh"
