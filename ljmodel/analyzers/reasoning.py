"""推理引擎 — 多模型逻辑求解"""

import re

from ..knowledge_base import KNOWLEDGE_BASE


class ReasoningEngine:
    """
    多模型推理求解器

    基于九本书的知识，对逻辑问题进行形式化求解：
    - 三段论验证
    - 演绎推理链
    - 溯因推理
    - 辩证分析
    """

    def __init__(self):
        self.kb = KNOWLEDGE_BASE

    def syllogism_check(self, major: str, minor: str, conclusion: str) -> dict:
        """验证三段论有效性

        Args:
            major: 大前提 (如 "所有人都会死")
            minor: 小前提 (如 "苏格拉底是人")
            conclusion: 结论 (如 "苏格拉底会死")

        Returns:
            dict: 验证结果
        """
        result = {
            "大前提": major,
            "小前提": minor,
            "结论": conclusion,
            "有效": False,
            "分析": []
        }

        m_terms = set(self._extract_terms(major))
        n_terms = set(self._extract_terms(minor))
        c_terms = set(self._extract_terms(conclusion))

        middle = m_terms & n_terms
        if not middle:
            result["分析"].append("无中项 — 三段论无效")

        major_term = m_terms - middle
        minor_term = n_terms - middle

        if major_term & c_terms and minor_term & c_terms:
            result["有效"] = True
            result["分析"].append("三段论有效：结论由前提必然推出")
        else:
            result["分析"].append("三段论无效：结论中的项不在前提中")

        return result

    def _extract_terms(self, sentence: str) -> set:
        """简单提取句子中的关键词作为项"""
        stopwords = {"所有", "有的", "是", "不是", "都", "会", "不会", "的", "了", "在",
                     "如果", "那么", "就", "因为", "所以", "因此", "而且", "或者"}
        words = re.findall(r'[\w一-鿿]+', sentence)
        return set(w for w in words if w not in stopwords)

    def logical_deduce(self, premises: list, conclusion: str) -> dict:
        """检验演绎推理"""
        result = {
            "前提": premises,
            "结论": conclusion,
            "演绎有效": False,
            "说明": ""
        }

        for i, p in enumerate(premises):
            if "如果" in p and "那么" in p:
                for j, q in enumerate(premises):
                    if i != j and ("是" in q or "成立" in q or "真" in q):
                        if conclusion in premises:
                            result["演绎有效"] = True
                            result["说明"] = "肯定前件式(Modus Ponens): 如果P则Q, P, 所以Q"

                if "并非" in conclusion or "不" in conclusion:
                    result["演绎有效"] = True
                    result["说明"] = "否定后件式(Modus Tollens): 如果P则Q, 非Q, 所以非P"

        if not result["演绎有效"]:
            result["说明"] = "未识别出标准演绎形式，需进一步分析"

        return result

    def analyze_causal(self, claim: str) -> dict:
        """因果分析 — 基于源思维+麦肯锡"""
        result = {
            "原因": [],
            "结果": [],
            "关键变量": None,
            "替代解释": ["反向因果", "第三方变量", "纯属巧合"]
        }

        if "因为" in claim and "所以" in claim:
            parts = claim.split("所以")
            result["原因"].append(parts[0].replace("因为", "").strip())
            result["结果"].append(parts[1].strip())
        elif "导致" in claim:
            parts = claim.split("导致")
            result["原因"].append(parts[0].strip())
            result["结果"].append(parts[1].strip())

        if result["原因"]:
            result["关键变量"] = f"在 {result['原因'][0]} 中寻找关键X"

        return result

    def tree_decompose(self, problem: str) -> dict:
        """逻辑树分解 — MECE"""
        return {
            "问题": problem,
            "分解维度": ["按要素分解", "按流程分解", "按层次分解"],
            "建议": "使用议题树将问题分解为MECE的子问题"
        }
