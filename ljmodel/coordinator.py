"""智囊团协调器 — 跨专家综合分析

智囊团架构:
  Tier 1 - 各专家独立分析（9本逻辑经典 + 知乎专家 + LLM）
  Tier 2 - 协调器综合（本模块）：识别共识/矛盾/缺口，生成多视角评估
  Tier 3 - 输出（加权结论 + 行动建议）
"""

import re
from typing import Any

# 专家分组 — 用于多视角分类
EXPERT_GROUPS = {
    "逻辑与推理": ["formal_logic", "simple_logic", "argumentation"],
    "批判与认知": ["critical_inquiry", "bias_detection", "elements_of_thought"],
    "结构与系统": ["structured_analysis", "dialectical"],
    "深度思维": ["source_thinking"],
    "真实世界经验": ["zhihu_expert"],
    "LLM综合分析": ["llm_primary"],
}

GROUP_LABELS = {
    "formal_logic": "形式逻辑",
    "simple_logic": "简明逻辑",
    "argumentation": "论证规则",
    "critical_inquiry": "批判性质询",
    "bias_detection": "认知偏见",
    "elements_of_thought": "思维元素",
    "structured_analysis": "结构化分析",
    "dialectical": "辩证系统",
    "source_thinking": "源思维",
    "zhihu_expert": "知乎专家",
    "llm_primary": "LLM综合",
}


def _extract_findings(modules: dict, module_key: str) -> list[dict]:
    """Extract structured findings from a module's output."""
    findings = []
    data = modules.get(module_key, {})
    if not data or "error" in data:
        return findings

    label = GROUP_LABELS.get(module_key, module_key)

    # Logic modules: look for 谬误检测, 警告, 问题检测 etc
    for section_key in ["谬误检测", "警告", "认知偏见检测", "问题列表", "思维模式诊断"]:
        items = data.get(section_key, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    desc = item.get("description", item.get("keyword", item.get("bias", "")))
                    findings.append({"source": label, "type": "problem", "text": desc})
                elif isinstance(item, str):
                    findings.append({"source": label, "type": "note", "text": item})

    # Zhihu expert: insights
    if module_key == "zhihu_expert" and data.get("洞见"):
        for ins in data["洞见"][:5]:
            findings.append({"source": label, "type": "empirical", "text": ins[:200]})
        if data.get("领域分布"):
            domains = [d["domain"] for d in data["领域分布"]]
            findings.append({"source": label, "type": "note", "text": f"涉及领域: {', '.join(domains)}"})

    return findings


def _extract_key_topics(text: str) -> list[str]:
    """Extract key topics from input text for cross-referencing."""
    topics = []
    # Extract phrases in quotes (both ASCII and Chinese)
    for match in re.findall(r'["""“”]([^""""“”]{2,30})["""“”]', text):
        topics.append(match)
    # Extract phrases after "关于", "对于", "针对"
    for match in re.findall(r'(?:关于|对于|针对)(\S{2,20})', text):
        topics.append(match)
    return list(set(topics))


def _find_contradictions(findings: list[dict]) -> list[str]:
    """Identify potential contradictions across expert findings."""
    contradictions = []
    # Look for positive vs negative assessments of same topic
    positive_patterns = ["合理", "正确", "有效", "可靠", "充分"]
    negative_patterns = ["谬误", "偏见", "错误", "缺陷", "不足", "问题", "风险"]

    positive_findings = []
    negative_findings = []

    for f in findings:
        text = f["text"]
        if any(p in text for p in positive_patterns):
            positive_findings.append(f)
        if any(n in text for n in negative_patterns):
            negative_findings.append(f)

    # If we have both positive and negative about the same topic
    for pf in positive_findings:
        for nf in negative_findings:
            if pf["source"] != nf["source"]:
                contradictions.append(
                    f"[潜在分歧] {pf['source']} 持正面评估 vs {nf['source']} 指出问题 — "
                    f"需综合判断哪方依据更充分"
                )
                break

    return contradictions


def _find_consensus(findings: list[dict], threshold: int = 2) -> list[str]:
    """Identify consensus points across multiple experts."""
    from collections import Counter
    # Group findings by type
    problems = [f for f in findings if f["type"] == "problem"]
    # If same type of problem noted by multiple experts
    source_count = Counter(f["source"] for f in problems)
    consensus_areas = []
    for source, count in source_count.most_common(3):
        if count >= threshold:
            relevant = [f for f in problems if f["source"] == source]
            examples = [f["text"][:100] for f in relevant[:2]]
            consensus_areas.append(
                f"[多专家共识] {source} 被 {count} 次提及 — {'; '.join(examples)}"
            )
    return consensus_areas


def _identify_gaps(findings: list[dict], topics: list[str]) -> list[str]:
    """Identify perspectives that might be missing."""
    gaps = []
    all_sources = set(f["source"] for f in findings)
    # Which groups didn't contribute?
    for group_name, module_keys in EXPERT_GROUPS.items():
        if not any(GROUP_LABELS.get(k, k) in all_sources for k in module_keys):
            gaps.append(f"[视角缺口] {group_name} 未参与分析 — 可能遗漏相关洞见")

    # Check if empirical perspective is missing
    if not any(f["type"] == "empirical" for f in findings):
        gaps.append("[视角缺口] 缺少真实世界经验视角 — 建议结合知乎等经验数据验证")

    return gaps


def coordinate(modules: dict, input_text: str = "") -> dict:
    """Run think tank coordination across all expert modules.

    Args:
        modules: All module outputs from the analysis pipeline
        input_text: Original input text for context extraction

    Returns:
        Coordination report with consensus, contradictions, gaps, and priority assessment
    """
    # Gather all findings
    all_findings = []
    for module_key in modules:
        all_findings.extend(_extract_findings(modules, module_key))

    # Extract key topics
    topics = _extract_key_topics(input_text)

    # Cross-expert analysis
    consensus = _find_consensus(all_findings, threshold=2)
    contradictions = _find_contradictions(all_findings)
    gaps = _identify_gaps(all_findings, topics)

    # Expert group activity summary
    group_activity = {}
    for group_name, module_keys in EXPERT_GROUPS.items():
        active = [k for k in module_keys if k in modules and modules.get(k) and "error" not in modules.get(k, {})]
        if active:
            group_activity[group_name] = {
                "active": True,
                "modules": [GROUP_LABELS.get(m, m) for m in active],
            }
        else:
            group_activity[group_name] = {"active": False, "modules": []}

    # Priority assessment: which expert is most relevant for this text
    zhihu_relevant = any(
        f["source"] == "知乎专家" for f in all_findings
    )
    logic_relevant = any(
        f["source"] in ("形式逻辑", "简明逻辑", "论证规则") for f in all_findings
    )

    relevance_profile = {
        "逻辑与推理": "高" if logic_relevant else "中",
        "批判与认知": "高",
        "真实世界经验": "高" if zhihu_relevant else "低",
        "深度思维": "中",
        "结构与系统": "中",
    }

    return {
        "协调状态": "完成 — 跨专家综合分析已生成",
        "活跃专家数": len(set(f["source"] for f in all_findings)),
        "总发现数": len(all_findings),
        "专家分组活跃度": group_activity,
        "专家相关性评估": relevance_profile,
        "共识点": consensus,
        "潜在分歧": contradictions,
        "视角缺口": gaps,
        "关键主题": topics,
    }
