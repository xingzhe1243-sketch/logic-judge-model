"""综合合成 — 融合LLM主分析和规则引擎验证结果"""


def synthesize(result: dict) -> dict:
    """综合所有模块的分析结果，形成最终判断"""
    modules = result["modules"]
    synthesis = {
        "逻辑质量评分": "待评估",
        "主要发现": [],
        "警告": [],
        "行动建议": []
    }

    llm_primary = modules.get("llm_primary", {})

    # 主评分：优先使用LLM的评分
    if llm_primary.get("综合评分"):
        llm_score = llm_primary["综合评分"].get("分数", 0)
        llm_rating = llm_primary["综合评分"].get("评价", "")
        synthesis["逻辑质量评分"] = f"LLM评估: {llm_rating} (评分: {llm_score}/100)"
    else:
        synthesis["逻辑质量评分"] = "规则引擎评估 (LLM不可用)"

    # 主发现：来自LLM分析
    llm_findings = llm_primary.get("主要发现", [])
    if llm_findings:
        for f in llm_findings:
            synthesis["主要发现"].append(f"[LLM] {f}")

    llm_warns = llm_primary.get("警告", [])
    llm_suggestions = llm_primary.get("行动建议", [])

    # 辅助：规则引擎交叉验证
    rule_warns = []
    rule_findings = []

    # 辅助函数：处理单个逻辑问题猎手的结果
    def _process_hunter(module_key: str, label_prefix: str):
        """处理猎手模块的结果，追加到 rule_findings 和 synthesis 警告中"""
        nonlocal rule_findings, synthesis
        lph = modules.get(module_key, {})
        lph_items = lph.get("问题列表", [])
        if lph_items:
            seen = set()
            for item in lph_items:
                text_excerpt = item.get("原文引用", "")
                ptype = item.get("问题类型", "")
                desc = item.get("问题说明", "")
                severity = item.get("严重程度", "中")
                correction = item.get("修正建议", "")
                prefix = f"[{label_prefix}]" if severity == "低" else f"[{label_prefix}!]"
                label = f"【{ptype}】({severity})"
                warn_msg = f"{prefix} {label} {desc}"
                if correction:
                    warn_msg += f" | 修正: {correction}"
                rule_findings.append(warn_msg)
                if severity in ("高", "中"):
                    if warn_msg not in seen:
                        synthesis["警告"].append(f"{prefix} {label} {desc[:100]}...")
                        seen.add(warn_msg)
            overall = lph.get("整体评估", {})
            if overall.get("论证稳健性") == "低":
                synthesis["警告"].append(f"[{label_prefix}] 整体论证稳健性评估为「低」: {overall.get('总体判断', '')}")
        elif lph and "error" not in lph:
            rule_findings.append(f"[{label_prefix}] 经独立审查，未发现隐蔽逻辑问题")

    # 逻辑问题猎手1 — DeepSeek 独立审查
    _process_hunter("logic_problem_hunter_1", "问题猎手1")

    # 逻辑问题猎手2 — 豆包大模型独立审查（第二视角）
    _process_hunter("logic_problem_hunter_2", "问题猎手2")

    fl = modules.get("formal_logic", {})
    for f in fl.get("谬误检测", []):
        rule_warns.append(f"[规则验证] 检测到谬误 {f['keyword']}: {f['description']}")
    for item in fl.get("论证结构", []):
        if "不完整" in item or "混淆" in item:
            rule_findings.append(f"[规则验证] {item}")

    bd = modules.get("bias_detection", {})
    for b in bd.get("认知偏见检测", []):
        rule_warns.append(f"[规则验证] 可能受{b['bias']}影响")

    st = modules.get("source_thinking", {})
    for w in st.get("思维模式诊断", []):
        if "单一断定" in w or "风险" in w:
            rule_warns.append(f"[规则验证] {w}")

    ar = modules.get("argumentation", {})
    for item in ar.get("谬误检查", []):
        if "潜在谬误" in item:
            rule_warns.append(f"[规则验证] 论证规则-{item}")

    sl = modules.get("simple_logic", {})
    for item in sl.get("谬误检测", []):
        rule_warns.append(f"[规则验证] 谬误: {item['keyword']} — {item['description']}")
    for item in sl.get("非逻辑思维根源检测", []):
        rule_warns.append(f"[规则验证] 非逻辑根源: {item}")

    ci = modules.get("critical_inquiry", {})
    for item in ci.get("谬误检测", []):
        rule_warns.append(f"[规则验证] 批判性质询-谬误: {item}")

    dl = modules.get("dialectical", {})
    for item in dl.get("替代性思考", []):
        if "建议" in item:
            rule_findings.append(f"[规则验证] {item}")

    # 知乎专家 — 真实世界经验视角
    ze = modules.get("zhihu_expert", {})
    if ze.get("洞见"):
        rule_findings.append(f"[知乎专家] {ze['状态']}")
        # 加入最有价值的洞见
        for ins in ze["洞见"][:4]:
            rule_findings.append(f"[知乎洞见] {ins[:200]}")
        # 加入领域分布信息
        if ze.get("领域分布"):
            domains = [d["domain"] for d in ze["领域分布"]]
            rule_findings.append(f"[知乎领域] 相关内容涉及: {'、'.join(domains)}")

    # 合并：LLM主分析 + 规则验证
    seen_warns = set()
    for w in llm_warns:
        if w not in seen_warns:
            synthesis["警告"].append(w)
            seen_warns.add(w)
    for w in rule_warns:
        if w not in seen_warns:
            synthesis["警告"].append(w)
            seen_warns.add(w)

    if not synthesis["警告"]:
        synthesis["警告"] = ["未检测到严重的逻辑问题"]

    synthesis["主要发现"].extend(rule_findings)
    if not synthesis["主要发现"]:
        synthesis["主要发现"] = ["分析完成，建议参考各模块详细结果"]

    synthesis["行动建议"] = llm_suggestions if llm_suggestions else [
        "参考具体模块分析结果",
        "检查潜在假设是否合理",
        "寻找替代解释和反例",
        "补充更多可靠证据"
    ]
    if rule_findings or rule_warns:
        synthesis["行动建议"].append("注意规则引擎交叉验证的标记 — 这些是关键词级别的检测结果")

    if not llm_primary:
        score = 80
        score -= len(rule_warns) * 5
        if score < 20:
            score = 20
        if score >= 80:
            rating = "良好 — 论证基本可靠，但仍需注意细节"
        elif score >= 60:
            rating = "一般 — 论证存在可改进之处"
        elif score >= 40:
            rating = "待改进 — 存在明显的逻辑缺陷"
        else:
            rating = "薄弱 — 论证在根本上存在问题"
        synthesis["逻辑质量评分"] = f"{rating} (评分: {score}/100) (规则引擎模式)"

    return synthesis
