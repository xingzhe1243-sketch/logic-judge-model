"""规则解剖模型 V4.0 — 共鸣拓扑引擎（模式B）

6条公理（LLM适配版），3套操作协议，痛苦分类系统。
为方向迷茫、过度分析、痛苦分类提供结构化导航。
"""

import re
from typing import Optional

from .logger import logger


class ResonanceEngine:
    """共鸣拓扑学 V1.0 (LLM适配版)"""

    def __init__(self, kb: dict):
        self._kb = kb
        self._axioms: list[dict] = []
        self._protocols: dict = {}
        self._init_from_kb()
        self._init_llm()

    def _init_from_kb(self):
        """从知识库加载公理和协议"""
        dk = self._kb.get("dissection_model", {})
        mode_b = dk.get("mode_b", {})
        self._axioms = mode_b.get("axioms", [])
        self._protocols = mode_b.get("protocols", {})

    def _init_llm(self):
        """惰性初始化 LLM 客户端"""
        self._client = None
        self._model = None
        try:
            import os
            from .config import CONFIG
            api_key = CONFIG.get("api_key") or os.environ.get("DEEPSEEK_API_KEY", "")
            if api_key:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=api_key,
                    base_url=CONFIG.get("base_url", "https://api.deepseek.com/v1")
                )
                self._model = CONFIG.get("model", "deepseek-chat")
        except Exception as e:
            logger.debug(f"共鸣拓扑 LLM 初始化跳过: {e}")

    def _llm_call(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM 进行增强分析"""
        if not self._client:
            return ""
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=1000,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"共鸣拓扑 LLM 调用异常: {e}")
            return ""

    def analyze(self, text: str) -> dict:
        """对输入文本执行共鸣拓扑分析"""
        result = {
            "模式": "B — 共鸣拓扑",
            "模式判定": self._detect_mode(text),
        }
        result["痛苦分类"] = self._classify_pain(text)
        result["感知扫描"] = self._build_perception_scan(text)
        result["场域检查"] = self._check_field(text)
        result["梯子检查"] = self._check_ladder(text)
        result["入场协议"] = self._build_entry_protocol(text)
        result["检查点"] = "3轮对话后询问是否需要切换模式"
        return result

    # ========== 模式判定 ==========

    def _detect_mode(self, text: str) -> dict:
        """检测是否应使用模式B"""
        b_signals = [
            "迷茫", "不知道", "没感觉", "累了", "焦虑",
            "写不出来", "没意义", "赢了也不开心", "困惑",
            "找不到方向", "下一步", "空虚", "疲惫",
        ]
        score = sum(1 for s in b_signals if s in text)
        if score >= 3:
            return {"依据": f"检测到 {score} 个强信号，模式B高度适用", "置信度": "高", "信号强度": score}
        elif score >= 1:
            return {"依据": f"检测到 {score} 个信号，建议模式B", "置信度": "中", "信号强度": score}
        return {"依据": "检测到少量模式B信号", "置信度": "低", "信号强度": score}

    # ========== 步骤1: 痛苦分类 ==========

    def _classify_pain(self, text: str) -> dict:
        """公理IV: 痛苦分类 — 循环痛苦 vs 蜕变痛苦"""
        cyclic_signals = ["又", "再次", "总是", "每次", "还是", "老样子", "重复"]
        is_cyclic = any(s in text for s in cyclic_signals)

        # 检测具体描述
        has_detail = len(text) > 30
        has_emotion = any(e in text for e in ["难受", "痛苦", "烦", "累", "焦虑", "不安"])

        if is_cyclic:
            pain_type = "循环痛苦"
            status = "新旧指数: 3-7分 — 部分重复但本质不同（建议进一步追问）"
            action = "建议: 切换至模式A进行结构性分析"
        elif has_detail and has_emotion:
            pain_type = "蜕变痛苦"
            status = "新旧指数: 8-10分 — 全新体验或重大转折"
            action = "操作: 不分析, 不防御, 只观察"
        else:
            pain_type = "待分类"
            status = "信息不足以判断。建议追问: '这个问题你遇到过类似的吗？几次？'"
            action = "按1-10打分新旧指数后决定模式"

        if self._client and is_cyclic:
            llm_insight = self._llm_call(
                "识别用户描述的痛苦是否为重复模式。如果是，简要概括这个模式。"
                "不要给建议，只描述模式。",
                text
            )
            if llm_insight:
                status += f"\n  模式识别: {llm_insight[:150]}"

        return {
            "类型": pain_type,
            "状态": status,
            "建议操作": action,
        }

    # ========== 步骤2: 感知扫描 ==========

    def _build_perception_scan(self, text: str) -> list[str]:
        """公理II+III: 感知扫描引导"""
        prompts = [
            "请描述: 你现在身体的哪个部位最紧？",
            "不要分析，先感受。专注呼吸15秒。",
        ]

        # 检测纯逻辑无感受型输入
        logic_only = any(w in text for w in ["分析", "逻辑", "理性", "利弊", "权衡"])
        emotion_present = any(e in text for e in ["感受", "感觉", "心里", "身体"])
        if logic_only and not emotion_present:
            prompts.append("你用了很多分析性语言。尝试关掉'分析模式'，用一句话描述你此刻的身体感受。")
            prompts.append("如果非要用逻辑: 你的逻辑分析让你更靠近了答案还是更焦虑了？")

        return prompts

    # ========== 步骤3: 场域检查 ==========

    def _check_field(self, text: str) -> list[str]:
        """公理I: 场域检查"""
        questions = [
            "你现在站在什么场上？—— 这个问题涉及什么游戏？",
        ]

        if any(w in text for w in ["只能", "没得选", "必须", "不得不"]):
            questions.append("这张桌子可以退吗？—— 是否有退出选项？")
        if any(w in text for w in ["他们都", "所有人都", "大家都是"]):
            questions.append("列出你此刻看不到的第三条路。")

        return questions

    # ========== 步骤4: 梯子检查 ==========

    def _check_ladder(self, text: str) -> dict:
        """公理V: 梯子检查 + 关闭条件评估"""
        conditions_met = []

        if any(w in text for w in ["方案", "怎么办", "方法", "步骤"]):
            conditions_met.append("用户要求具体方案 → 建议切换至模式A")
        if any(w in text for w in ["开心", "平静", "好了", "明白了"]):
            conditions_met.append("用户情绪良好 → 可结束分析，转为纯聊天")
        if any(w in text for w in ["行动", "做了", "动手"]):
            conditions_met.append("用户已进入行动阶段 → 降级为监听")

        if not conditions_met:
            conditions_met.append("无关闭条件触发 → 继续当前模式")

        return {
            "检查": "这段对话让你更靠近你的感受，还是把它推远了？",
            "关闭条件": conditions_met,
        }

    # ========== 入场协议 ==========

    def _build_entry_protocol(self, text: str) -> dict:
        """入场校准协议"""
        return {
            "需求分类": "请确认: 你现在需要的是分析（看清局面）还是导航（找到方向）？" if "?" not in text[-5:] else "继续当前模式",
            "协议说明": "每5轮对话会插入检查点，确认是否需要切换模式",
        }
