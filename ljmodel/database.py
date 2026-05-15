"""SQLite 持久化 — 分析结果存储与查询"""

import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".logic_judge.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """自动建表（幂等）"""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                text        TEXT    NOT NULL,
                score       INTEGER DEFAULT 0,
                modules     TEXT    DEFAULT '',
                result      TEXT    DEFAULT '{}',
                created_at  TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)


def save_analysis(text: str, score: int, modules: list[str], result: dict) -> int:
    """保存一条分析记录，返回 id"""
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (text, score, modules, result) VALUES (?, ?, ?, ?)",
            (text, score, json.dumps(modules, ensure_ascii=False),
             json.dumps(result, ensure_ascii=False))
        )
        return cur.lastrowid


def list_analyses(limit: int = 20, offset: int = 0) -> list[dict]:
    """列出最近的分析记录"""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, score, modules, created_at FROM analyses ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [dict(r) for r in rows]


def get_analysis(analysis_id: int) -> dict | None:
    """获取单条完整记录"""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["modules"] = json.loads(d["modules"]) if d["modules"] else []
        d["result"] = json.loads(d["result"]) if d["result"] else {}
        return d


def search_analyses(q: str, limit: int = 20) -> list[dict]:
    """按关键词搜索分析文本"""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, score, modules, created_at FROM analyses WHERE text LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{q}%", limit)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_analysis(analysis_id: int) -> bool:
    """删除一条记录，返回是否删除成功"""
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        return cur.rowcount > 0


def clear_history() -> int:
    """清空所有记录，返回删除条数"""
    with _get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        conn.execute("DELETE FROM analyses")
        return count


# 模块导入时自动建表
init_db()
