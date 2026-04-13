"""
ClipFusion Database v3.0 - Schema Unificado
Resolve: Incompatibilidade entre viral_analyzer e prompt_builder
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

DB_PATH = Path(os.path.expanduser("~")) / ".clipfusion" / "clipfusion_v3.db"

def _get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    conn = _get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Inicializa banco com schema unificado (corrigido)."""
    with get_db() as conn:
        conn.executescript("""
            -- Projetos
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                language TEXT DEFAULT 'pt',
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Transcrições
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                full_text TEXT,
                segments_json TEXT,
                quality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            -- Candidatos (CORE DO SISTEMA - Schema Unificado)
            -- CORREÇÃO: Campos mapeados corretamente
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                transcript_id INTEGER NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                text TEXT NOT NULL,

                -- Scores da Regra de Ouro (mapeados corretamente)
                hook_strength REAL,           -- Antigo 'viral_score' / Gatilhos emocionais
                retention_score REAL,         -- Mapeia 'retencao_estimada' / Retenção projetada
                moment_strength REAL,         -- Mapeia 'comentabilidade' / Força do momento
                shareability REAL,            -- Potencial de compartilhamento

                -- Fit por plataforma
                platform_fit_tiktok REAL,
                platform_fit_reels REAL,
                platform_fit_shorts REAL,

                -- Score final
                combined_score REAL,          -- Resultado da Regra de Ouro

                -- Metadados
                status TEXT DEFAULT 'pending',
                duration_seconds REAL,
                word_count INTEGER,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (transcript_id) REFERENCES transcripts(id) ON DELETE CASCADE
            );

            -- Cortes aprovados
            CREATE TABLE IF NOT EXISTS cuts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                candidate_id INTEGER UNIQUE,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                title TEXT,
                hook TEXT,
                archetype TEXT,
                platforms TEXT,              -- JSON array
                protection_level TEXT DEFAULT 'none',
                output_paths TEXT,           -- JSON dict
                viral_score REAL,
                decision TEXT,               -- 'approved', 'rework', 'discarded'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE SET NULL
            );

            -- Performance real (para learning)
            CREATE TABLE IF NOT EXISTS performances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cut_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                posted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cut_id) REFERENCES cuts(id) ON DELETE CASCADE
            );

            -- Pesos de aprendizado
            CREATE TABLE IF NOT EXISTS learning_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                subkey TEXT,
                weight REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Índices para performance
            CREATE INDEX IF NOT EXISTS idx_candidates_project ON candidates(project_id);
            CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(combined_score DESC);
            CREATE INDEX IF NOT EXISTS idx_cuts_project ON cuts(project_id);
        """)
        conn.commit()

# Helpers JSON
def segments_to_json(segments):
    return json.dumps(segments, ensure_ascii=False)

def json_to_segments(json_str):
    return json.loads(json_str) if json_str else []

def platforms_to_json(platforms):
    return json.dumps(platforms)

def json_to_platforms(json_str):
    return json.loads(json_str) if json_str else []

# Operações CRUD

def create_project(name, video_path, language='pt'):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO projects (name, video_path, language) VALUES (?, ?, ?)",
            (name, video_path, language)
        )
        conn.commit()
        return cur.lastrowid

def get_project(project_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None

def save_transcript(project_id, full_text, segments, quality_score=None):
    segments_json = segments_to_json(segments)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO transcripts (project_id, full_text, segments_json, quality_score) VALUES (?, ?, ?, ?)",
            (project_id, full_text, segments_json, quality_score)
        )
        conn.commit()
        return cur.lastrowid

def get_transcript(project_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM transcripts WHERE project_id = ? ORDER BY id DESC LIMIT 1",
            (project_id,)
        ).fetchone()
        if row:
            d = dict(row)
            d['segments'] = json_to_segments(d['segments_json'])
            return d
        return None

def save_candidate(project_id, transcript_id, start, end, text, scores=None, duration=None, word_count=None):
    """
    Salva candidato com scores da Regra de Ouro.
    CORREÇÃO: Mapeia corretamente os campos.
    """
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO candidates
            (project_id, transcript_id, start_time, end_time, text,
             hook_strength, retention_score, moment_strength, shareability,
             platform_fit_tiktok, platform_fit_reels, platform_fit_shorts, 
             combined_score, duration_seconds, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, transcript_id, start, end, text,
            scores.get('hook') if scores else None,
            scores.get('retention') if scores else None,
            scores.get('moment') if scores else None,
            scores.get('shareability') if scores else None,
            scores.get('platform_fit_tiktok') if scores else None,
            scores.get('platform_fit_reels') if scores else None,
            scores.get('platform_fit_shorts') if scores else None,
            scores.get('combined') if scores else None,
            duration,
            word_count
        ))
        conn.commit()
        return cur.lastrowid

def get_candidates(project_id, status=None, min_score=0.0):
    """Recupera candidatos ordenados por score."""
    with get_db() as conn:
        if status:
            rows = conn.execute(
                """SELECT * FROM candidates 
                   WHERE project_id = ? AND status = ? AND combined_score >= ?
                   ORDER BY combined_score DESC""",
                (project_id, status, min_score)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM candidates 
                   WHERE project_id = ? AND combined_score >= ?
                   ORDER BY combined_score DESC""",
                (project_id, min_score)
            ).fetchall()
        return [dict(r) for r in rows]

def update_candidate_status(candidate_id, status):
    with get_db() as conn:
        conn.execute("UPDATE candidates SET status = ? WHERE id = ?", (status, candidate_id))
        conn.commit()

def save_cut(project_id, candidate_id, start, end, title, hook, archetype, 
             platforms, protection_level, output_paths, viral_score, decision):
    platforms_json = platforms_to_json(platforms)
    output_paths_json = json.dumps(output_paths)

    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO cuts
            (project_id, candidate_id, start_time, end_time, title, hook, archetype,
             platforms, protection_level, output_paths, viral_score, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, candidate_id, start, end, title, hook, archetype,
            platforms_json, protection_level, output_paths_json, viral_score, decision
        ))
        conn.commit()
        return cur.lastrowid

def save_performance(cut_id, platform, views=0, likes=0, shares=0, comments=0, posted_at=None):
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO performances
            (cut_id, platform, views, likes, shares, comments, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cut_id, platform, views, likes, shares, comments, posted_at))
        conn.commit()
        return cur.lastrowid

# Inicializa ao importar
init_db()
