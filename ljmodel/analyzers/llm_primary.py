"""LLM主分析引擎 — 使用9本书框架进行综合分析"""

import json
import re


def build_llm_primary_prompt(kb: dict) -> str:
    """从9本书的知识库构建LLM主分析提示词"""
    prompt = """你是一位精通逻辑与批判性思维的资深分析专家，整合了以下9本经典著作的核心框架。
请用这9个维度对用户输入的文本进行全面分析，输出结构化的中文分析报告。

## 你掌握的分析框架

"""
    for key, book in [
        ("formal_logic", "1. 形式逻辑分析 — 逻辑学十五讲"),
        ("critical_inquiry", "2. 批判性质询 — 学会提问"),
        ("dual_system", "3. 认知偏见检测 — 思考,快与慢"),
        ("simple_logic", "4. 简单逻辑分析 — 简单的逻辑学"),
        ("argumentation_rules", "5. 论证规则评估 — 论证是一门学问"),
        ("critical_thinking_tools", "6. 思维元素分析 — 批判性思维工具"),
        ("mckinsey_logic", "7. 结构化分析 — 麦肯锡逻辑思维"),
        ("dialectical_system", "8. 辩证系统分析 — 世界的逻辑"),
        ("source_thinking", "9. 源思维深度分析 — 源思维"),
    ]:
        prompt += f"\n### {book}\n"
        data = kb.get(key, {})
        if isinstance(data, dict):
            for sub_key, sub_val in data.items():
                if sub_key in ("source", "description"):
                    continue
                if isinstance(sub_val, list):
                    prompt += f"- {sub_key}: {'; '.join(str(s)[:120] for s in sub_val[:5])}\n"
                elif isinstance(sub_val, dict):
                    desc = sub_val.get("description", "")
                    if desc:
                        prompt += f"- {sub_key}: {str(desc)[:200]}\n"
                    else:
                        prompt += f"- {sub_key}: (含{sub_key}分析框架)\n"

    prompt += """

## 输出格式要求

请严格按照以下JSON格式输出（不要包含markdown代码块标记，直接输出纯JSON）：

```json
{
  "综合评分": {
    "分数": <0-100的整数>,
    "评价": "<一句话概括论证质量>"
  },
  "维度分析": {
    "形式逻辑": {
      "分析": "<基于逻辑学十五讲的分析结论>",
      "问题": ["<具体问题1>", "<具体问题2>"]
    },
    "批判性质询": {
      "分析": "<基于学会提问的分析：论题、结论、理由、假设、证据质量等>",
      "问题": ["<问题1>", "<问题2>"]
    },
    "认知偏见": {
      "分析": "<基于思考快与慢的分析：系统1/2激活状态、认知偏见、前景理论特征>",
      "问题": ["<问题1>"]
    },
    "论证规则": {
      "分析": "<基于论证是一门学问的规则检查>",
      "问题": ["<问题1>"]
    },
    "思维元素": {
      "分析": "<基于批判性思维工具的8元素分析>",
      "问题": ["<问题1>"]
    },
    "结构化": {
      "分析": "<基于麦肯锡的结构化分析：MECE、金字塔、逻辑树>",
      "问题": ["<问题1>"]
    },
    "辩证系统": {
      "分析": "<基于世界的逻辑的辩证系统分析>",
      "问题": ["<问题1>"]
    },
    "源思维": {
      "分析": "<基于源思维的深度分析：现象/事实/本质分层、多元因果、关键变量>",
      "问题": ["<问题1>"]
    }
  },
  "主要发现": ["<最重要的3-5条发现>"],
  "警告": ["<需要警惕的逻辑问题，若无则填[]>"],
  "行动建议": ["<改进建议1>", "<改进建议2>", "<改进建议3>"]
}
```

注意：如果某个维度不适用或没有问题，问题列表可以为空。警告必须有实质内容才列。
分数计算规则：90+为可靠论证，70-89为基本可靠，50-69存在明显问题，50以下为薄弱。
"""
    return prompt


def analyze_llm_primary(text: str, kb: dict, client, model: str) -> dict:
    """LLM作为主分析引擎，使用9本书框架进行综合分析"""
    if not client:
        return {}
    try:
        system_prompt = build_llm_primary_prompt(kb)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "综合评分": {"分数": 0, "评价": "LLM分析失败"}}
