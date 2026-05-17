"""
Content extraction and cleaning: HTML → plain text.
内容提取与清洗：HTML → 纯文本

Why this exists / 为什么存在:
- Zhihu API returns content as rich HTML with tags, images, links
- 知乎API返回的内容是带标签、图片、链接的富HTML
- LLMs need clean plain text for training / knowledge base
- 大语言模型需要干净的纯文本用于训练/知识库
"""
import re
from html import unescape


def clean_html(html_content: str) -> str:
    """Strip HTML tags and decode entities → readable plain text.
    去除HTML标签并解码实体 → 可读的纯文本

    Why this order / 为什么这个顺序:
    1. Remove code blocks first (they contain < and > symbols)
       先移除代码块（它们包含<和>符号）
    2. Then strip remaining tags
       再移除剩余标签
    3. Finally decode HTML entities like &amp; → &
       最后解码HTML实体
    """
    if not html_content:
        return ""

    text = html_content

    # Step 1: Remove code blocks (they contain angle brackets)
    # 步骤1：移除代码块（它们包含尖括号）
    text = re.sub(r'<pre>.*?</pre>', '', text, flags=re.DOTALL)
    text = re.sub(r'<code>.*?</code>', '', text, flags=re.DOTALL)

    # Step 2: Remove images (just keep alt text if any)
    # 步骤2：移除图片（保留alt文本）
    text = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'\1', text)
    text = re.sub(r'<img[^>]*>', '', text)

    # Step 3: Replace <br> and </p> with newlines
    # 步骤3：将换行标签替换为实际换行
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)

    # Step 4: Remove all remaining HTML tags
    # 步骤4：移除所有剩余HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # Step 5: Decode HTML entities / 解码HTML实体
    text = unescape(text)

    # Step 6: Remove multiple blank lines (keep max 2)
    # 步骤6：合并多余空行（最多保留2个连续换行）
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Step 7: Strip leading/trailing whitespace
    # 步骤7：去除首尾空格
    text = text.strip()

    return text


def trim_to_length(text: str, max_chars: int = 5000) -> str:
    """Trim text to a maximum character count, preserving whole sentences.
    将文本截断至最大字符数，保持句子完整

    Why / 为什么:
    - Some answers are extremely long (>10000 chars)
    - 有些回答非常长（超过10000字）
    - For knowledge base, first ~5000 chars has the core argument
    - 对于知识库，前5000字通常包含核心论点
    """
    if len(text) <= max_chars:
        return text

    # Cut at max_chars, then find last sentence boundary
    # 在max_chars处截断，然后找最后一个句子边界
    cut = text[:max_chars]
    last_period = cut.rfind("。")
    last_newline = cut.rfind("\n\n")

    boundary = max(last_period, last_newline)
    if boundary > max_chars * 0.7:  # Only trim if we find a good boundary
        # 只在找到好的边界时才截断
        return cut[:boundary + 1] + "\n\n[...truncated/截断...]"
    return cut + "\n\n[...truncated/截断...]"
