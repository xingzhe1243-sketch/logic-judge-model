#!/usr/bin/env python3
"""
思维解剖模型 V1.0 — 基于 40+ 本书籍的多模型智囊团深度辩论系统

独立系统，非逻辑评分模型。基于全部知识库进行深度决策分析与多专家辩论。
"""
import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ljmodel import LogicJudgeModel
from ljmodel.knowledge_base import KNOWLEDGE_BASE


BANNER = """
╔══════════════════════════════════════════════════════════╗
║              思维解剖模型 V1.0                           ║
║   基于 40+ 本书籍的多模型智囊团深度辩论系统              ║
║   解剖分析 → 多专家辩论 → 综合裁决 → 行动指引           ║
╚══════════════════════════════════════════════════════════╝
"""


def interactive_mode():
    """交互式 CLI"""
    print(BANNER)
    print(f"已加载 {len(KNOWLEDGE_BASE)} 本书籍知识库")
    print()
    print("可用命令:")
    print("  dissect <问题>     — 解剖分析 + 自动模式检测")
    print("  game    <问题>     — 模式A：博弈分析")
    print("  nav     <问题>     — 模式B：方向导航")
    print("  debate  <问题>     — 多模型智囊团深度辩论")
    print("  deep    <问题>     — 解剖分析 + 深度辩论（全流程）")
    print("  books              — 列出所有书籍")
    print("  help               — 帮助")
    print("  exit               — 退出")
    print()

    judge = LogicJudgeModel()

    while True:
        try:
            cmd = input("\n❯ ").strip()
            if not cmd:
                continue
            if cmd in ("exit", "quit"):
                print("再见。")
                break
            if cmd == "help":
                print("可用命令同上。输入问题即可开始分析。")
                continue
            if cmd == "books":
                print(f"\n知识库 ({len(KNOWLEDGE_BASE)} 本书):")
                for k in sorted(KNOWLEDGE_BASE.keys()):
                    info = KNOWLEDGE_BASE[k]
                    src = info.get("source", k)[:50]
                    cc = len(info.get("core_concepts", []))
                    print(f"  [{cc:2d}概念] {src}")
                print()
                continue

            if cmd.startswith("debate "):
                text = cmd[7:]
                print(f"\n>> 启动多模型智囊团深度辩论...")
                result = judge.debate(text, verbose=True)
                continue

            if cmd.startswith("deep "):
                text = cmd[5:]
                print(f"\n>> 阶段1: 规则解剖分析...")
                dissect_result = judge.dissect(text, mode="auto", verbose=True)
                print(f"\n>> 阶段2: 多模型智囊团深度辩论...")
                debate_result = judge.debate(text, verbose=True,
                                              dissection_result=dissect_result)
                continue

            if cmd.startswith("dissect "):
                text = cmd[8:]
                judge.dissect(text, mode="auto", verbose=True)
                continue
            if cmd.startswith("game "):
                text = cmd[5:]
                judge.dissect(text, mode="a", verbose=True)
                continue
            if cmd.startswith("nav "):
                text = cmd[4:]
                judge.dissect(text, mode="b", verbose=True)
                continue

            # 默认当作 dissect 处理
            judge.dissect(cmd, mode="auto", verbose=True)

        except KeyboardInterrupt:
            print("\n再见。")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="思维解剖",
        description="思维解剖模型 — 基于40+本书的多模型智囊团深度辩论系统",
    )
    parser.add_argument("text", nargs="*", help="待分析问题")
    parser.add_argument("--mode", "-m", type=str, default="auto",
                        choices=["auto", "a", "b"],
                        help="解剖模式: auto(自动) / a(博弈分析) / b(方向导航)")
    parser.add_argument("--debate", action="store_true",
                        help="启动多模型智囊团深度辩论")
    parser.add_argument("--deep", action="store_true",
                        help="解剖分析 + 深度辩论全流程")
    parser.add_argument("--json", "-j", action="store_true",
                        help="JSON 格式输出")

    args = parser.parse_args()
    text = " ".join(args.text) if args.text else None

    if not text:
        interactive_mode()
        return

    judge = LogicJudgeModel()

    # 深度辩论
    if args.debate:
        result = judge.debate(text, verbose=not args.json)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 全流程
    if args.deep:
        dr = judge.dissect(text, mode=args.mode, verbose=not args.json)
        debate_result = judge.debate(text, verbose=not args.json,
                                      dissection_result=dr)
        if args.json:
            print(json.dumps({"解剖分析": dr, "深度辩论": debate_result},
                             ensure_ascii=False, indent=2))
        return

    # 纯解剖
    result = judge.dissect(text, mode=args.mode, verbose=not args.json)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
