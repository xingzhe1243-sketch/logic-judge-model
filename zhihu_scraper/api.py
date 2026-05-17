"""
Core Zhihu API client with rate limiting and error handling.
知乎API核心客户端，含限速和错误处理
"""
import time
import random
import logging
from collections import deque
from datetime import datetime, date
from typing import Optional

import requests

from .config import (
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, DAILY_LIMIT, HEADERS_TEMPLATE,
    MAX_PER_MINUTE, RETRY_BASE_DELAY, RETRY_MAX_DELAY, RETRY_MAX_ATTEMPTS,
    USER_AGENTS, AVOID_PEAK_HOURS, PEAK_START_HOUR, PEAK_END_HOUR, WEEKEND_LIMIT,
    BATCH_SIZE,
)
from .auth import load_cookies, format_cookie_header

logger = logging.getLogger(__name__)


class ZhihuAPI:
    """Zhihu API client with multi-layer rate limiting and anti-crawl measures."""

    def __init__(self):
        self.session = requests.Session()

        # Load cookies / 加载Cookie
        self.cookies = load_cookies()
        if self.cookies:
            self._pick_user_agent()
            self.session.headers.update(HEADERS_TEMPLATE)
            self.session.headers["Cookie"] = format_cookie_header(self.cookies)

        # Rate limit state / 限速状态
        self.last_request_time = 0.0
        self.today_count = 0
        self.today_date = date.today()

        # Per-minute rate tracking / 每分钟请求计数
        self._minute_timestamps: deque = deque(maxlen=MAX_PER_MINUTE)

    def _pick_user_agent(self):
        """Rotate User-Agent on each request to avoid fingerprinting."""
        ua = random.choice(USER_AGENTS)
        self.session.headers["User-Agent"] = ua

    def is_authenticated(self) -> bool:
        return bool(self.cookies)

    def _rate_limit(self):
        """Multi-layer rate limiting: peak avoidance → daily cap → per-minute → random delay."""
        today = date.today()
        if today != self.today_date:
            self.today_count = 0
            self.today_date = today

        # Layer 1: Peak hour avoidance / 高峰时段规避
        if AVOID_PEAK_HOURS:
            current_hour = datetime.now().hour
            if PEAK_START_HOUR <= current_hour < PEAK_END_HOUR:
                wait_minutes = random.randint(30, 60)
                print(f"[RATE] Peak hour ({PEAK_START_HOUR}:00-{PEAK_END_HOUR}:00), sleeping {wait_minutes}min...")
                print(f"[RATE] 高峰时段，暂停 {wait_minutes} 分钟...")
                time.sleep(wait_minutes * 60)
                return

        # Layer 2: Daily cap / 每日上限
        effective_limit = WEEKEND_LIMIT if today.weekday() >= 5 else DAILY_LIMIT
        if self.today_count >= effective_limit:
            print(f"[RATE] Daily limit ({effective_limit}) reached. See you tomorrow!")
            print(f"[RATE] 每日上限 ({effective_limit}) 已达，明天见！")
            raise RuntimeError(
                f"Daily limit ({effective_limit}) reached. "
                f"每日上限已达 ({effective_limit})，明天再试。"
            )

        # Layer 3: Per-minute rate / 每分钟限速
        now = time.time()
        self._minute_timestamps.append(now)
        if len(self._minute_timestamps) >= MAX_PER_MINUTE:
            oldest = self._minute_timestamps[0]
            if now - oldest < 60:
                wait = 60 - (now - oldest)
                print(f"[RATE] Per-minute limit ({MAX_PER_MINUTE}/min), waiting {wait:.0f}s...")
                print(f"[RATE] 每分钟上限，等待 {wait:.0f}秒...")
                time.sleep(wait)

        # Layer 4: Random delay with human-like jitter / 随机延迟 + 人性化抖动
        # Base random delay in the configured range
        base_delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        # Occasionally add longer pauses to simulate reading behavior
        if random.random() < 0.15:  # 15% chance of a "reading pause"
            base_delay += random.uniform(10, 30)
        elapsed = time.time() - self.last_request_time
        if elapsed < base_delay:
            wait = base_delay - elapsed
            time.sleep(wait)

    def _request(self, method: str, url: str, **kwargs) -> Optional[dict]:
        """Rate-limited request with 429 retry and User-Agent rotation."""
        self._pick_user_agent()  # Rotate UA each request
        self._rate_limit()
        self.last_request_time = time.time()
        self.today_count += 1

        last_error = None
        for attempt in range(RETRY_MAX_ATTEMPTS + 1):
            try:
                resp = self.session.request(method, url, timeout=15, **kwargs)
                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 429:
                    # Rate limited — exponential backoff / 被限流 → 指数退避
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY)
                    logger.error(f"429 Too Many Requests (attempt {attempt+1}): {url}")
                    if attempt < RETRY_MAX_ATTEMPTS:
                        print(f"[WARN] 触发了知 限流！等待 {delay}s 后重试 ({attempt+1}/{RETRY_MAX_ATTEMPTS})...")
                        time.sleep(delay)
                        last_error = e
                        continue
                    print("[ERROR] 多次重试仍然被限流，建议暂停一段时间。")
                    return None

                if status == 403:
                    logger.error(f"403 Forbidden: {url}")
                    print("[ERROR] Cookie expired! Re-run with --login to renew.")
                    print("[ERROR] Cookie已过期！请重新运行 --login 更新。")
                    return None
                if status == 401:
                    logger.error(f"401 Unauthorized: {url}")
                    print("[ERROR] Not logged in. Run --login first.")
                    return None

                logger.error(f"HTTP {status}: {url}")
                return None

            except requests.exceptions.ConnectionError:
                logger.error(f"Connection failed: {url}")
                print("[ERROR] Network error. Check your internet connection.")
                print("[ERROR] 网络错误。请检查网络连接。")
                return None

            except requests.exceptions.Timeout:
                logger.error(f"Timeout: {url}")
                print("[WARN] Request timed out. Retrying...")
                last_error = e if 'e' in locals() else None
                continue

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None

        return None

    def search(self, query: str, offset: int = 0) -> Optional[dict]:
        """Search Zhihu for a topic."""
        url = "https://www.zhihu.com/api/v4/search_v3"
        params = {
            "t": "general",
            "q": query,
            "correction": 1,
            "offset": offset,
            "limit": BATCH_SIZE,
        }
        return self._request("GET", url, params=params)

    def get_question(self, question_id: str) -> Optional[dict]:
        url = f"https://www.zhihu.com/api/v4/questions/{question_id}"
        return self._request("GET", url)

    def get_answers(self, question_id: str, offset: int = 0, limit: int = 15) -> Optional[dict]:
        url = f"https://www.zhihu.com/api/v4/questions/{question_id}/answers"
        params = {
            "include": (
                "data[*].content,"
                "voteup_count,"
                "comment_count,"
                "created_time,"
                "updated_time,"
                "author.name,"
                "author.follower_count,"
                "author.headline"
            ),
            "limit": limit,
            "offset": offset,
        }
        return self._request("GET", url, params=params)

    def get_answer_detail(self, answer_id: str) -> Optional[dict]:
        url = f"https://www.zhihu.com/api/v4/answers/{answer_id}"
        params = {
            "include": (
                "data[*].content,"
                "question.title,question.url,question.id,"
                "voteup_count,comment_count,author.name"
            ),
        }
        return self._request("GET", url, params=params)

    def get_article(self, article_id: str) -> Optional[dict]:
        url = f"https://zhuanlan.zhihu.com/api/posts/{article_id}"
        return self._request("GET", url)

    def get_hot_topics(self) -> Optional[dict]:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        params = {"limit": 50}
        return self._request("GET", url, params=params)
