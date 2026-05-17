#!/usr/bin/env python3
"""
CLI entry point for Zhihu scraper.
知乎爬虫命令行入口

Usage / 使用方法:
    To see this help / 查看帮助:
        python zhihu_scraper\cli.py --help

    First time: set up cookies / 首次使用：设置Cookie:
        python zhihu_scraper\cli.py --login

    Run full scrape / 执行完整爬取:
        python zhihu_scraper\cli.py --run

    Export for LLM / 导出供LLM使用:
        python zhihu_scraper\cli.py --export
"""
import sys
import argparse
from pathlib import Path

# Add parent dir to path so we can run as `python zhihu_scraper/cli.py`
# 将上级目录加入路径，使我们可以直接运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zhihu_scraper.auth import save_cookies
from zhihu_scraper.api import ZhihuAPI
from zhihu_scraper.search import search_and_collect
from zhihu_scraper.storage import save_results, export_for_llm
from zhihu_scraper.config import SEARCH_TOPICS, DAILY_LIMIT, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, MAX_PER_MINUTE


def cmd_login():
    """Interactive cookie setup / 交互式Cookie设置

    How to get cookies / 如何获取Cookie:
    1. Open zhihu.com in Chrome, log in
       在Chrome中打开zhihu.com并登录
    2. Press F12 → Application → Cookies → zhihu.com
       按F12 → Application → Cookies → zhihu.com
    3. Right-click any cookie → Copy All
       右键任意Cookie → 全部复制
    4. Paste below / 粘贴到下方
    """
    print("=" * 60)
    print("Zhihu Cookie Setup / 知乎Cookie设置")
    print("=" * 60)
    print()
    print("Step 1: Open Chrome, log in to https://www.zhihu.com")
    print("步骤1: 打开Chrome，登录知乎")
    print()
    print("Step 2: Press F12 → Application (应用) → Cookies → zhihu.com")
    print("步骤2: 按F12 → 应用 → Cookie → zhihu.com")
    print()
    print("Step 3: Click any cookie, Ctrl+A to select all, Ctrl+C to copy")
    print("步骤3: 点击任意Cookie，Ctrl+A全选，Ctrl+C复制")
    print()
    print("Step 4: Paste below (paste and press Enter, then Ctrl+Z then Enter):")
    print("步骤4: 粘贴到下方（粘贴后按Enter，再按Ctrl+Z再按Enter）:")
    print()

    cookie_str = input("Paste cookies here / 在此粘贴Cookie: ").strip()
    if not cookie_str:
        print("[ERROR] Nothing entered. Aborted. / 未输入任何内容。已取消。")
        return

    if save_cookies(cookie_str):
        print()
        print("Next step / 下一步:")
        print("  Run: python zhihu_scraper\\cli.py --run")
        print("  This will search and collect data / 这将搜索并收集数据")


def cmd_run():
    """Execute the full scrape pipeline / 执行完整爬取流程"""
    print("=" * 60)
    print("Zhihu Scraper - Starting / 知乎爬虫 - 开始运行")
    print("=" * 60)
    print(f"Topics to search / 搜索主题数: {len(SEARCH_TOPICS)}")
    print(f"Daily limit / 每日上限: {DAILY_LIMIT} requests")
    print(f"Request delay / 请求间隔: {REQUEST_DELAY_MIN}-{REQUEST_DELAY_MAX}s (random)")
    print(f"Per-minute limit / 每分钟上限: {MAX_PER_MINUTE} requests")
    print()

    api = ZhihuAPI()

    if not api.is_authenticated():
        print("[ERROR] Not authenticated. Run --login first.")
        print("[ERROR] 未登录。请先运行 --login。")
        return

    print("[OK] Authenticated. Starting scrape...")
    print("[OK] 已认证。开始爬取...")
    print()

    results = search_and_collect(api, SEARCH_TOPICS)

    if not results:
        print("[WARN] No results collected. Check your cookies or network.")
        print("[WARN] 未收集到结果。请检查Cookie或网络。")
        return

    print()
    print("Saving results / 保存结果...")
    saved_files = save_results(results)

    print()
    print("=" * 60)
    print("Done! / 完成！")
    print(f"Questions collected / 收集问题数: {len(results)}")
    total_answers = sum(len(q.get("answers", [])) for q in results)
    print(f"Answers collected / 收集回答数: {total_answers}")
    print(f"Requests made today / 今日请求数: {api.today_count}")
    print()
    print(f"Saved to / 已保存至:")
    for f in saved_files:
        print(f"  {f}")
    print()
    print("Export for LLM / 导出供LLM使用:")
    print("  python zhihu_scraper\\cli.py --export")


def cmd_export():
    """Export cleaned data for LLM / 导出已清洗数据供LLM使用"""
    output = export_for_llm()
    if output:
        print()
        print("You can now use this file for / 现在可以将这个文件用于:")
        print("  1. LLM knowledge base injection / 注入LLM知识库")
        print("  2. Fine-tuning data / 微调训练数据")
        print("  3. Reference cases for 规则解剖模型")
        print("  4. Manual reading to understand patterns / 手动阅读理解模式")


def main():
    parser = argparse.ArgumentParser(
        description="Zhihu Scraper - Collect data for 规则解剖模型 knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 示例:
  python zhihu_scraper\\cli.py --login     First-time cookie setup / 首次设置Cookie
  python zhihu_scraper\\cli.py --run       Full scrape / 完整爬取
  python zhihu_scraper\\cli.py --export    Export cleaned text for LLM / 导出给LLM
        """,
    )

    parser.add_argument(
        "--login", action="store_true",
        help="Set up Zhihu cookies (do this first) / 设置知乎Cookie（先做这个）"
    )
    parser.add_argument(
        "--run", action="store_true",
        help="Run full scrape / 执行完整爬取"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export latest data for LLM / 导出最新数据给LLM"
    )

    args = parser.parse_args()

    if args.login:
        cmd_login()
    elif args.run:
        cmd_run()
    elif args.export:
        cmd_export()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
