"""终极逻辑判断模型 . 九维思维矩阵 — 主调度器"""

import hashlib
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from openai import OpenAI

from .config import CONFIG
from .knowledge_base import KNOWLEDGE_BASE
from .logger import logger
from .analyzers import (
    analyze_formal_logic, analyze_critical_inquiry, analyze_biases,
    analyze_argumentation, analyze_elements_of_thought, analyze_structured,
    analyze_dialectical, analyze_source_thinking, analyze_simple_logic,
    analyze_llm_primary, build_llm_primary_prompt,
    analyze_logic_problems, analyze_zhihu_expert,
)

ALL_MODULES = {
    "formal_logic": analyze_formal_logic,
    "critical_inquiry": analyze_critical_inquiry,
    "bias_detection": analyze_biases,
    "argumentation": analyze_argumentation,
    "elements_of_thought": analyze_elements_of_thought,
    "structured_analysis": analyze_structured,
    "dialectical": analyze_dialectical,
    "source_thinking": analyze_source_thinking,
    "simple_logic": analyze_simple_logic,
    "zhihu_expert": analyze_zhihu_expert,
    "llm_primary": None,  # special-cased
}
from .synthesis import synthesize
from .coordinator import coordinate
from .report import print_report
from .report_html import generate_html_report
from .database import save_analysis
from .debate_engine import DebateEngine, print_debate_report


class LogicJudgeModel:
    """
    终极逻辑判断模型 . 九维思维矩阵

    整合九本经典著作的思维框架，构建多层推理引擎，
    通过系统化的分析流程对任何论述、决策或问题进行深度逻辑判断。
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 llm_provider: Optional[str] = None):
        """初始化模型

        Args:
            api_key: LLM API密钥，默认从 .env / 环境变量 DEEPSEEK_API_KEY 读取
                     显式传入空字符串 "" 可禁用 LLM
            model: 使用的模型名
            llm_provider: LLM提供商，deepseek / openai，默认从配置读取
        """
        cfg = CONFIG
        if api_key is None:
            self.api_key = cfg["api_key"] or os.environ.get("DEEPSEEK_API_KEY", "")
        else:
            self.api_key = api_key
        self.llm_provider = (llm_provider or cfg.get("llm_provider") or "deepseek").lower()

        # 根据提供商设置默认参数
        PROVIDERS = {
            "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
            "openai":   {"base_url": "https://api.openai.com/v1",       "model": "gpt-4o"},
        }
        provider_defaults = PROVIDERS.get(self.llm_provider, PROVIDERS["deepseek"])
        self.base_url = cfg.get("base_url") or provider_defaults["base_url"]
        self.model = model or cfg.get("model") or provider_defaults["model"]

        # 从配置同步日志级别
        level = (cfg.get("log_level") or "WARNING").upper()
        logger.setLevel(getattr(logging, level, logging.WARNING))

        if not self.api_key:
            logger.warning("未设置 DEEPSEEK_API_KEY，将使用本地知识库分析（无 LLM 增强）")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

        # 豆包/火山引擎大模型客户端（作为逻辑问题猎手2使用）
        doubao_key = cfg.get("doubao_api_key") or os.environ.get("DOUBAO_API_KEY", "")
        self.doubao_key = doubao_key
        self.doubao_base_url = cfg.get("doubao_base_url") or os.environ.get("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.doubao_model = cfg.get("doubao_model") or os.environ.get("DOUBAO_MODEL", "doubao-pro-32k")
        if doubao_key:
            logger.info("豆包大模型客户端已就绪（逻辑问题猎手2）")
            self.doubao_client = OpenAI(api_key=doubao_key, base_url=self.doubao_base_url)
        else:
            self.doubao_client = None
        self.kb = KNOWLEDGE_BASE
        self._cache: dict[str, dict] = {}
        self._cache_max = 64

    # --- 工具方法 ---------------------------------------------------------

    def _llm_chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """调用 DeepSeek 大模型（如果可用）"""
        if not self.client:
            return ""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[LLM 调用异常: {e}]"

    def _prompt_system(self) -> str:
        """构建系统提示词"""
        return f"""你是 <终极逻辑判断模型 . 九维思维矩阵 v2.0>。
你整合了以下九本逻辑/思维经典的核心框架：
1. 《逻辑学十五讲》(陈波) — 命题逻辑(¬∧∨→↔)/词项逻辑(A/E/I/O)/谓词逻辑(∀∃)/归纳逻辑(密尔五法)/形式谬误与非形式谬误(歧义性/假设性/关联性共20+种)/悖论(说谎者/罗素)
2. 《学会提问》(Neil Browne) — 淘金式思维 + 批判性质询10问
3. 《思考,快与慢》(Kahneman) — 系统1快思维/系统2慢思维；认知放松/紧张；启动效应；WYSIATI；前景理论(参照点/损失厌恶/风险偏好逆转)；峰终定律；体验自我vs记忆自我；理论诱导盲视
4. 《简单的逻辑学》— 逻辑基本定律、思维准备、非逻辑根源
5. 《论证是一门学问》(Weston) — 24条论证规则（举例/类比/权威/因果/演绎）
6. 《批判性思维工具》(Paul & Elder) — 思维8元素+9理智标准+7思维特质+自我中心/社会中心思维
7. 《麦肯锡教我的逻辑思维》— MECE、金字塔原理、逻辑树、四象限
8. 《世界的逻辑》(Harvey) — 辩证系统分析、资本循环、剥夺性积累、空间修复、不平衡发展
9. 《源思维》(何艳玲) — 还原事实->辨析因果->锚定切口；多元因果思维；关键X
10. 《知乎集体智慧》— 从知乎高赞回答中提炼的真实世界经验（社会与权力/经济与职场/认知与心理/人际关系/策略与决策五大领域）

回答要求：
- 严格遵循逻辑推理，区分演绎有效性和归纳强度
- 指出论证中的假设、歧义和潜在谬误
- 考虑多种视角和替代解释
- 明确区分描述性陈述和规范性陈述
- 保持思维谦逊，指出不确定之处"""

    # --- 缓存 ---------------------------------------------------------------

    def _cache_key(self, text: str, modules: Optional[list[str]] = None) -> str:
        key = hashlib.md5(text.encode()).hexdigest()
        if modules:
            key += ":" + hashlib.md5(json.dumps(sorted(modules), ensure_ascii=False).encode()).hexdigest()
        return key

    def clear_cache(self):
        """清空分析结果缓存"""
        self._cache.clear()

    # --- 核心分析管道 ----------------------------------------------------

    def analyze(self, text: str, verbose: bool = True, html_path: str = None,
                modules: Optional[list[str]] = None, use_cache: bool = False,
                save_db: bool = True) -> dict:
        """对输入文本进行全面逻辑分析

        架构: LLM主分析 + 规则引擎交叉验证
        - LLM作为主角，使用9本书框架进行综合分析
        - 规则引擎作为辅助，检测关键词模式来交叉验证LLM的结论

        Args:
            text: 待分析文本
            verbose: 是否打印控制台报告
            html_path: 可选，HTML报告输出路径
            modules: 可选，要运行的模块列表（默认全部运行）
                     可用模块：formal_logic, critical_inquiry, bias_detection,
                     argumentation, elements_of_thought, structured_analysis,
                     dialectical, source_thinking, simple_logic, llm_primary
        """
        result = {
            "input": text,
            "modules": {},
            "synthesis": {}
        }

        if use_cache:
            cached = self._cache.get(self._cache_key(text, modules))
            if cached:
                logger.info("缓存命中 — 返回缓存结果")
                return cached

        run_all = modules is None

        if verbose:
            logger.info("=" * 56 + " 九维思维矩阵 (LLM主分析模式)")
            logger.info(f"分析对象: {text[:100]}{'...' if len(text) > 100 else ''}")

        # 阶段1: LLM主分析
        if self.client and (run_all or "llm_primary" in modules):
            logger.info("LLM综合分析中...")
            try:
                result["modules"]["llm_primary"] = analyze_llm_primary(text, self.kb, self.client, self.model)
                logger.info("LLM分析完成")
            except Exception as e:
                logger.warning(f"LLM分析异常: {e}")
                result["modules"]["llm_primary"] = {"error": str(e)}
        else:
            result["modules"]["llm_primary"] = {}

        # 阶段2: 规则引擎交叉验证（并行执行）
        logger.info("规则引擎交叉验证中...")
        modules_to_run = [
            (name, func) for name, func in ALL_MODULES.items()
            if name != "llm_primary" and (run_all or name in modules)
        ]
        with ThreadPoolExecutor(max_workers=len(modules_to_run) or 1) as executor:
            fut = {executor.submit(func, text, self.kb): name for name, func in modules_to_run}
            for f in as_completed(fut):
                name = fut[f]
                try:
                    result["modules"][name] = f.result()
                except Exception as e:
                    logger.warning(f"模块 [{name}] 执行异常: {e}")
                    result["modules"][name] = {"error": str(e)}
        logger.info("规则引擎交叉验证完成")

        # 阶段3: 逻辑问题猎手1 — DeepSeek 独立LLM审查
        if self.client and (run_all or "llm_primary" in modules):
            logger.info("逻辑问题猎手1搜寻中...")
            try:
                result["modules"]["logic_problem_hunter_1"] = analyze_logic_problems(
                    text, result, self.client, self.model
                )
                logger.info("逻辑问题猎手1完成")
            except Exception as e:
                logger.warning(f"逻辑问题猎手1异常: {e}")
                result["modules"]["logic_problem_hunter_1"] = {"error": str(e)}

        # 阶段3b: 逻辑问题猎手2 — 豆包大模型独立审查（提供第二视角交叉验证）
        if self.doubao_client and (run_all or "llm_primary" in modules):
            logger.info("逻辑问题猎手2（豆包大模型）搜寻中...")
            try:
                result["modules"]["logic_problem_hunter_2"] = analyze_logic_problems(
                    text, result, self.doubao_client, self.doubao_model
                )
                logger.info("逻辑问题猎手2完成")
            except Exception as e:
                logger.warning(f"逻辑问题猎手2异常: {e}")
                result["modules"]["logic_problem_hunter_2"] = {"error": str(e)}

        # 阶段3: 综合合成
        result["synthesis"] = synthesize(result)

        # 阶段4: 智囊团协调 — 跨专家综合分析
        result["coordination"] = coordinate(result["modules"], result.get("input", ""))

        # 持久化到 SQLite
        if save_db:
            try:
                score_str = result["synthesis"].get("逻辑质量评分", "")
                score = 0
                import re
                m = re.search(r"(\d+)/100", score_str)
                if m:
                    score = int(m.group(1))
                save_analysis(text, score, modules or list(ALL_MODULES.keys()), result)
            except Exception as e:
                logger.warning(f"数据库保存失败: {e}")

        self._cache[self._cache_key(text, modules)] = result

        if verbose:
            print_report(result)

        if html_path:
            generate_html_report(result, html_path)
            logger.info(f"HTML报告已保存至 {os.path.abspath(html_path)}")

        return result

    # ========== 规则解剖模型 — 独立决策分析引擎 ==========

    def dissect(self, text: str, mode: str = "auto", verbose: bool = True) -> dict:
        """规则解剖模型 — 独立决策分析引擎

        结合所有知识库（9本逻辑经典 + 知乎集体智慧），
        对用户的决策/问题进行全面剖析。不评分，只剖析。

        Args:
            text: 用户问题/决策场景
            mode: 'auto'（自动检测）, 'a'（解剖引擎-博弈分析）, 'b'（共鸣拓扑-方向导航）
            verbose: 是否打印分析报告

        Returns:
            dict: 完整的决策分析结果
        """
        from .dissection_engine import DissectionEngine
        from .resonance_engine import ResonanceEngine

        # 模式检测
        a_signals = ["该不该", "怎么谈", "如何选择", "值不值得", "利益", "风险",
                      "跳槽", "薪资", "谈判", "决策", "权衡", "划算", "博弈"]
        b_signals = ["迷茫", "不知道", "没感觉", "累了", "焦虑",
                      "没意义", "赢了也不开心", "困惑", "找不到方向"]

        if mode == "auto":
            a_score = sum(1 for s in a_signals if s in text)
            b_score = sum(1 for s in b_signals if s in text)
            if a_score >= b_score and a_score > 0:
                mode = "a"
            elif b_score > 0:
                mode = "b"
            else:
                mode = "a"  # default

        if verbose:
            print(f"\n{'='*60}")
            print(f"  规则解剖模型 V4.0 — {'博弈分析（模式A）' if mode == 'a' else '方向导航（模式B）'}")
            print(f"{'='*60}")
            print(f"  分析对象: {text[:100]}{'...' if len(text) > 100 else ''}")
            print(f"{'='*60}\n")

        if mode == "b":
            engine = ResonanceEngine(self.kb)
            result = engine.analyze(text)
            if verbose:
                self._print_dissection_report(result, mode="b")
            return result

        # 模式A: 解剖引擎 — 完整决策分析
        engine = DissectionEngine(self.kb)
        result = engine.analyze(text)

        # 整合知乎知识库洞察（如果数据存在）
        zhihu_insights = self._get_zhihu_insights(text)
        if zhihu_insights:
            result["知乎参考"] = zhihu_insights

        if verbose:
            self._print_dissection_report(result, mode="a")

        return result

    def _get_zhihu_insights(self, text: str) -> dict:
        """从知乎知识库获取相关洞察"""
        try:
            from .analyzers.zhihu_expert import _get_db, _extract_keywords, _search_answers, _search_questions
            conn = _get_db()
            if not conn:
                return {}
            keywords = _extract_keywords(text, max_keywords=5)
            qs = _search_questions(conn, keywords, max_results=3)
            ans = _search_answers(conn, keywords, min_votes=500, max_answers=5)
            conn.close()
            return {
                "关键词": keywords,
                "相关问题": [q["title"] for q in qs],
                "高赞参考": [{"作者": a["author"], "问题": a["question_title"][:60],
                              "赞同": a["voteup_count"]} for a in ans],
            }
        except Exception:
            return {}

    def _print_dissection_report(self, result: dict, mode: str = "a"):
        """打印解剖分析报告"""
        if mode == "b":
            pain = result.get("痛苦分类", {})
            print(f"  [痛苦分类] 类型: {pain.get('类型', '未分类')}")
            print(f"  [状态] {pain.get('状态', '')}")
            print(f"  [建议] {pain.get('建议操作', '')}")
            print()
            for s in result.get("感知扫描", []):
                print(f"  ? {s}")
            for f in result.get("场域检查", []):
                print(f"  ? {f}")
            ladder = result.get("梯子检查", {})
            if isinstance(ladder, dict):
                for k, v in ladder.items():
                    if isinstance(v, list):
                        for item in v:
                            print(f"  [{k}] {item}")
                    else:
                        print(f"  [{k}] {v}")
            print(f"\n{'='*60}")
            return

        # 模式A: 完整解剖报告
        mode_judge = result.get("模式判定", {})
        print(f"  [模式判定] {mode_judge.get('依据', '')} (置信度: {mode_judge.get('置信度', '')})")

        # 博弈地图
        print(f"\n  ┌─ 博弈地图 ──────────────────────────────")
        gm = result.get("博弈地图", {})
        if gm:
            for key, val in gm.items():
                if key.startswith("_"):
                    continue
                if isinstance(val, list) and val:
                    print(f"  │ {key}:")
                    for v in val:
                        print(f"  │   • {v}")
                elif isinstance(val, str):
                    print(f"  │ {key}: {val}")

        # 风险计算
        print(f"\n  ┌─ 风险扫描 ──────────────────────────────")
        risks = result.get("风险计算", {})
        if risks:
            for k, v in risks.items():
                if not k.startswith("_"):
                    print(f"  │ {k}: {v}")

        # 公理冲突
        print(f"\n  ┌─ 公理冲突检查 ──────────────────────────")
        conflicts = result.get("公理冲突检查", {})
        if conflicts:
            print(f"  │ 活跃公理: {'、'.join(conflicts.get('活跃公理列表', []))}")
            for c in conflicts.get("冲突列表", []):
                if isinstance(c, dict):
                    cv = c.get("裁决", "")
                    ca = c.get("公理A", "")
                    cb = c.get("公理B", "")
                    print(f"  │ [!] {ca} vs {cb} → {cv}")

        # 行动指令
        print(f"\n  ┌─ 行动指令 ──────────────────────────────")
        for a in result.get("行动指令", []):
            print(f"  │ • {a}")

        # 预测
        preds = result.get("预测", [])
        if preds and not any("暂无足够信息" in str(p.get("text", "")) for p in preds):
            print(f"\n  ┌─ 预测（将被记录并验证）───────────────")
            for p in preds:
                conf = p.get("置信度", "?")
                text = p.get("text", "")[:200]
                print(f"  │ [置信度: {conf}] {text}")

        # 知乎参考
        zhihu = result.get("知乎参考", {})
        if zhihu and zhihu.get("高赞参考"):
            print(f"\n  ┌─ 知乎集体智慧参考 ────────────────────")
            for a in zhihu["高赞参考"][:3]:
                print(f"  │ • [{a['赞同']}赞] {a['作者']} — {a.get('问题', '')}")
        elif zhihu:
            print(f"\n  ┌─ 知乎集体智慧参考 ────────────────────")
            print(f"  │ （知识库中暂未找到相关问题）")

    # ========== 多模型智囊团深度辩论 ==========

    def debate(self, text: str, verbose: bool = True,
               dissection_result: dict = None,
               resonance_result: dict = None) -> dict:
        """多模型智囊团深度辩论

        基于解剖分析（模式A）和/或共鸣拓扑（模式B）的结构化结果，
        结合全部书籍知识库和知乎集体智慧，让 5 位领域专家进行三阶段辩论。

        Args:
            text: 用户原始问题
            verbose: 是否打印报告
            dissection_result: 解剖分析结果（模式A），可选（自动运行）
            resonance_result: 共鸣拓扑结果（模式B），可选（自动运行）

        Returns:
            dict: 辩论完整结果
        """
        # 如果没有提供分析结果，自动运行解剖
        if not dissection_result and not resonance_result:
            if verbose:
                print("\n  [自动运行规则解剖分析作为辩论输入...]")
            dissection_result = self.dissect(text, mode="a", verbose=False)
            resonance_result = self.dissect(text, mode="b", verbose=False)

        engine = DebateEngine(
            kb=self.kb,
            llm_client=self.client,
            llm_model=self.model,
            doubao_client=getattr(self, "doubao_client", None),
            doubao_model=getattr(self, "doubao_model", None),
        )

        result = engine.debate(
            text=text,
            dissection_result=dissection_result,
            resonance_result=resonance_result,
        )

        if verbose:
            print_debate_report(result)

        return result
