#!/usr/bin/env python3
"""
Banco SQLite do ClipFusionV3.
Compatível com a GUI atual.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "output"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "clipfusion_v3.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        video_path TEXT NOT NULL,
        status TEXT DEFAULT 'created',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        full_text TEXT,
        segments_json TEXT,
        quality REAL DEFAULT 0.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL NOT NULL,
        title TEXT,
        hook TEXT,
        reason TEXT,
        raw_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cuts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        candidate_id INTEGER,
        output_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_project(name: str, video_path: str) -> int:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO projects (name, video_path, status) VALUES (?, ?, ?)",
        (name, video_path, "created"),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def list_projects() -> List[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_project_status(project_id: int, status: str) -> None:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE projects SET status = ? WHERE id = ?",
        (status, project_id),
    )
    conn.commit()
    conn.close()


def save_transcription(project_id: int, full_text: str, segments: List[Dict[str, Any]], quality: float) -> int:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transcripts (project_id, full_text, segments_json, quality) VALUES (?, ?, ?, ?)",
        (project_id, full_text, json.dumps(segments, ensure_ascii=False), quality),
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def get_transcription(project_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM transcripts WHERE project_id = ? ORDER BY id DESC LIMIT 1",
        (project_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["segments"] = json.loads(data["segments_json"]) if data.get("segments_json") else []
    return data


def save_cuts(project_id: int, cuts: List[Dict[str, Any]]) -> None:
    init_db()
    conn = _conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM candidates WHERE project_id = ?", (project_id,))

    for cut in cuts:
        cur.execute(
            """
            INSERT INTO candidates (
                project_id, start_time, end_time, title, hook, reason, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                float(cut.get("start", 0.0)),
                float(cut.get("end", 0.0)),
                cut.get("title", "Corte"),
                cut.get("hook", ""),
                cut.get("reason", ""),
                json.dumps(cut, ensure_ascii=False),
            ),
        )

    conn.commit()
    conn.close()


def get_candidates(project_id: int) -> List[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM candidates WHERE project_id = ? ORDER BY id ASC",
        (project_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_cut_output(candidate_id: int, output_paths: Any) -> None:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cuts (project_id, candidate_id, output_json) VALUES ((SELECT project_id FROM candidates WHERE id = ?), ?, ?)",
        (candidate_id, candidate_id, json.dumps(output_paths, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def get_cuts(project_id: int) -> List[Dict[str, Any]]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM cuts WHERE project_id = ? ORDER BY id DESC",
        (project_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


init_db()
