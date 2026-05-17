"""
Configuration for Zhihu scraper.
知乎爬虫配置文件

Why this exists / 为什么存在:
- Centralizes all tunable parameters in one place
- 所有可调参数集中管理，方便修改
- Rate limits protect you from being banned
- 限速保护账号不被封禁
"""
from pathlib import Path

# === Project paths / 项目路径 ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # LogicJudgeModel/
DATA_DIR = PROJECT_ROOT / "data"  # All scraped data goes here / 爬取数据存放目录

# === Rate limiting / 请求限速 ===
# Why conservative delays / 为什么保守:
# - Random 8-12s = ~360 requests/day max if running 24h
# - 随机8-12秒 ≈ 连续跑24小时最多约360次
# - Per-minute cap adds second-layer protection
# - 每分钟上限作为第二层保护，防止短时间密集请求触发风控
REQUEST_DELAY_MIN = 8.0    # Min seconds between requests / 最小请求间隔（秒）
REQUEST_DELAY_MAX = 12.0   # Max seconds between requests / 最大请求间隔（秒）
MAX_PER_MINUTE = 5          # Max requests in any 60s window / 每分钟最多请求数
DAILY_LIMIT = 250           # Max requests per day / 每日最大请求数

# === Peak hour avoidance / 高峰时段规避 ===
AVOID_PEAK_HOURS = True
PEAK_START_HOUR = 13        # Peak hour start (24h) / 高峰开始时间
PEAK_END_HOUR = 15          # Peak hour end (24h) / 高峰结束时间
WEEKEND_LIMIT = 150         # Reduced limit on weekends / 周末降低上限

# === Advanced anti-crawl / 高级反爬 ===
# When we get a 429, wait this many seconds before retry (doubles each time)
# 遇到429时，初始等待秒数（每次翻倍）
RETRY_BASE_DELAY = 60       # Start at 60s, then 120s, 240s, max 600s
RETRY_MAX_DELAY = 600       # Max 10 minutes between retries
RETRY_MAX_ATTEMPTS = 3      # Max retries before giving up

BATCH_SIZE = 20              # Results per API page / 每页API返回条数

# === Search configuration / 搜索配置 ===
SEARCH_TOPICS = [
    # 社会与权力 (Society & Power)
    "世界的真相是什么",
    "社会的底层规则",
    "世界运行的本质规则",
    "社会潜规则",
    "人性真相",
    "社会运行的逻辑",
    "这个世界是怎么运作的",
    "人性到底能有多阴暗",
    "权力是什么",
    "社会阶层如何跨越",

    # 经济与职场 (Economy & Career)
    "赚钱的本质是什么",
    "普通人怎么赚钱",
    "职场晋升的底层逻辑",
    "打工为什么很难致富",
    "经济运行的逻辑",
    "资本家是如何剥削的",
    "中产阶级如何破局",
    "什么是资产什么是负债",

    # 认知与心理 (Cognition & Psychology)
    "认知升级 底层逻辑",
    "人是怎么变强的",
    "如何提升认知水平",
    "改变自己为什么这么难",
    "自律的本质是什么",
    "什么是真正的聪明",
    "如何克服焦虑",
    "深度思考的能力怎么培养",

    # 人际关系 (Relationships)
    "人际关系的本质",
    "如何识人",
    "社交的底层逻辑",
    "亲密关系的真相",
    "为什么好人没好人缘",
    "说话的艺术 高情商",
    "如何判断一个人的价值观",

    # 策略与决策 (Strategy & Decision)
    "选择比努力更重要吗",
    "如何做正确的决定",
    "长期主义是什么意思",
    "风险控制的本质",
    "什么是博弈思维",
    "如何建立人生护城河",
    "失败中能学到什么",
]

# How many search results per topic / 每个主题取多少搜索结果
MAX_QUESTIONS_PER_TOPIC = 10   # Questions to scrape per topic / 每主题爬取问题数
MAX_ANSWERS_PER_QUESTION = 15  # Answers per question / 每个问题爬取回答数

# === Output formats / 输出格式 ===
SAVE_JSON = True
SAVE_SQLITE = True

# === HTTP headers / 请求头 ===
# Why rotation / 为什么轮换:
# - Fixed User-Agent is detectable by anti-bot systems
# - 固定User-Agent容易被反爬系统识别
# - Multiple UAs from different browsers makes traffic look organic
# - 多个浏览器头让流量看起来更自然
USER_AGENTS = [
    # Chrome 125
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Chrome 124
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Edge 125
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    # Firefox 127
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) "
    "Gecko/20100101 Firefox/127.0",
]

HEADERS_TEMPLATE = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.zhihu.com/",
    "x-requested-with": "XMLHttpRequest",
    # Why XMLHttpRequest: Zhihu API requires this header for JSON responses
}
