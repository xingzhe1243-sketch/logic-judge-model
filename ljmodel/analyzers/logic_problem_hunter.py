"""逻辑问题猎手 — 独立 LLM 调用，基于原始文本+全部分析结果，
精确定位潜在逻辑谬误，给出明确修正。"""

import json
import re


def analyze_logic_problems(text: str, full_result: dict, client, model: str) -> dict:
    """独立 LLM 调用，全方位搜寻文本中的逻辑问题

    与 llm_primary 不同：
    - 这是一次**全新的、独立的** LLM 调用，不继承任何之前的对话上下文
    - 输入包括原始文本 + 全部已有分析结果（LLM主分析 + 规则引擎）
    - 但不会被已有分析带偏，以「局外人」视角独立判断
    - 输出：精确定位 + 谬误命名 + 严谨说明 + 具体修正

    Args:
        text: 原始输入文本
        full_result: 完整的分析结果 dict (包含 input, modules, synthesis)
        client: OpenAI 兼容客户端
        model: 模型名

    Returns:
        {
            "问题列表": [
                {
                    "原文引用": "...",
                    "起始位置": 12,
                    "结束位置": 28,
                    "问题类型": "推不出/循环论证/偷换概念/...",
                    "严重程度": "高/中/低",
                    "问题说明": "...",
                    "修正建议": "..."
                }
            ],
            "整体评估": {
                "问题总数": 3,
                "最严重问题": "...",
                "论证稳健性": "高/中/低"
            }
        }
    """
    if not client:
        return {}

    # 收集已有分析摘要，供 LLM 参考但不盲从
    existing_summary = _build_existing_summary(full_result)
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(text, existing_summary)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw)
    except Exception as e:
        return {
            "error": str(e),
            "问题列表": [],
            "整体评估": {"问题总数": 0, "最严重问题": f"分析异常: {e}", "论证稳健性": "未知"},
        }


def _build_existing_summary(full_result: dict) -> str:
    """从完整结果中构建已有分析摘要，供 LLM 参考"""
    parts = []

    # LLM 主分析摘要
    llm = full_result.get("modules", {}).get("llm_primary", {})
    if llm and "error" not in llm:
        score = llm.get("综合评分", {})
        parts.append(f"【LLM主分析】评分: {score.get('分数', '?')}/100 — {score.get('评价', '?')}")
        findings = llm.get("主要发现", [])
        if findings:
            parts.append(f"  主要发现: {'; '.join(findings[:3])}")
        warns = llm.get("警告", [])
        if warns:
            parts.append(f"  警告: {'; '.join(warns[:3])}")

    # 合成摘要
    syn = full_result.get("synthesis", {})
    if syn:
        parts.append(f"【综合合成】评分: {syn.get('逻辑质量评分', '?')}")
        syn_warns = syn.get("警告", [])
        if syn_warns:
            parts.append(f"  警告: {'; '.join(syn_warns[:3])}")

    # 规则引擎谬误检测汇总
    rule_fallacies = []
    for mod_name in ["formal_logic", "simple_logic", "argumentation", "critical_inquiry"]:
        mod = full_result.get("modules", {}).get(mod_name, {})
        for item in mod.get("谬误检测", []):
            if isinstance(item, dict):
                rule_fallacies.append(f"[{mod_name}] {item.get('keyword', '')}: {item.get('description', '')}")
            elif isinstance(item, str):
                rule_fallacies.append(f"[{mod_name}] {item}")
    if rule_fallacies:
        parts.append(f"【规则引擎谬误】{'; '.join(rule_fallacies[:5])}")

    return "\n".join(parts) if parts else "（无已有分析结果）"


def _build_system_prompt() -> str:
    from ..fallacy_registry import build_llm_fallacy_taxonomy_prompt
    taxonomy = build_llm_fallacy_taxonomy_prompt()

    parts = [
        """你是一位独立于所有已有分析之外的「逻辑问题猎手」。

## 你的定位

你的判断**完全独立**于系统中其他任何分析模块。你不继承任何对话上下文，
你以「局外人」的身份重新审视原始文本。即使已有分析说"没有问题"，
你也要用自己的头脑重新判断。

## 你的任务

逐字逐句审查原始文本，找出其中**所有潜在的逻辑问题**，
对每个问题给出：
1. **精确引用** — 原文中哪句话/哪个词有问题（附字符偏移位置）
2. **问题类型** — 是什么逻辑谬误/缺陷
3. **严谨说明** — 为什么这是问题，推理链条在哪里断裂
4. **具体修正** — 应该怎么改才能消除这个逻辑问题

## 你须检查的问题类型（完整谬误分类体系，不限于此）
""",
        taxonomy,
        """

## 特别重点 — 需要你特别关注的两种关键谬误

### 1. 忽略限定谬误 (Secundum quid / a dicto simpliciter)
这是本系统其他模块**最容易漏掉**的谬误类型，你作为独立猎手必须特别关注。
它的本质是：前提中带有限定条件，结论中把这个限定条件**悄悄去掉**，当作无条件的一般命题。

经典模式：
- "正常X都Y，所以这个X Y" → X不一定是"正常"的，推不出
- "大多数X都Y，所以这个X Y" → 大多数≠所有，可能有反例

### 2. 以全概偏谬误 (Accident fallacy / dicto simpliciter)
与忽略限定相反，这是把一条**一般规则不加分辨地应用于一个特殊的子类**，忽略了该子类可能是例外。

经典模式：
- "X都Y，所以这个特殊子类Z(X的一种) Y" → Z可能是X中的例外
- 例如："鸟类会飞，所以企鹅会飞" → 企鹅是鸟但不会飞
- 例如："人都会死，所以塑料人也会死" → 塑料人不是生物学意义上的人
- 例如："人会走路，所以刚出生的婴儿也会走路" → 刚出生婴儿是人中的特例

你被特别训练来识别这两种模式。逐句扫描前提中的限定词（正常、通常、一般、大多数、所有、每个...），
同时留意一般规则被应用到可能例外的子类的情形。这是你的核心任务之一。

**论证结构问题**:
- 结论与前提无关
- 隐藏假设可疑
- 关键概念未定义
- 证据不足以支撑结论
- 自相矛盾/前后不一致
- 套套逻辑/空洞真陈述 (Tautology)

## 输出格式

严格按以下 JSON 格式输出，直接输出纯 JSON，不要代码块标记：

{
  "问题列表": [
    {
      "原文引用": "有问题的原句/原词",
      "起始位置": 0,
      "结束位置": 10,
      "问题类型": "推不出",
      "严重程度": "高",
      "问题说明": "前提'1+1=2'与结论'2+2=4'之间没有推理链条。前者是关于1的加法，后者是关于2的加法，需要用算术公理连接，而不是直接'所以'。",
      "修正建议": "应补全推理：1+1=2 ⇒ 两边同时乘以2 ⇒ 2+2=4；或者去掉'所以'，改为分别陈述两个独立事实。"
    }
  ],
  "整体评估": {
    "问题总数": 1,
    "最严重问题": "前提与结论无逻辑关联",
    "论证稳健性": "低",
    "总体判断": "（一段话总结原始文本的整体逻辑质量）"
  }
}

如果完全没有发现逻辑问题，"问题列表"返回空数组，"整体评估"中如实说明。
""",
    ]
    return "\n".join(parts)


def _build_user_prompt(text: str, existing_summary: str) -> str:
    return f"""## 原始文本

{text}

## 系统已有分析结果（供参考，但请独立判断）

{existing_summary}

---

请以「逻辑问题猎手」的身份，对上述原始文本进行独立的逻辑审查。
不要受已有分析结果的影响——你的价值就在于提供不一样的视角。
"""
