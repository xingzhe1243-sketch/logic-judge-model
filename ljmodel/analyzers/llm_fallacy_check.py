"""LLM 自检引擎 — 对 LLM 主分析输出进行逻辑谬误二次审查"""

import json
import re


def analyze_llm_fallacy_check(
    text: str,
    llm_primary_output: dict,
    client,
    model: str,
) -> dict:
    """对 LLM 主分析的输出进行二次谬误审查

    要求 LLM 以批判性视角审视自己刚刚生成的分析，
    精确定位其中可能存在的逻辑谬误、草率论断、概念混淆等问题。

    Args:
        text: 用户输入的原始文本
        llm_primary_output: LLM 主分析的 JSON 结果
        client: OpenAI 兼容客户端
        model: 模型名

    Returns:
        包含自检谬误列表的 dict
    """
    if not client or not llm_primary_output:
        return {}

    llm_analysis_json = json.dumps(llm_primary_output, ensure_ascii=False, indent=2)

    system_prompt = """你是一位极其严苛的逻辑谬误审查官。你的任务是：
对一份由 AI 生成的逻辑分析报告进行「二次审查」，找出该报告本身存在的逻辑问题。

## 审查原则

1. **逐句检视** — 仔细阅读报告中的每个维度分析，不放过任何可疑论断
2. **严谨细致** — 必须精确引用原文，不能笼统概括，要具体到哪个词/哪句话有问题
3. **实事求是** — 确实没有问题就说没有问题，不要为了找问题而编造
4. **分类明确** — 区分形式谬误（推理结构错误）和非形式谬误（歧义、假设、关联）

## 你要检查的谬误类型（包括但不限于）

- **偷换概念/混淆定义**: 同一个词在不同语境下含义不一致
- **循环论证**: 结论被用作前提
- **虚假二分/非黑即白**: 忽略中间选项
- **草率概括**: 从不足够的证据推出一般性结论
- **滑坡谬误**: 未提供充分证据就断言连锁反应
- **诉诸权威/情感/大众**: 用非逻辑因素代替论证
- **虚假因果**: 把相关性当作因果性
- **歧义模糊**: 关键概念缺乏清晰定义
- **不当类比**: 类比对象之间缺乏实质相似性
- **预期理由**: 以尚未证明的命题作为论据
- **以全概偏/以偏概全**: 不当推广或不当限制
- **自相矛盾**: 报告中前后陈述不一致
- **过度自信**: 在证据不足时给出确定结论
- **稻草人**: 歪曲或简化原始文本的观点再进行批判

## 输出格式

严格按以下 JSON 格式输出，直接输出纯 JSON，不要代码块标记：

{
  "自检结果": [
    {
      "引用原文": "报告中具体有问题的语句，精确到原句",
      "所属维度": "形式逻辑/认知偏见/源思维/综合评分/...",
      "谬误类型": "如'草率概括'",
      "问题说明": "为什么这是逻辑问题，推理链条哪里断了",
      "严重程度": "高/中/低",
      "修正建议": "如何改进这条分析"
    }
  ],
  "整体评估": {
    "总谬误数": 3,
    "主要风险": "该分析在哪些方面最需要警惕",
    "可信度": "高/中/低",
    "总体评价": "对这份分析报告本身的评价"
  }
}

如果完全没有发现逻辑问题，"自检结果"返回空列表 []，"整体评估"中说明分析质量良好。
"""

    user_prompt = f"""## 原始用户输入文本

{text}

## LLM 主分析生成的报告

{llm_analysis_json}

请严格审查上述 AI 分析报告，找出其中存在的逻辑谬误和推理问题。
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "自检结果": [], "整体评估": {"总谬误数": 0, "主要风险": f"自检过程异常: {e}", "可信度": "未知"}}
