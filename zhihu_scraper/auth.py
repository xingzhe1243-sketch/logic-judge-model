"""
Zhihu cookie authentication management.
知乎Cookie认证管理

Why this exists / 为什么存在:
- Zhihu requires login cookies for API access
- 知乎API需要登录Cookie才能访问
- Cookies expire after 1-2 days, so we need easy renewal
- Cookie约1-2天过期，需要方便地更新
"""
import json
import re
from pathlib import Path
from datetime import datetime


COOKIE_FILE = Path(__file__).parent / "cookies.json"


def save_cookies(cookie_str: str) -> bool:
    """Save cookies from browser to file.
    将浏览器中复制的Cookie字符串保存到文件

    Why / 为什么:
    - Store once, reuse many times without re-pasting
    - 存一次，多次复用，无需反复粘贴

    Args:
        cookie_str: Raw cookie string from browser DevTools
                    从浏览器DevTools复制的原始Cookie字符串

    Returns:
        True if valid cookies were saved / 保存成功返回True
    """
    # Parse the cookie string into a dict
    # 将Cookie字符串解析为字典
    cookies = {}
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookies[key.strip()] = value.strip()

    # Validate: z_c0 is the essential Zhihu auth cookie
    # 验证：z_c0是知乎最关键的身份验证Cookie
    if "z_c0" not in cookies:
        print("[ERROR] Missing z_c0 cookie. Please log in to zhihu.com first.")
        print("[ERROR] 缺少z_c0 Cookie。请先在浏览器登录知乎。")
        return False

    data = {
        "cookies": cookies,
        "saved_at": datetime.now().isoformat(),
        # Why ISO format: sortable, timezone-aware, universally parsable
        # ISO格式：可排序、带时区、通用可解析
    }
    COOKIE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[OK] Cookies saved to {COOKIE_FILE}")
    print(f"[OK] Cookie已保存，含 {len(cookies)} 个键值对")
    return True


def load_cookies() -> dict:
    """Load saved cookies from file.
    从文件加载已保存的Cookie

    Why / 为什么:
    - Reads the saved cookie dict for use in API requests
    - 读取已保存的Cookie字典供API请求使用
    """
    if not COOKIE_FILE.exists():
        print("[ERROR] No cookies file found. Run 'python -m zhihu_scraper.cli --login' first.")
        print("[ERROR] 未找到Cookie文件。请先运行 'python -m zhihu_scraper.cli --login'")
        return {}

    data = json.loads(COOKIE_FILE.read_text(encoding="utf-8"))
    return data.get("cookies", {})


def format_cookie_header(cookies: dict) -> str:
    """Convert cookie dict back to header string.
    将Cookie字典转换回请求头字符串

    Why / 为什么:
    - The requests library needs a semicolon-joined string
    - requests库需要分号连接的字符串格式
    """
    return "; ".join(f"{k}={v}" for k, v in cookies.items())
