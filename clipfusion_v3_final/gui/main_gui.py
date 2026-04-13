"""
ClipFusion GUI v3.0 - Interface 7 Abas (Simplificada)
Tkinter otimizado para i5-6200U
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os

# Cores SignalCut
BG = "#0d0d1a"
BG2 = "#151528"
BG3 = "#1e1e3a"
ACC = "#7c3aed"
GRN = "#22c55e"
RED = "#ef4444"
YEL = "#f59e0b"
WHT = "#f1f5f9"
GRY = "#64748b"

class ClipFusionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✂ ClipFusion Viral Pro v3.0")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)

        self.video_path = None
        self.project_name = tk.StringVar(value="Meu Projeto")

        self._build_ui()

    def run(self):
        self.root.mainloop()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=ACC, height=60)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✂ ClipFusion Viral Pro v3.0", 
                font=("Helvetica", 16, "bold"), bg=ACC, fg=WHT).pack(pady=15)

        # Notebook (7 abas)
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Estilo
        style = ttk.Style()
        style.configure("TNotebook", background=BG2)
        style.configure("TNotebook.Tab", background=BG3, foreground=GRY, padding=10)

        # Abas
        self._tab_projeto()
        self._tab_transcricao()
        self._tab_ia()
        self._tab_cortes()
        self._tab_render()
        self._tab_historico()
        self._tab_agenda()

    def _tab_projeto(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📁 Projeto")

        tk.Label(f, text="Novo Projeto", font=("Helvetica", 14, "bold"), 
                bg=BG2, fg=WHT).pack(pady=20)

        tk.Label(f, text="Nome:", bg=BG2, fg=WHT).pack(anchor="w", padx=30)
        tk.Entry(f, textvariable=self.project_name, width=40).pack(padx=30, pady=5)

        tk.Button(f, text="📂 Selecionar Vídeo", command=self._select_video,
                 bg=ACC, fg=WHT).pack(pady=20)

        self.lbl_video = tk.Label(f, text="Nenhum vídeo selecionado", 
                                 bg=BG2, fg=GRY)
        self.lbl_video.pack()

        # Anti-copyright nível
        tk.Label(f, text="Proteção Anti-Copyright:", bg=BG2, fg=WHT).pack(pady=10)
        self.protection = tk.StringVar(value="none")
        for val, txt in [("none", "🟢 Nenhum"), ("basic", "🟡 Básico"), 
                        ("anti_ai", "🟠 Anti-IA"), ("maximum", "🔴 Máximo")]:
            tk.Radiobutton(f, text=txt, variable=self.protection, value=val,
                          bg=BG2, fg=WHT, selectcolor=ACC).pack(anchor="w", padx=30)

    def _tab_transcricao(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📝 Transcrição")

        tk.Label(f, text="Transcrição Whisper", font=("Helvetica", 12), 
                bg=BG2, fg=WHT).pack(pady=10)

        self.txt_trans = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=WHT)
        self.txt_trans.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="▶ Iniciar Transcrição", command=self._start_transcription,
                 bg=GRN, fg=WHT).pack(pady=10)

    def _tab_ia(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="🤖 IA Externa")

        tk.Label(f, text="Prompt para IA Externa", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_prompt = scrolledtext.ScrolledText(f, height=10, bg=BG3, fg="#a5b4fc")
        self.txt_prompt.pack(fill="x", padx=20, pady=5)

        tk.Button(f, text="📋 Gerar Prompt", command=self._generate_prompt,
                 bg=ACC, fg=WHT).pack(pady=5)

        tk.Label(f, text="Resposta da IA (JSON):", bg=BG2, fg=WHT).pack(pady=5)
        self.txt_resp = scrolledtext.ScrolledText(f, height=10, bg=BG3, fg=GRN)
        self.txt_resp.pack(fill="both", expand=True, padx=20, pady=5)

    def _tab_cortes(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="✂ Cortes")

        tk.Label(f, text="Cortes Sugeridos (18-35s)", bg=BG2, fg=WHT).pack(pady=10)

        self.lst_cuts = tk.Listbox(f, bg=BG3, fg=WHT, height=15)
        self.lst_cuts.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="✅ Aprovar Selecionado", bg=GRN, fg=WHT).pack(side="left", padx=20)
        tk.Button(f, text="❌ Rejeitar", bg=RED, fg=WHT).pack(side="right", padx=20)

    def _tab_render(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="🎬 Render")

        tk.Label(f, text="Progresso do Render", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_log = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=GRN)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="🎬 Iniciar Render", command=self._start_render,
                 bg=ACC, fg=WHT).pack(pady=10)

    def _tab_historico(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📋 Histórico")

        tk.Label(f, text="Projetos Anteriores", bg=BG2, fg=WHT).pack(pady=10)

        tree = ttk.Treeview(f, columns=("ID", "Nome", "Data"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Nome", text="Nome")
        tree.heading("Data", text="Data")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

    def _tab_agenda(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="📅 Agenda")

        tk.Label(f, text="Agenda de Postagem", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_agenda = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=GRN)
        self.txt_agenda.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="📅 Gerar Agenda", bg=ACC, fg=WHT).pack(pady=10)

    def _select_video(self):
        p = filedialog.askopenfilename(filetypes=[("Vídeos", "*.mp4 *.mkv *.mov")])
        if p:
            self.video_path = p
            self.lbl_video.config(text=f"✅ {os.path.basename(p)}", fg=GRN)

    def _start_transcription(self):
        self.txt_trans.insert("end", "📝 Iniciando transcrição...\n")
        # Thread para não travar GUI
        threading.Thread(target=self._transcribe_worker, daemon=True).start()

    def _transcribe_worker(self):
        # Simulação - em produção, chamar Whisper aqui
        import time
        time.sleep(2)
        self.root.after(0, lambda: self.txt_trans.insert("end", "✅ Transcrição completa!\n"))

    def _generate_prompt(self):
        prompt = f"""Analise o vídeo '{self.project_name.get()}'.
Gere cortes virais de 18-35 segundos.
Retorne JSON com: start, end, title, hook, score."""
        self.txt_prompt.delete("1.0", "end")
        self.txt_prompt.insert("1.0", prompt)

    def _start_render(self):
        protection = self.protection.get()
        self.txt_log.insert("end", f"🎬 Iniciando render com proteção: {protection}\n")
        threading.Thread(target=self._render_worker, daemon=True).start()

    def _render_worker(self):
        import time
        time.sleep(3)
        self.root.after(0, lambda: self.txt_log.insert("end", "✅ Render completo!\n"))
