"""
Data storage: saves scraped data to JSON and SQLite.
数据存储：将爬取数据保存为JSON和SQLite

Why SQLite / 为什么用SQLite:
- No server needed, single file database
- 无需服务器，单文件数据库
- Supports deduplication (UNIQUE constraint on URLs)
- 支持去重（URL上的UNIQUE约束）
- Easy to query: "all answers with >1000 votes"
- 方便查询："所有赞同数>1000的回答"
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from .config import DATA_DIR, SAVE_JSON, SAVE_SQLITE
from .extractor import clean_html, trim_to_length


def ensure_data_dir():
    """Create data directory if it doesn't exist.
    确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_results(results: List[Dict], topic: str = "social_hidden_rules"):
    """Save all scraped results to files.
    将所有爬取结果保存到文件

    Why two formats / 为什么两种格式:
    - JSON: Easy to read, copy, feed to LLM instantly
    - JSON：方便人类阅读、复制、直接喂给LLM
    - SQLite: Data analysis, dedup, future growth
    - SQLite：数据分析、去重、未来扩展
    """
    ensure_data_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []

    if SAVE_JSON:
        json_path = DATA_DIR / f"zhihu_{topic}_{timestamp}.json"
        json_path.write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        saved_files.append(str(json_path))
        print(f"[OK] JSON saved: {json_path}")

    if SAVE_SQLITE:
        db_path = _save_to_sqlite(results)
        saved_files.append(str(db_path))

    return saved_files


def _save_to_sqlite(results: List[Dict]) -> Path:
    """Save results to SQLite database with dedup.
    将结果保存到SQLite数据库（带过去重）"""
    db_path = DATA_DIR / "zhihu_knowledge.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create tables / 建表
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            detail TEXT,
            answer_count INTEGER DEFAULT 0,
            follower_count INTEGER DEFAULT 0,
            source TEXT DEFAULT 'zhihu',
            scraped_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer_id TEXT UNIQUE NOT NULL,
            question_id TEXT NOT NULL,
            author TEXT,
            author_followers INTEGER DEFAULT 0,
            content TEXT,
            content_clean TEXT,
            voteup_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            created_time INTEGER,
            scraped_at TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(question_id)
        );
    """)

    scraped_at = datetime.now().isoformat()

    for q in results:
        # Insert question / 插入问题
        try:
            cursor.execute(
                """INSERT OR IGNORE INTO questions
                   (question_id, title, detail, answer_count, follower_count, source, scraped_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    q["question_id"], q["title"], q["detail"],
                    q["answer_count"], q["follower_count"],
                    q["source"], scraped_at
                )
            )
        except sqlite3.Error as e:
            print(f"[WARN] DB error on question {q['question_id']}: {e}")

        # Insert answers / 插入回答
        for a in q.get("answers", []):
            try:
                cleaned = clean_html(a.get("content", ""))
                cleaned = trim_to_length(cleaned, 8000)

                cursor.execute(
                    """INSERT OR IGNORE INTO answers
                       (answer_id, question_id, author, author_followers,
                        content, content_clean, voteup_count, comment_count,
                        created_time, scraped_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        str(a["answer_id"]), q["question_id"],
                        a["author"], a["author_followers"],
                        a["content"], cleaned,
                        a["voteup_count"], a["comment_count"],
                        a["created_time"], scraped_at
                    )
                )
            except sqlite3.Error as e:
                print(f"[WARN] DB error on answer {a.get('answer_id')}: {e}")

    conn.commit()
    conn.close()

    print(f"[OK] SQLite saved: {db_path}")
    return db_path


def export_for_llm(json_path: str = None, output_path: str = None) -> str:
    """Export cleaned text for LLM training/knowledge base.
    导出已清洗文本供LLM训练/知识库使用

    Why / 为什么:
    - Creates a single merged text file with all cleaned content
    - 创建包含所有清洗后内容的单一合并文本文件
    - Ready to be fed into LLM prompt or fine-tuning pipeline
    - 准备好直接输入LLM提示词或微调流程
    """
    if json_path:
        path = Path(json_path)
    else:
        # Use most recent JSON file / 使用最近的JSON文件
        json_files = sorted(DATA_DIR.glob("zhihu_*.json"))
        if not json_files:
            print("[ERROR] No JSON files found.")
            return None
        path = json_files[-1]

    if not output_path:
        output_path = str(path.with_name(path.stem + "_for_llm.txt"))

    data = json.loads(path.read_text(encoding="utf-8"))
    lines = []

    for q in data:
        lines.append(f"# 问题: {q['title']}")
        lines.append("")
        for a in q.get("answers", []):
            cleaned = clean_html(a.get("content", ""))
            lines.append(f"## 回答者: {a['author']} (赞同: {a['voteup_count']})")
            lines.append("")
            lines.append(cleaned)
            lines.append("")
            lines.append("---")
            lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] LLM export saved: {output_path}")
    return output_path
