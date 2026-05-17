"""规则解剖模型 V4.0 — 解剖引擎（模式A）

三层公理体系（L1 > L2 > L3），22条实战规则，
四步分析流程（博弈地图 → 风险计算 → 公理冲突检查 → 行动指令），
预测生成与置信度标注。
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional

from .logger import logger


@dataclass
class Axiom:
    """单条公理"""
    id: str
    layer: int          # 1=L1, 2=L2, 3=L3
    text: str
    supplement: str = ""
    scope_indicators: list[str] = field(default_factory=list)
    active: bool = True


@dataclass
class ConflictRecord:
    """公理冲突裁决记录"""
    axiom_a: str
    axiom_b: str
    layer_a: int
    layer_b: int
    conclusion_a: str
    conclusion_b: str
    verdict: str
    confidence: str      # "高" | "中" | "低"
    note: str = ""


class DissectionEngine:
    """规则解剖引擎 V4.0 — 博弈分析引擎"""

    def __init__(self, kb: dict):
        self._kb = kb
        self._axioms: list[Axiom] = []
        self._rules: list[dict] = []
        self._diseases: dict = {}
        self._analysis_flow: list[str] = []
        self._init_from_kb()
        self._init_llm()

    def _init_from_kb(self):
        """从知识库构建公理和规则"""
        dk = self._kb.get("dissection_model", {})
        mode_a = dk.get("mode_a", {})

        for ad in mode_a.get("axioms", []):
            layer_str = ad.get("id", "L1.0")
            layer = int(layer_str[1]) if len(layer_str) > 1 and layer_str[1].isdigit() else 1
            self._axioms.append(Axiom(
                id=ad["id"],
                layer=layer,
                text=ad["text"],
                supplement=ad.get("supplement", ""),
                scope_indicators=ad.get("scope_indicators", []),
                active=True,
            ))

        self._rules = mode_a.get("rules", [])
        self._diseases_strings = dk.get("mode_disambiguation", {})
        self._analysis_flow = [s["text"] if isinstance(s, dict) else s
                                for s in mode_a.get("analysis_flow", {}).get("steps", [])]

    def _init_llm(self):
        """惰性初始化 LLM 客户端"""
        self._client = None
        self._model = None
        try:
            from .config import CONFIG
            api_key = CONFIG.get("api_key") or os.environ.get("DEEPSEEK_API_KEY", "")
            if api_key:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key, base_url=CONFIG.get("base_url", "https://api.deepseek.com/v1"))
                self._model = CONFIG.get("model", "deepseek-chat")
        except Exception as e:
            logger.debug(f"解剖引擎 LLM 初始化跳过: {e}")

    def _llm_call(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM 进行增强分析（如果可用）"""
        if not self._client:
            return ""
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"解剖引擎 LLM 调用异常: {e}")
            return ""

    # ========== 主入口 ==========

    def analyze(self, text: str) -> dict:
        """对输入文本执行完整的模式 A 分析"""
        result = {
            "模式": "A — 解剖引擎",
            "模式判定": self._detect_mode(text),
        }
        result["博弈地图"] = self._build_game_map(text)
        result["风险计算"] = self._calculate_risks(text)
        result["公理冲突检查"] = self._check_conflicts(text, result["博弈地图"])
        actions, predictions = self._generate_actions_and_predictions(text, result)
        result["行动指令"] = actions
        result["预测"] = predictions
        result["适用规则"] = self._match_rules(text)
        result["_置信度"] = self._annotate_confidence(result)
        return result

    # ========== 步骤1: 模式判定 ==========

    def _detect_mode(self, text: str) -> dict:
        """检测文本特征，确认模式A适用性"""
        a_signals = [
            "该不该", "怎么谈", "如何选择", "值不值得",
            "利益", "风险", "跳槽", "薪资", "谈判",
            "决策", "代价", "权衡", "划算", "博弈",
        ]
        score = sum(1 for s in a_signals if s in text)
        if score >= 3:
            confidence = "高"
            basis = f"检测到 {score} 个强信号，模式A高度适用"
        elif score >= 1:
            confidence = "中"
            basis = f"检测到 {score} 个信号，建议模式A"
        else:
            confidence = "低"
            basis = "检测到少量模式A信号，需结合上下文判断"
        return {"依据": basis, "置信度": confidence, "信号强度": score}

    # ========== 步骤2: 博弈地图 ==========

    def _build_game_map(self, text: str) -> dict:
        """构建博弈地图"""
        game_map = {
            "参与者": self._extract_participants(text),
            "筹码分析": self._analyze_stakes(text),
            "对方诉求": self._analyze_opponent(text),
            "隐藏条款": self._detect_hidden_terms(text),
        }

        # LLM 增强
        if self._client and len(text) > 20:
            llm_result = self._llm_call(
                "你是一个博弈论分析专家。分析以下场景中的博弈结构，列出："
                "1) 所有参与方及其筹码 2) 各方的显性和隐性诉求 "
                "3) 可能存在的信息不对称 4) 隐藏的关键变量。简洁回答。",
                text
            )
            if llm_result:
                game_map["_llm增强"] = llm_result
        return game_map

    def _extract_participants(self, text: str) -> list[str]:
        """识别博弈参与者"""
        participants = []
        # 人称识别
        person_patterns = [
            (r"(?:我|我们|本人)", "自己"),
            (r"(?:他|她|他们|她们|对方|老板|领导|公司|同事|客户)", "对方"),
            (r"(?:第三方|中间人|中介|律师|顾问|朋友|家人|父母|伴侣)", "第三方"),
        ]
        found = set()
        for pattern, label in person_patterns:
            if re.search(pattern, text):
                found.add(label)
        participants = sorted(found)
        if not participants:
            participants = ["未明确识别的参与方"]
        return participants

    def _analyze_stakes(self, text: str) -> list[str]:
        """分析筹码"""
        stakes = []
        keywords_map = [
            (["薪资", "工资", "收入", "钱", "待遇"], "经济筹码"),
            (["职位", "title", "晋升", "级别", "头衔"], "职位筹码"),
            (["时间", "精力", "生活平衡", "加班"], "时间筹码"),
            (["机会", "前景", "发展", "成长", "学习"], "发展筹码"),
            (["关系", "人脉", "资源", "圈子"], "关系筹码"),
            (["声誉", "名声", "品牌", "口碑"], "声誉筹码"),
        ]
        for keywords, label in keywords_map:
            if any(kw in text for kw in keywords):
                stakes.append(label)
        if not stakes:
            stakes.append("待识别 — 信息不足以判断筹码")
        return stakes

    def _analyze_opponent(self, text: str) -> list[str]:
        """分析对方诉求"""
        demands = []
        # 显性诉求
        if any(kw in text for kw in ["招聘", "offer", "录用", "邀请"]):
            demands.append("显性: 希望建立合作关系")
        if any(kw in text for kw in ["销售", "推销", "推荐产品"]):
            demands.append("显性: 促成交易")
        if any(kw in text for kw in ["谈判", "协商", "沟通"]):
            demands.append("显性: 寻求双方可接受的方案")
        # 隐性诉求信号
        if any(kw in text for kw in ["急", "马上", "尽快", "限时"]):
            demands.append("可能隐藏: 对方有时间压力")
        if any(kw in text for kw in ["独家", "排他", "长期"]):
            demands.append("可能隐藏: 对方寻求绑定/锁定关系")
        if not demands:
            demands.append("待识别 — 需更多上下文判断对方诉求")
        return demands

    def _detect_hidden_terms(self, text: str) -> list[str]:
        """检测隐藏条款/潜在陷阱"""
        hidden = []
        checks = [
            (["口头", "承诺", "以后", "将来"], "警惕: 口头承诺没有约束力"),
            (["试用期", "实习"], "注意: 试用期的权利义务需明确"),
            (["分红", "期权", "股权"], "风险: 非现金报酬的兑现条件可能很苛刻"),
            (["不明确", "模糊", "含糊"], "信号: 信息不透明需要进一步澄清"),
            (["合同", "协议", "条款"], "提示: 重点关注违约责任和退出条款"),
            (["大家都", "普遍", "惯例", "行规"], "风险: '惯例'不能替代明确约定"),
        ]
        for keywords, warning in checks:
            if any(kw in text for kw in keywords):
                hidden.append(warning)
        if not hidden:
            hidden.append("未检测到明显的隐藏条款信号")
        return hidden

    # ========== 步骤3: 风险计算 ==========

    def _calculate_risks(self, text: str) -> dict:
        """多维度风险扫描"""
        risks = {
            "法律红线": self._check_red_line(text, ["违法", "起诉", "诉讼", "合同", "违规", "处罚", "罚款"]),
            "物理红线": self._check_red_line(text, ["暴力", "人身安全", "威胁", "安全"]),
            "声誉成本": self._assess_reputation_risk(text),
            "经济成本": self._assess_economic_risk(text),
            "机会成本": self._assess_opportunity_cost(text),
        }
        # LLM 增强风险扫描
        if self._client:
            llm_risk = self._llm_call(
                "作为风险分析专家，从以下输入中识别被忽略的风险。"
                "仅列出输入中提及或隐含的风险，不要编造。格式: [类别] 风险描述",
                text
            )
            if llm_risk:
                risks["_llm增强"] = llm_risk
        return risks

    def _check_red_line(self, text: str, keywords: list[str]) -> str:
        """检查红线"""
        matched = [kw for kw in keywords if kw in text]
        if matched:
            return f"⚠️ 检测到红线词: {'、'.join(matched)}"
        return "✅ 未检测到明显红线"

    def _assess_reputation_risk(self, text: str) -> str:
        """评估声誉风险"""
        high = ["欺骗", "撒谎", "造假", "背信", "失信"]
        medium = ["拒绝", "放弃", "退出", "离开"]
        if any(kw in text for kw in high):
            return "⚠️ 高声誉风险"
        if any(kw in text for kw in medium):
            return "⚡ 中度声誉风险"
        return "✅ 声誉风险可控"

    def _assess_economic_risk(self, text: str) -> str:
        """评估经济风险"""
        high = ["负债", "贷款", "借款", "抵押", "倾家荡产"]
        medium = ["降薪", "减薪", "扣钱", "罚款", "亏损"]
        if any(kw in text for kw in high):
            return "⚠️ 高经济风险"
        if any(kw in text for kw in medium):
            return "⚡ 中度经济风险"
        return "✅ 经济风险可控"

    def _assess_opportunity_cost(self, text: str) -> str:
        """评估机会成本"""
        if any(kw in text for kw in ["可惜", "放弃", "错过", "其他选择", "备选"]):
            return "⚡ 存在显著机会成本，需权衡"
        return "信息不足以评估机会成本"

    # ========== 步骤4: 公理冲突检查 ==========

    def _check_conflicts(self, text: str, game_map: dict) -> dict:
        """公理冲突检查"""
        conflicts = []
        active = [a for a in self._axioms if a.active]

        triggered = []
        for axiom in active:
            if any(indicator in text for indicator in axiom.scope_indicators) or \
               any(kw in str(game_map) for kw in axiom.scope_indicators):
                triggered.append(axiom)

        for i, a in enumerate(triggered):
            for b in triggered[i+1:]:
                if a.layer != b.layer:
                    winner, loser = (a, b) if a.layer < b.layer else (b, a)
                    record = ConflictRecord(
                        axiom_a=a.id, axiom_b=b.id,
                        layer_a=a.layer, layer_b=b.layer,
                        conclusion_a=f"公理 {a.id} 指向: {a.text[:30]}...",
                        conclusion_b=f"公理 {b.id} 指向: {b.text[:30]}...",
                        verdict=f"层级优先: L{a.layer} > L{b.layer}, 采用 {winner.id}",
                        confidence="高" if winner.layer == 1 else "中",
                        note=f"冲突涉及 {a.id}(L{a.layer}) 和 {b.id}(L{b.layer})。"
                             f"当 {a.id} 的适用范围与 {b.id} 冲突时，{winner.id} 优先级更高。"
                             f"但如果用户处于自我认知场景(L3覆盖范围)，L3可能更相关，需自行判断。"
                    )
                    conflicts.append(record)
                else:
                    conflicts.append(ConflictRecord(
                        axiom_a=a.id, axiom_b=b.id,
                        layer_a=a.layer, layer_b=b.layer,
                        conclusion_a=a.text[:30],
                        conclusion_b=b.text[:30],
                        verdict=f"同层级冲突: L{a.layer}。场景匹配度决定。{a.id}适用面更窄 => 优先",
                        confidence="中",
                        note="同层级公理冲突需要更多上下文信息才能裁决。建议向用户追问具体情况。"
                    ))

        conflict_dicts = []
        for c in conflicts:
            conflict_dicts.append({
                "公理A": c.axiom_a, "公理B": c.axiom_b,
                "层级A": f"L{c.layer_a}", "层级B": f"L{c.layer_b}",
                "结论A": c.conclusion_a, "结论B": c.conclusion_b,
                "裁决": c.verdict,
                "置信度": c.confidence,
                "说明": c.note,
            })

        triggered_ids = [a.id for a in triggered]
        return {
            "活跃公理数": len(triggered),
            "活跃公理列表": triggered_ids,
            "冲突数": len(conflicts),
            "冲突列表": conflict_dicts,
        }

    # ========== 步骤5: 生成行动指令与预测 ==========

    def _generate_actions_and_predictions(self, text: str, analysis: dict) -> tuple:
        """生成行动指令和可验证预测"""
        actions = []
        predictions = []
        risks = analysis.get("风险计算", {})

        # 基于风险状态生成行动建议
        risk_values = [str(v) for v in risks.values() if not v.startswith("_")]
        if any("⚠️" in r for r in risk_values):
            actions.append("【优先】处理已标记的高风险项，在风险可控前暂缓重大决策")

        if any("经济" in str(risks.get("经济成本", "")) for _ in [1]):
            actions.append("进行详细的财务测算，量化收益和成本后再做决策")

        legal = str(risks.get("法律红线", ""))
        if "⚠️" in legal:
            actions.append("【必做】咨询法律专业人士，明确法律风险边界")

        # LM增强
        if self._client:
            llm_actions = self._llm_call(
                "基于以下分析结果，生成3条具体可执行的操作建议。"
                "格式: 每行一条，以序号开头。具体、有时限、可衡量。",
                f"文本: {text}\n博弈地图: {analysis.get('博弈地图', {})}\n风险: {risks}"
            )
            if llm_actions:
                for line in llm_actions.strip().split("\n"):
                    line = line.strip()
                    if line and any(c.isdigit() for c in line[:4]):
                        actions.append(line)

            llm_pred = self._llm_call(
                "基于输入场景，生成1-2条在未来6个月内可验证的具体预测。"
                "格式: [预测] + 预测内容 + [置信度: 高/中/低]",
                text
            )
            if llm_pred:
                predictions.append({
                    "text": llm_pred[:200],
                    "置信度": "中",
                    "_来源": "LLM增强",
                })

        if not actions:
            actions.append("收集更多信息后再决策，不要在不充分信息下做不可逆的选择")
            actions.append("列出至少3个备选方案，分别评估优劣")

        if not predictions:
            predictions.append({"text": "暂无足够信息生成可验证预测", "置信度": "低", "_来源": "规则引擎"})

        return actions, predictions

    # ========== 辅助方法 ==========

    def _match_rules(self, text: str) -> list[dict]:
        """匹配输入文本触发的实战规则"""
        matched = []
        for rule in self._rules:
            rule_text = rule.get("text", "")
            rule_id = rule.get("id", "")
            triggers = {
                1: ["事实", "观点"],
                4: ["受益", "好处", "动机"],
                7: ["来源", "可靠", "渠道"],
                9: ["确认", "验证", "证明"],
                10: ["导致", "因为", "所以", "原因", "结果"],
                13: ["成本", "收益", "代价"],
                14: ["最坏", "万一", "如果"],
                16: ["已经投入", "白费", "放弃可惜"],
                18: ["投入", "坚持", "继续"],
            }
            matched_keywords = triggers.get(rule_id, [])
            if matched_keywords and any(kw in text for kw in matched_keywords):
                matched.append({"编号": f"规则{rule_id}", "内容": rule_text})
        return matched

    def _annotate_confidence(self, result: dict) -> str:
        """整体置信度标注"""
        risks = [str(v) for v in result.get("风险计算", {}).values() if not str(v).startswith("_")]
        has_warning = any("⚠️" in r for r in risks)
        conflicts = result.get("公理冲突检查", {}).get("冲突数", 0)
        game_map = result.get("博弈地图", {})

        info_sufficient = any(
            len(v) > 0 for k, v in game_map.items()
            if isinstance(v, list) and not k.startswith("_")
        )

        if info_sufficient and not has_warning and conflicts == 0:
            return "高"
        elif info_sufficient and not has_warning:
            return "中"
        return "低"
