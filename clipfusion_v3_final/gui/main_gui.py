"""
ClipFusion GUI v3.0 - Interface 7 Abas
Tkinter otimizado para i5-6200U
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import sys

# garante que o projeto raiz está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from core.candidate_engine import generate_candidates
from core.hybrid_parser import parse_ai_response, validate_ai_cut
from core.scoring_engine import ScoringEngine

BG  = "#0d0d1a"
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
        self.root.title("ClipFusion Viral Pro v3.0")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)

        self.video_path   = None
        self.project_id   = None
        self.transcript   = None
        self.candidates   = []
        self.project_name = tk.StringVar(value="Meu Projeto")

        self._build_ui()

    def run(self):
        self.root.mainloop()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=ACC, height=60)
        hdr.pack(fill="x")
        tk.Label(hdr, text="ClipFusion Viral Pro v3.0",
                 font=("Helvetica", 16, "bold"), bg=ACC, fg=WHT).pack(pady=15)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("TNotebook",     background=BG2)
        style.configure("TNotebook.Tab", background=BG3, foreground=GRY, padding=10)

        self._tab_projeto()
        self._tab_transcricao()
        self._tab_ia()
        self._tab_cortes()
        self._tab_render()
        self._tab_historico()
        self._tab_agenda()

    def _tab_projeto(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Projeto")

        tk.Label(f, text="Novo Projeto", font=("Helvetica", 14, "bold"),
                 bg=BG2, fg=WHT).pack(pady=20)

        tk.Label(f, text="Nome:", bg=BG2, fg=WHT).pack(anchor="w", padx=30)
        tk.Entry(f, textvariable=self.project_name, width=40).pack(padx=30, pady=5)

        tk.Button(f, text="Selecionar Video", command=self._select_video,
                  bg=ACC, fg=WHT).pack(pady=20)

        self.lbl_video = tk.Label(f, text="Nenhum video selecionado", bg=BG2, fg=GRY)
        self.lbl_video.pack()

        tk.Button(f, text="Criar Projeto", command=self._criar_projeto,
                  bg=GRN, fg=WHT, font=("Helvetica", 11, "bold")).pack(pady=15)

        self.lbl_projeto = tk.Label(f, text="", bg=BG2, fg=GRY)
        self.lbl_projeto.pack()

        tk.Label(f, text="Protecao Anti-Copyright:", bg=BG2, fg=WHT).pack(pady=10)
        self.protection = tk.StringVar(value="none")
        for val, txt in [("none", "Nenhum"), ("basic", "Basico"),
                         ("anti_ai", "Anti-IA"), ("maximum", "Maximo")]:
            tk.Radiobutton(f, text=txt, variable=self.protection, value=val,
                           bg=BG2, fg=WHT, selectcolor=ACC).pack(anchor="w", padx=30)

    def _tab_transcricao(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Transcricao")

        tk.Label(f, text="Transcricao Whisper", font=("Helvetica", 12),
                 bg=BG2, fg=WHT).pack(pady=10)

        self.txt_trans = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=WHT)
        self.txt_trans.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="Iniciar Transcricao", command=self._start_transcription,
                  bg=GRN, fg=WHT).pack(pady=10)

    def _tab_ia(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="IA Externa")

        tk.Label(f, text="Prompt para IA Externa", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_prompt = scrolledtext.ScrolledText(f, height=10, bg=BG3, fg="#a5b4fc")
        self.txt_prompt.pack(fill="x", padx=20, pady=5)

        tk.Button(f, text="Gerar Prompt", command=self._generate_prompt,
                  bg=ACC, fg=WHT).pack(pady=5)

        tk.Label(f, text="Resposta da IA (JSON):", bg=BG2, fg=WHT).pack(pady=5)
        self.txt_resp = scrolledtext.ScrolledText(f, height=10, bg=BG3, fg=GRN)
        self.txt_resp.pack(fill="both", expand=True, padx=20, pady=5)

        tk.Button(f, text="Importar Cortes da IA", command=self._importar_ia,
                  bg=YEL, fg=WHT).pack(pady=5)

    def _tab_cortes(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Cortes")

        tk.Label(f, text="Cortes Sugeridos (18-35s)", bg=BG2, fg=WHT).pack(pady=10)

        self.lst_cuts = tk.Listbox(f, bg=BG3, fg=WHT, height=15)
        self.lst_cuts.pack(fill="both", expand=True, padx=20, pady=10)

        frm = tk.Frame(f, bg=BG2)
        frm.pack()
        tk.Button(frm, text="Aprovar", command=self._aprovar_corte,
                  bg=GRN, fg=WHT).pack(side="left", padx=20, pady=10)
        tk.Button(frm, text="Rejeitar", command=self._rejeitar_corte,
                  bg=RED, fg=WHT).pack(side="right", padx=20, pady=10)

    def _tab_render(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Render")

        tk.Label(f, text="Log do Render", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_log = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=GRN)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="Iniciar Render", command=self._start_render,
                  bg=ACC, fg=WHT).pack(pady=10)

    def _tab_historico(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Historico")

        tk.Label(f, text="Projetos Anteriores", bg=BG2, fg=WHT).pack(pady=10)

        self.tree = ttk.Treeview(f, columns=("ID", "Nome", "Status", "Data"), show="headings")
        self.tree.heading("ID",     text="ID")
        self.tree.heading("Nome",   text="Nome")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Data",   text="Data")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="Atualizar", command=self._carregar_historico,
                  bg=ACC, fg=WHT).pack(pady=5)

    def _tab_agenda(self):
        f = tk.Frame(self.nb, bg=BG2)
        self.nb.add(f, text="Agenda")

        tk.Label(f, text="Agenda de Postagem", bg=BG2, fg=WHT).pack(pady=10)

        self.txt_agenda = scrolledtext.ScrolledText(f, height=20, bg=BG3, fg=GRN)
        self.txt_agenda.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(f, text="Gerar Agenda", bg=ACC, fg=WHT,
                  command=self._gerar_agenda).pack(pady=10)

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _select_video(self):
        p = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.mkv *.mov *.avi")])
        if p:
            self.video_path = p
            self.lbl_video.config(text=os.path.basename(p), fg=GRN)

    def _criar_projeto(self):
        if not self.video_path:
            messagebox.showwarning("Aviso", "Selecione um video primeiro.")
            return
        nome = self.project_name.get().strip() or "Projeto"
        self.project_id = db.create_project(nome, self.video_path)
        self.lbl_projeto.config(text=f"Projeto #{self.project_id} criado", fg=GRN)

    def _start_transcription(self):
        if not self.project_id:
            messagebox.showwarning("Aviso", "Crie um projeto primeiro.")
            return
        self.txt_trans.insert("end", "Iniciando transcricao...\n")
        threading.Thread(target=self._transcribe_worker, daemon=True).start()

    def _transcribe_worker(self):
        try:
            from core.transcriber import WhisperTranscriber
            t      = WhisperTranscriber(model="tiny", language="pt")
            result = t.transcribe(self.video_path,
                                  progress_callback=lambda m: self._log_trans(m))
            tid = db.save_transcript(self.project_id,
                                     result["full_text"], result["segments"])
            self.transcript = {"id": tid, "segments": result["segments"]}

            # gera candidatos automaticamente
            generate_candidates(self.project_id, tid, result["segments"], db)
            self.candidates = db.get_candidates(self.project_id)

            self.root.after(0, self._popular_lista_cortes)
            self._log_trans(f"Pronto — {len(self.candidates)} candidatos gerados.")
        except Exception as e:
            self._log_trans(f"Erro: {e}")

    def _log_trans(self, msg):
        self.root.after(0, lambda: self.txt_trans.insert("end", msg + "\n"))

    def _generate_prompt(self):
        if not self.transcript:
            messagebox.showwarning("Aviso", "Transcreva o video primeiro.")
            return
        from core.prompt_builder import build_prompt
        try:
            texto = " ".join(s["text"] for s in self.transcript["segments"])
            prompt = build_prompt(texto, self.project_name.get())
        except Exception:
            prompt = f'Analise o video "{self.project_name.get()}".\nGere cortes virais de 18-35s.\nRetorne JSON: [{{"start":0,"end":30,"title":"...","hook":"...","score":8.5}}]'
        self.txt_prompt.delete("1.0", "end")
        self.txt_prompt.insert("1.0", prompt)

    def _importar_ia(self):
        raw = self.txt_resp.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Aviso", "Cole a resposta da IA antes.")
            return
        cortes = parse_ai_response(raw)
        if not cortes:
            messagebox.showerror("Erro", "JSON invalido ou fora do formato esperado.")
            return
        validos = [c for c in cortes if validate_ai_cut(c)]
        self.txt_log.insert("end", f"{len(validos)} cortes importados da IA.\n")
        for c in validos:
            self.lst_cuts.insert("end",
                f"[IA] {c.get('title','?')}  {c.get('start',0):.0f}s-{c.get('end',0):.0f}s  score={c.get('score','?')}")

    def _popular_lista_cortes(self):
        self.lst_cuts.delete(0, "end")
        for c in self.candidates:
            self.lst_cuts.insert("end",
                f"#{c['id']}  {c['start_time']:.0f}s-{c['end_time']:.0f}s  score={c.get('combined_score') or '-'}")

    def _aprovar_corte(self):
        sel = self.lst_cuts.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self.candidates):
            cid = self.candidates[idx]["id"]
            db.update_candidate_status(cid, "approved")
            self.lst_cuts.itemconfig(idx, fg=GRN)

    def _rejeitar_corte(self):
        sel = self.lst_cuts.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self.candidates):
            cid = self.candidates[idx]["id"]
            db.update_candidate_status(cid, "rejected")
            self.lst_cuts.itemconfig(idx, fg=RED)

    def _start_render(self):
        if not self.project_id:
            messagebox.showwarning("Aviso", "Crie um projeto primeiro.")
            return
        protection = self.protection.get()
        self.txt_log.insert("end", f"Iniciando render — protecao: {protection}\n")
        threading.Thread(target=self._render_worker,
                         args=(protection,), daemon=True).start()

    def _render_worker(self, protection):
        try:
            from core.cut_engine import render_cut
            aprovados = db.get_candidates(self.project_id, status="approved")
            if not aprovados:
                self.root.after(0, lambda: self.txt_log.insert("end", "Nenhum corte aprovado.\n"))
                return
            out_dir = os.path.join(os.path.expanduser("~"), ".clipfusion", "output")
            os.makedirs(out_dir, exist_ok=True)
            trans = db.get_transcript(self.project_id)
            segs  = trans["segments"] if trans else []
            for c in aprovados:
                cut = {"start": c["start_time"], "end": c["end_time"],
                       "title": f"corte_{c['id']}", "cut_index": c["id"]}
                self.root.after(0, lambda t=cut["title"]: self.txt_log.insert("end", f"Renderizando {t}...\n"))
                result = render_cut(db.get_project(self.project_id)["video_path"],
                                    cut, segs, out_dir, str(self.project_id),
                                    ace_level=protection,
                                    progress_cb=lambda m: self.root.after(0,
                                        lambda mm=m: self.txt_log.insert("end", mm + "\n")))
                self.root.after(0, lambda r=result: self.txt_log.insert("end",
                    f"Salvo: {list(r.get('outputs',{}).values())}\n"))
        except Exception as e:
            self.root.after(0, lambda: self.txt_log.insert("end", f"Erro render: {e}\n"))

    def _carregar_historico(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            with db.get_db() as conn:
                rows = conn.execute(
                    "SELECT id, name, status, created_at FROM projects ORDER BY id DESC"
                ).fetchall()
            for r in rows:
                self.tree.insert("", "end", values=(r[0], r[1], r[2], str(r[3])[:16]))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _gerar_agenda(self):
        import random
        from datetime import datetime, timedelta
        self.txt_agenda.delete("1.0", "end")
        horarios = ["07:00", "12:00", "18:00", "21:00"]
        hoje = datetime.now()
        for i in range(7):
            dia = hoje + timedelta(days=i)
            h   = horarios[i % len(horarios)]
            # jitter anti-padrao: +/- alguns minutos
            jitter = random.randint(-5, 5)
            self.txt_agenda.insert("end",
                f"{dia.strftime('%d/%m/%Y')}  {h}  (+{jitter}min)\n")
