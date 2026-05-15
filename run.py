#!/usr/bin/env python3
"""
终极逻辑判断模型 . 九维思维矩阵

整合九本逻辑/思维经典构建的多层推理引擎（v2.0 增强版）：
① 逻辑学十五讲 ② 学会提问 ③ 思考,快与慢 ④ 简单的逻辑学
⑤ 论证是一门学问 ⑥ 批判性思维工具 ⑦ 麦肯锡教我的逻辑思维
⑧ 世界的逻辑 ⑨ 源思维

依赖: pip install -r requirements.txt
使用: 设置环境变量 DEEPSEEK_API_KEY，或使用 --config 配置文件
"""

import argparse
import json
import os
import sys

# Windows 终端 UTF-8 支持
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ljmodel import LogicJudgeModel, ReasoningEngine, KNOWLEDGE_BASE


def interactive_mode():
    """交互式分析 CLI"""
    print("\n" + "#" * 60)
    print("#  终极逻辑判断模型 . 九维思维矩阵")
    print("#" + " " * 20 + "整合9本经典著作的思维框架")
    print("#" * 60)
    print()

    judge = LogicJudgeModel()

    print("\n支持的命令：")
    print("  analyze <文本>  — 全面逻辑分析")
    print("  syllogism       — 三段论验证")
    print("  causal          — 因果分析")
    print("  models          — 查看所有知识库模型")
    print("  help            — 帮助")
    print("  exit/quit       — 退出")
    print()

    reasoning = ReasoningEngine()

    while True:
        try:
            cmd = input("\n> ").strip()
            if not cmd:
                continue
            if cmd in ("exit", "quit"):
                print("再见！")
                break
            elif cmd == "help":
                print("可用命令同上。也可输入原始文本直接开始分析。")
            elif cmd == "models":
                for name, info in KNOWLEDGE_BASE.items():
                    print(f"  {name}: {info['source']}")
            elif cmd.startswith("analyze "):
                text = cmd[8:]
                judge.analyze(text)
            elif cmd == "syllogism":
                print("三段论验证器")
                major = input("  大前提: ")
                minor = input("  小前提: ")
                conc = input("  结论: ")
                result = reasoning.syllogism_check(major, minor, conc)
                print(f"  有效: {result['有效']}")
                for a in result["分析"]:
                    print(f"  {a}")
            elif cmd == "causal":
                claim = input("  因果陈述: ")
                result = reasoning.analyze_causal(claim)
                print(f"  原因: {result['原因']}")
                print(f"  结果: {result['结果']}")
                print(f"  需排除: {result['替代解释']}")
            else:
                judge.analyze(cmd)

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def _read_input(path: str) -> list[str]:
    """从文件读取文本列表"""
    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(item) for item in data if item]
        return [str(data)]
    else:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]


def _batch_analyze(texts: list[str], modules: list[str] = None, html_mode: bool = False):
    """批量分析文本"""
    judge = LogicJudgeModel()
    results = []
    for i, text in enumerate(texts):
        html_path = f"logic_judge_report_{i+1}.html" if html_mode else None
        print(f"[{i+1}/{len(texts)}] 分析中...")
        result = judge.analyze(text, verbose=False, html_path=html_path, modules=modules)
        result["_index"] = i
        results.append(result)
        print(f"  [OK] 完成")
    return results


def _build_parser() -> argparse.ArgumentParser:
    """构建参数解析器"""
    parser = argparse.ArgumentParser(
        prog="logic-judge",
        description="终极逻辑判断模型 · 九维思维矩阵 — 对任意文本进行深度逻辑分析",
    )

    # 文本参数（位置参数）
    parser.add_argument("text", nargs="*", help="待分析文本")

    # 输出控制
    parser.add_argument("--json", "-j", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--html", action="store_true", help="生成 HTML 报告")

    # 模块选择
    parser.add_argument("--modules", "-m", type=str,
                        help="指定分析模块，逗号分隔（默认全部）")
    # 配置
    parser.add_argument("--config", "-c", type=str,
                        help="配置文件路径 (YAML)")

    # 批量处理
    parser.add_argument("--input", "-i", type=str,
                        help="输入文件路径，逐行或 JSON 数组格式")
    parser.add_argument("--output", "-o", type=str,
                        help="输出文件路径 (JSON)")

    # 历史记录
    parser.add_argument("--history", "-H", nargs="?", const=0, default=None, type=int,
                        help="列出最近分析记录，或查看指定 ID 的记录")
    parser.add_argument("--clear", action="store_true",
                        help="与 --history 配合使用，清空所有历史")

    # 书籍管理
    parser.add_argument("--books", nargs="?", const=0, default=None,
                        help="列出所有书籍，或查看指定书籍内容")

    # 服务模式
    parser.add_argument("--serve", "-s", action="store_true",
                        help="启动 API 服务器")
    parser.add_argument("--port", "-p", type=int, default=8000,
                        help="API 服务器端口 (默认 8000)")
    parser.add_argument("--reload", action="store_true",
                        help="开启自动重载（改代码/YAML 后自动重启服务器）")

    return parser


def main():
    """入口"""
    parser = _build_parser()
    args = parser.parse_args()
    text = " ".join(args.text) if args.text else None

    # 历史记录
    if args.history is not None:
        from ljmodel.database import list_analyses, get_analysis, clear_history
        if args.clear:
            n = clear_history()
            print(f"已清空 {n} 条历史记录")
            return
        if args.history > 0:
            row = get_analysis(args.history)
            if row is None:
                print(f"记录 #{args.history} 不存在")
                return
            print(f"\n## 分析记录 #{row['id']} ({row['created_at']})")
            print(f"   文本: {row['text'][:100]}")
            print(f"   评分: {row['score']}/100")
            print(f"   模块: {', '.join(row['modules'][:5])}")
            print(f"   结果概要: 发现 {len(row['result'].get('synthesis', {}).get('主要发现', []))} 条, "
                  f"警告 {len(row['result'].get('synthesis', {}).get('警告', []))} 条")
            return
        rows = list_analyses(10)
        if not rows:
            print("暂无分析记录")
            return
        print(f"\n最近 {len(rows)} 条分析记录:")
        print(f"{'ID':<4} {'评分':<6} {'时间':<20} 文本")
        print("-" * 60)
        for r in rows:
            text_short = r["text"][:50].replace("\n", " ")
            print(f"{r['id']:<4} {r['score']}/100  {r['created_at']:<20} {text_short}")
        print("\n使用 python run.py -H <ID> 查看详情")
        return

    # 书籍管理
    if args.books is not None:
        from ljmodel.knowledge_base import KNOWLEDGE_BASE
        if args.books and args.books != 0:
            book = KNOWLEDGE_BASE.get(args.books)
            if book is None:
                print(f"书籍 '{args.books}' 不存在")
                print(f"可用书籍: {', '.join(KNOWLEDGE_BASE.keys())}")
                return
            print(f"\n## {book.get('source', args.books)}")
            print(f"   描述: {book.get('description', '')}")
            print(f"   字段: {', '.join(k for k in book.keys() if k not in ('source','description'))}")
            return
        print(f"\n可用书籍 ({len(KNOWLEDGE_BASE)} 本):")
        for name, book in KNOWLEDGE_BASE.items():
            print(f"  {name}: {book.get('source', '')} — {book.get('description', '')[:60]}")
        print("\n使用 python run.py --books <name> 查看详情")
        return

    # 从配置文件加载默认模块
    if args.config:
        from ljmodel.config import _load_config
        cfg = _load_config(args.config)
        if cfg.get("modules") and not args.modules:
            args.modules = ",".join(cfg["modules"])

    # 模块列表
    modules = [m.strip() for m in args.modules.split(",")] if args.modules else None

    # 服务模式
    if args.serve:
        from api_server import run_server
        run_server(port=args.port, reload=args.reload)
        return

    # 批量模式
    if args.input:
        texts = _read_input(args.input)
        if not texts:
            print("错误: 输入文件为空", file=sys.stderr)
            sys.exit(1)
        results = _batch_analyze(texts, modules, args.html)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存至 {args.output}")
        elif args.json:
            print(json.dumps(results, ensure_ascii=True, indent=2))
        return

    # 单文本分析
    if text:
        html_path = "logic_judge_report.html" if args.html else None
        judge = LogicJudgeModel()
        result = judge.analyze(text, verbose=not args.json,
                               html_path=html_path, modules=modules)
        if args.json:
            print(json.dumps(result, ensure_ascii=True, indent=2))
        return

    # 无参数 -> 交互模式
    interactive_mode()


if __name__ == "__main__":
    main()
