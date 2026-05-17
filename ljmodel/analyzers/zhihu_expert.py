"""知乎专家 — 从知乎数据中提取真实世界经验和洞见"""

import re
import sqlite3
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "zhihu_knowledge.db"


# 知识域分类关键词 — 用于将知乎内容归类到智囊团5大领域
DOMAIN_KEYWORDS = {
    "社会与权力": [
        "社会", "规则", "权力", "阶层", "人性", "真相", "潜规则",
        "世界", "运作", "底层", "阴暗", "黑暗", "阶级", "跨越",
    ],
    "经济与职场": [
        "赚钱", "财富", "职场", "晋升", "打工", "经济", "资本",
        "剥削", "中产", "资产", "负债", "工资", "收入", "创业",
    ],
    "认知与心理": [
        "认知", "心理", "变强", "自律", "本质", "聪明", "焦虑",
        "思考", "深度", "改变", "习惯", "成长", "学习", "思维",
    ],
    "人际关系": [
        "人际", "社交", "识人", "情商", "说话", "亲密", "关系",
        "沟通", "相处", "朋友", "好人缘", "价值观", "信任",
    ],
    "策略与决策": [
        "选择", "决定", "长期主义", "风险", "博弈", "护城河",
        "决策", "战略", "规划", "失败", "机会", "判断", "权衡",
    ],
}


def _get_db() -> Optional[sqlite3.Connection]:
    """Connect to the Zhihu knowledge database."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """Extract meaningful keywords from input text for matching against Zhihu data."""
    # Remove common stopwords and punctuation
    stopwords = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
        "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
        "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
        "吗", "吧", "呢", "啊", "哦", "嗯", "哈", "呀", "么", "怎么", "什么",
        "为什么", "如何", "哪", "谁", "何时", "多少", "几个",
    }
    # Split into words: for Chinese, extract 2-4 character segments
    # Filter out pure punctuation and stopwords
    words = set()
    for token in re.split(r'[\s,，。．！？、；：""''（）\(\)\[\]【】《》/\\#@\+\.\,\;\:\!\"\'\?\-]+', text):
        token = token.strip()
        if len(token) >= 2 and token not in stopwords:
            words.add(token)
        # Also extract 2-char substrings for shorter keyword matching
        for i in range(len(token) - 1):
            bigram = token[i:i+2]
            if bigram not in stopwords and not re.match(r'^[一-鿿]$', bigram):
                words.add(bigram)

    # Prefer longer keywords first (more specific)
    sorted_words = sorted(words, key=lambda w: (-len(w), w))
    return sorted_words[:max_keywords]


def _search_questions(conn: sqlite3.Connection, keywords: list[str],
                      max_results: int = 5) -> list[dict]:
    """Search for questions matching any of the keywords."""
    results = []
    for keyword in keywords:
        if len(results) >= max_results:
            break
        cursor = conn.execute(
            "SELECT question_id, title, answer_count, follower_count "
            "FROM questions WHERE title LIKE ? LIMIT ?",
            (f"%{keyword}%", max_results - len(results))
        )
        for row in cursor.fetchall():
            qid = row["question_id"]
            if qid not in [r["question_id"] for r in results]:
                results.append({
                    "question_id": qid,
                    "title": row["title"],
                    "answer_count": row["answer_count"],
                    "follower_count": row["follower_count"],
                })
    return results


def _search_answers(conn: sqlite3.Connection, keywords: list[str],
                    min_votes: int = 100, max_answers: int = 10) -> list[dict]:
    """Search for high-voted answers matching keywords."""
    results = []
    for keyword in keywords:
        if len(results) >= max_answers:
            break
        cursor = conn.execute(
            "SELECT a.answer_id, a.author, a.content_clean, a.voteup_count, "
            "       a.comment_count, q.title as question_title "
            "FROM answers a JOIN questions q ON a.question_id = q.question_id "
            "WHERE a.voteup_count >= ? AND a.content_clean LIKE ? "
            "ORDER BY a.voteup_count DESC LIMIT ?",
            (min_votes, f"%{keyword}%", max_answers - len(results))
        )
        for row in cursor.fetchall():
            aid = row["answer_id"]
            if aid not in [r["answer_id"] for r in results]:
                content = row["content_clean"] or ""
                results.append({
                    "answer_id": aid,
                    "author": row["author"],
                    "question_title": row["question_title"],
                    "content": content[:500],
                    "voteup_count": row["voteup_count"],
                    "comment_count": row["comment_count"],
                })
    return results


def _classify_domain(text: str) -> list[dict]:
    """Classify content into think tank domains based on keyword matching."""
    domain_scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            domain_scores[domain] = score
    return sorted(
        [{"domain": d, "relevance": s} for d, s in domain_scores.items()],
        key=lambda x: -x["relevance"]
    )


def _analyze_with_answers(text: str, conn: sqlite3.Connection) -> dict:
    """Main analysis: match input text to Zhihu wisdom."""
    keywords = _extract_keywords(text)
    matching_questions = _search_questions(conn, keywords, max_results=8)
    matching_answers = _search_answers(conn, keywords, min_votes=100, max_answers=15)

    # Classify the input itself into domains
    domains = _classify_domain(text)

    # Extract domain-relevant answers
    domain_insights = {}
    for domain_entry in domains:
        domain = domain_entry["domain"]
        domain_kws = DOMAIN_KEYWORDS[domain]
        relevant = [
            a for a in matching_answers
            if any(kw in (a.get("question_title", "") or "") or
                   kw in (a.get("content", "") or "")
                   for kw in domain_kws)
        ]
        if relevant:
            domain_insights[domain] = [
                {
                    "author": a["author"],
                    "question": a["question_title"],
                    "insight": a["content"][:300],
                    "votes": a["voteup_count"],
                }
                for a in relevant[:5]
            ]

    return {
        "匹配关键词数": len(keywords),
        "关键词": keywords,
        "匹配问题数": len(matching_questions),
        "匹配高赞回答数": len(matching_answers),
        "匹配问题": [
            {
                "title": q["title"],
                "回答数": q["answer_count"],
                "关注数": q["follower_count"],
            }
            for q in matching_questions
        ],
        "高赞回答": [
            {
                "作者": a["author"],
                "问题": a["question_title"],
                "赞同": a["voteup_count"],
                "内容摘要": a["content"][:200],
            }
            for a in matching_answers[:8]
        ],
        "所属智囊团领域": domains,
        "领域洞见": domain_insights,
        "知识来源": "知乎 — 真实世界经验与集体智慧",
    }


def analyze_zhihu_expert(text: str, kb: dict) -> dict:
    """Zhihu Expert analyzer: provides real-world wisdom from Zhihu Q&A data.

    This module functions as a '知乎专家' in the think tank, offering empirical,
    experience-based perspectives from thousands of real-world answers on
    society, economics, psychology, relationships, and strategy.
    """
    result = {
        "状态": "未连接数据库",
        "匹配结果": {},
        "洞见": [],
    }

    conn = _get_db()
    if conn is None:
        result["状态"] = "数据库不存在 — 请先运行爬虫收集知乎数据"
        result["洞见"] = ["提示: 运行 python zhihu_scraper/cli.py --run 收集数据后可使用此模块"]
        return result

    try:
        analysis = _analyze_with_answers(text, conn)
        result["状态"] = f"成功匹配 {analysis['匹配问题数']} 个问题和 {analysis['匹配高赞回答数']} 个回答"
        result["匹配结果"] = analysis

        # Build insights summary
        insights = []
        for a in analysis["高赞回答"][:5]:
            insights.append(
                f"[知乎·{a['作者']}] 关于「{a['问题']}」"
                f"(赞同:{a['赞同']}) — {a['内容摘要'][:150]}"
            )
        for domain, domain_data in analysis.get("领域洞见", {}).items():
            for item in domain_data[:2]:
                insights.append(
                    f"[{domain}·{item['author']}] {item['insight'][:150]}"
                )

        result["洞见"] = insights
        result["领域分布"] = analysis.get("所属智囊团领域", [])
        result["知识来源"] = analysis.get("知识来源", "知乎")

    except Exception as e:
        result["状态"] = f"查询异常: {e}"
        result["洞见"] = []

    finally:
        conn.close()

    return result
