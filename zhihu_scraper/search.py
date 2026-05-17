"""
Search orchestrator: runs all topics, collects questions + answers.
搜索编排器：执行所有搜索主题，收集问题和回答

Why this approach / 为什么用这种方案:
- get_question() returns 403 with basic cookies
- get_question() 在基础Cookie下返回403
- Workaround: extract question data from search results + answer details
- 变通方案：从搜索结果和回答详情中提取问题数据
- get_answers() and get_answer_detail() work fine
- get_answers() 和 get_answer_detail() 正常工作
"""
import re
import logging
from typing import List, Dict, Optional

from .api import ZhihuAPI
from .config import MAX_QUESTIONS_PER_TOPIC, MAX_ANSWERS_PER_QUESTION, BATCH_SIZE

logger = logging.getLogger(__name__)


def extract_question_id(url_or_id: str) -> Optional[str]:
    """Extract question ID from URL or return as-is if already numeric.
    从URL中提取问题ID，如果是纯数字则直接返回

    Why / 为什么:
    - Zhihu returns IDs in various formats
    - 知乎以多种格式返回ID
    - Some are pure strings like "486546847", some are embedded in URLs
    - 有些是纯数字字符串，有些嵌入在URL中
    """
    if not url_or_id:
        return None
    # If already pure digits / 如果已经是纯数字
    if url_or_id.strip().isdigit():
        return url_or_id.strip()
    # Extract from URL / 从URL中提取
    match = re.search(r"/question/(\d+)", url_or_id)
    return match.group(1) if match else None


def search_and_collect(api: ZhihuAPI, topics: List[str]) -> List[Dict]:
    """Main search: run all topics, collect questions + answers.
    主搜索：执行所有主题，收集问题和回答

    Now saves incrementally after each topic — if daily limit is hit,
    partial data is preserved.
    现在每完成一个主题就增量保存 — 即使达到日限额，已完成数据不丢失。
    """
    from .storage import save_results

    all_results = []
    seen_ids = _load_existing_ids()  # 加载已有数据避免重复

    for topic_idx, topic in enumerate(topics, 1):
        print(f"\n[{topic_idx}/{len(topics)}] Searching: {topic}")

        try:
            items = _search_all_items(api, topic)
        except RuntimeError as e:
            if "Daily limit" in str(e):
                print(f"  -> {e}")
            raise

        if not items:
            print(f"  -> No results for: {topic}")
            # Save empty progress so we know this topic was attempted
            continue

        print(f"  -> Found {len(items)} result items")
        topic_results = []

        for item in items:
            qid = item.get("question_id")
            if not qid or qid in seen_ids:
                continue
            seen_ids.add(qid)

            try:
                result = _collect_answers(api, qid, item)
            except RuntimeError as e:
                if "Daily limit" in str(e):
                    print(f"  -> {e}")
                    # Save what we have so far before quitting
                    if topic_results:
                        save_results(topic_results, topic="incremental")
                    return all_results
                raise

            if result:
                topic_results.append(result)
                all_results.append(result)

        # Save incremental: per topic
        if topic_results:
            try:
                save_results(topic_results, topic="incremental")
                print(f"  [SAVED] {len(topic_results)} questions from topic {topic_idx}")
            except Exception as e:
                print(f"  [WARN] Save failed: {e}")

    print(f"\n{'='*50}")
    print(f"Done! Collected {len(all_results)} questions total.")
    print(f"完成！共收集 {len(all_results)} 个问题。")
    return all_results


def _load_existing_ids() -> set:
    """Load already-scraped question IDs from SQLite to skip duplicates.
    从SQLite加载已有问题ID，避免重复爬取"""
    from pathlib import Path
    from .config import DATA_DIR
    db_path = DATA_DIR / "zhihu_knowledge.db"
    if not db_path.exists():
        return set()
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        ids = {str(r[0]) for r in conn.execute("SELECT question_id FROM questions").fetchall()}
        conn.close()
        return ids
    except sqlite3.Error:
        return set()


def _search_all_items(api: ZhihuAPI, topic: str) -> List[Dict]:
    """Search a topic and return normalized items with question_id + metadata.
    搜索主题并返回规范化结果项（含question_id和元数据）

    Returns / 返回:
    [
        {
            "question_id": "123456",
            "title": "...",
            "detail": "...",
            "answer_count": 99,
            "follower_count": 42,
            "type": "question" or "answer",
        },
        ...
    ]
    """
    items = []
    offset = 0

    while len(items) < MAX_QUESTIONS_PER_TOPIC:
        data = api.search(topic, offset=offset)
        if not data or "data" not in data:
            break

        for raw_item in data["data"]:
            obj = raw_item.get("object", {})
            if not obj:
                continue

            obj_type = obj.get("type", "")
            normalized = None

            if obj_type == "question":
                # Direct question result / 直接的问题结果
                # Extract all data from search result (avoids get_question 403)
                # 从搜索结果中提取所有数据（绕过get_question的403错误）
                q_url = obj.get("url", "")
                qid = extract_question_id(q_url) or obj.get("id", "")
                if qid:
                    normalized = {
                        "question_id": str(qid),
                        "title": obj.get("title", ""),
                        "detail": obj.get("detail", ""),
                        "answer_count": obj.get("answer_count", 0),
                        "follower_count": obj.get("follower_count", 0),
                        "type": "question",
                    }

            elif obj_type == "answer":
                # Answer result: use get_answer_detail to get question info
                # 回答结果：使用get_answer_detail获取问题信息
                answer_id = obj.get("id", "")
                if answer_id:
                    detail = api.get_answer_detail(str(answer_id))
                    if detail:
                        q_info = detail.get("question", {})
                        qid = q_info.get("id", "") or extract_question_id(q_info.get("url", ""))
                        if qid:
                            normalized = {
                                "question_id": str(qid),
                                "title": q_info.get("title", obj.get("question_title", "")),
                                "detail": "",
                                "answer_count": 0,
                                "follower_count": 0,
                                "type": "answer",
                            }

            if normalized and normalized["question_id"] not in [it["question_id"] for it in items]:
                items.append(normalized)
                if len(items) >= MAX_QUESTIONS_PER_TOPIC:
                    break

        # Pagination / 分页
        page = data.get("paging", {})
        if page.get("is_end", True):
            break
        offset += BATCH_SIZE

    return items


def _collect_answers(api: ZhihuAPI, question_id: str, question_info: Dict) -> Optional[Dict]:
    """Collect answers for a given question.
    收集指定问题的回答

    Why separate function / 为什么独立成函数:
    - We need to show progress per question
    - 每个问题需要显示进度
    - Error handling per question (one failing shouldn't stop all)
    - 单个问题失败不应影响其他问题
    """
    answers = []
    offset = 0
    api_calls = 0

    print(f"    Fetching answers for question {question_id[:10]}...", end="")
    while len(answers) < MAX_ANSWERS_PER_QUESTION:
        a_data = api.get_answers(question_id, offset=offset, limit=BATCH_SIZE)
        api_calls += 1
        if not a_data or "data" not in a_data:
            break

        for item in a_data["data"]:
            answers.append({
                "answer_id": item.get("id"),
                "author": item.get("author", {}).get("name", "匿名"),
                "author_followers": item.get("author", {}).get("follower_count", 0),
                "content": item.get("content", ""),
                "voteup_count": item.get("voteup_count", 0),
                "comment_count": item.get("comment_count", 0),
                "created_time": item.get("created_time", 0),
                "updated_time": item.get("updated_time", 0),
            })
            if len(answers) >= MAX_ANSWERS_PER_QUESTION:
                break

        page = a_data.get("paging", {})
        if page.get("is_end", True):
            break
        offset += BATCH_SIZE

    print(f" {len(answers)} answers ({api_calls} API calls)")

    if not answers:
        return None

    return {
        "question_id": question_id,
        "title": question_info.get("title", ""),
        "detail": question_info.get("detail", ""),
        "answer_count": question_info.get("answer_count", 0),
        "follower_count": question_info.get("follower_count", 0),
        "answers": answers,
        "source": "zhihu",
    }
