"""处理知乎数据：按智囊团5大领域分类、提取精华洞见、生成结构化知识库"""

import sqlite3
import json
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "zhihu_knowledge.db"
OUTPUT_DIR = DATA_DIR

# 领域分类关键词
DOMAIN_KEYWORDS = {
    "社会与权力": [
        "社会", "规则", "权力", "阶层", "人性", "真相", "潜规则",
        "世界", "运作", "底层", "阴暗", "阶级", "跨越", "现实",
        "规则", "草台班子", "老实人", "残酷",
    ],
    "经济与职场": [
        "赚钱", "财富", "职场", "晋升", "打工", "经济", "资本",
        "剥削", "中产", "资产", "负债", "工资", "收入", "创业",
        "老板", "打工人", "贫穷", "富贵",
    ],
    "认知与心理": [
        "认知", "心理", "变强", "自律", "本质", "聪明", "焦虑",
        "思考", "深度", "改变", "习惯", "成长", "学习", "思维",
        "性格", "单纯", "成熟",
    ],
    "人际关系": [
        "人际", "社交", "识人", "情商", "说话", "亲密", "关系",
        "沟通", "相处", "朋友", "好人缘", "价值观", "信任", "交往",
        "潜规则", "说话", "饭局",
    ],
    "策略与决策": [
        "选择", "决定", "长期主义", "风险", "博弈", "护城河",
        "决策", "战略", "规划", "失败", "机会", "判断", "权衡",
        "信息", "认知",
    ],
}

def classify_domain(title: str, content: str = "") -> list[str]:
    """分类文本所属的智囊团领域"""
    text = (title + " " + content).lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[domain] = score
    sorted_domains = sorted(scores.keys(), key=lambda d: -scores[d])
    return sorted_domains if sorted_domains else ["未分类"]


def extract_insight(content: str, max_len: int = 300) -> str:
    """从回答内容中提取最有价值的一段"""
    if not content:
        return ""
    # 去掉HTML标签
    clean = re.sub(r'<[^>]+>', '', content)
    # 去掉空行
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    if not lines:
        return clean[:max_len]
    # 优先找带数字、引号、有实质内容的句子
    valuable = [l for l in lines if len(l) > 20 and not l.startswith(('http', '图片', '图'))]
    if valuable:
        # 取最长的有内容的段落
        best = max(valuable, key=len)
        return best[:max_len]
    return lines[0][:max_len]


def process():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # 加载所有回答（按赞同数排序）
    answers = conn.execute("""
        SELECT a.*, q.title as question_title
        FROM answers a
        JOIN questions q ON a.question_id = q.question_id
        ORDER BY a.voteup_count DESC
    """).fetchall()

    # 按领域分类
    domain_data = defaultdict(lambda: {
        "questions": set(),
        "answers": [],
        "total_votes": 0,
        "top_answers": [],
    })

    for a in answers:
        content = a["content_clean"] or a["content"] or ""
        title = a["question_title"] or ""
        domains = classify_domain(title, content)
        entry = {
            "question": title,
            "author": a["author"],
            "votes": a["voteup_count"],
            "comments": a["comment_count"],
            "insight": extract_insight(content),
            "full_length": len(content),
        }
        for d in domains:
            domain_data[d]["questions"].add(title)
            domain_data[d]["answers"].append(entry)
            domain_data[d]["total_votes"] += a["voteup_count"]
            if len(domain_data[d]["top_answers"]) < 20:
                domain_data[d]["top_answers"].append(entry)

    # 生成结构化输出
    total_questions = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    total_answers = conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
    total_votes = conn.execute("SELECT SUM(voteup_count) FROM answers").fetchone()[0]
    conn.close()

    output = {
        "数据概览": {
            "总问题数": total_questions,
            "总回答数": total_answers,
            "总赞同数": total_votes,
        },
        "领域分布": {},
    }

    for domain, data in sorted(domain_data.items()):
        # 去重问题列表
        unique_questions = list(data["questions"])
        output["领域分布"][domain] = {
            "相关问题数": len(unique_questions),
            "相关回答数": len(data["answers"]),
            "总赞同数": data["total_votes"],
            "代表性问题": unique_questions[:10],
            "精华洞见（高赞回答摘要）": [
                {
                    "问题": a["question"][:80],
                    "作者": a["author"],
                    "赞同": a["votes"],
                    "洞见": a["insight"],
                }
                for a in data["top_answers"][:10]
            ],
        }

    # 智囊团知识库报告
    report_lines = ["# 知乎智囊团 · 知识库报告\n"]
    report_lines.append(f"> 数据来源: 知乎爬虫 | 问题数: {output['数据概览']['总问题数']} | 回答数: {output['数据概览']['总回答数']} | 总赞同: {output['数据概览']['总赞同数']:,}\n")

    for domain, info in output["领域分布"].items():
        report_lines.append(f"---\n## {domain}\n")
        report_lines.append(f"- 相关问题: {info['相关问题数']}个 | 相关回答: {info['相关回答数']}个 | 总赞同: {info['总赞同数']:,}\n")
        report_lines.append("### 代表性问题\n")
        for q in info["代表性问题"]:
            report_lines.append(f"- {q[:60]}")
        report_lines.append("\n### 精华洞见\n")
        for a in info["精华洞见（高赞回答摘要）"]:
            report_lines.append(f"**{a['问题']}** — {a['作者']}（赞同:{a['赞同']}）")
            report_lines.append(f"> {a['洞见']}\n")

    # 跨领域交叉洞见 — 最高赞精华TOP30
    report_lines.append("---\n## 跨领域 · 最高赞精华 TOP 30\n")
    all_sorted = sorted(
        [a for domain_info in domain_data.values() for a in domain_info["top_answers"]],
        key=lambda x: -x["votes"]
    )
    # 去重
    seen = set()
    unique_top = []
    for a in all_sorted:
        key = a["question"] + a["author"]
        if key not in seen:
            seen.add(key)
            unique_top.append(a)
    for i, a in enumerate(unique_top[:30], 1):
        report_lines.append(f"{i}. [{a['votes']}赞] {a['question'][:60]} — {a['author']}")
        report_lines.append(f"   {a['insight'][:200]}\n")

    # 保存
    output["领域分布"] = {k: {
        "相关问题数": v["相关问题数"],
        "相关回答数": v["相关回答数"],
        "总赞同数": v["总赞同数"],
        "代表性问题": v["代表性问题"],
        "精华洞见": v["精华洞见（高赞回答摘要）"],
    } for k, v in output["领域分布"].items()}

    json_path = OUTPUT_DIR / "zhihu_thinktank_knowledge.json"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] JSON 已保存: {json_path}")

    md_path = OUTPUT_DIR / "zhihu_thinktank_report.md"
    md_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"[OK] 报告已保存: {md_path}")

    return output


if __name__ == "__main__":
    result = process()
    # 打印摘要
    print(f"\n{'='*60}")
    print(f"知乎智囊团 · 数据处理完成")
    print(f"{'='*60}")
    print(f"总数据: {result['数据概览']['总问题数']} 问题, {result['数据概览']['总回答数']} 回答, {result['数据概览']['总赞同数']:,} 赞同")
    print(f"\n领域分布:")
    for domain, info in result["领域分布"].items():
        print(f"  {domain}: {info['相关回答数']} 回答 ({info['总赞同数']:,} 赞同)")
