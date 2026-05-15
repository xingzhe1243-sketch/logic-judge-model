"""基于《思考,快与慢》的认知偏见检测"""


def analyze_biases(text: str, kb: dict) -> dict:
    """双系统认知偏见检测 + 前景理论 + 峰终定律"""
    analysis = {
        "系统激活状态": [],
        "认知放松/紧张检测": [],
        "认知偏见检测": [],
        "前景理论分析": [],
        "记忆自我特征": [],
        "判断建议": []
    }

    # 系统激活状态判断
    text_len = len(text)
    if text_len < 50:
        analysis["系统激活状态"].append("系统1快速判断模式 — 文本简短，可能基于直觉而非分析")
    elif text_len > 200:
        analysis["系统激活状态"].append("系统2分析模式 — 文本较长，适合深入逻辑分析")

    emotional_words = ["太", "非常", "极其", "绝对", "永远", "肯定", "受不了", "好",
                       "糟糕", "完美", "垃圾", "恶心", "棒", "烂"]
    emotional_count = sum(1 for w in emotional_words if w in text)
    if emotional_count > 3:
        analysis["系统激活状态"].append(f"检测到 {emotional_count} 个情绪化用词 — 偏系统1快速判断，警惕情感遮蔽理性")
    elif emotional_count > 0:
        analysis["系统激活状态"].append(f"情绪化用词较少({emotional_count}个)，偏向理性分析模式")
    else:
        analysis["系统激活状态"].append("未检测到情绪化表达 — 适合理性分析")

    # 认知放松/紧张检测
    ease_indicators = []
    if any(w in text for w in ["简单", "显然", "一目了然", "不言而喻", "常识", "众所周知"]):
        ease_indicators.append("使用'显然/常识'等词 — 处于认知放松状态，有真实感错觉风险，建议激活系统2核查")
    if any(w in text for w in ["复杂", "难以理解", "费解", "困惑", "不确定", "模棱两可"]):
        ease_indicators.append("承认复杂性/不确定性 — 处于认知紧张状态，有利于启动系统2深入分析")
    if any(w in text for w in ["重复", "众所周知", "老生常谈", "经典"]):
        ease_indicators.append("提及熟悉概念 — 曝光效应可能增强认同感，但熟悉不等于正确")
    analysis["认知放松/紧张检测"] = ease_indicators

    # WYSIATI检测
    if any(w in text for w in ["唯一原因", "主要因素", "归根结底", "说到底", "无非是"]):
        analysis["认知放松/紧张检测"].append(
            "可能犯WYSIATI错误: 仅基于可见信息下结论，忽略了大量缺失信息"
        )

    # 理论诱导盲视检测
    if any(w in text for w in ["众所周知", "不可否认", "这是真理", "这是定律", "从来如此"]):
        analysis["认知放松/紧张检测"].append(
            "理论诱导盲视风险: 将某种理论/观点视为不证自明，可能排除相悖证据"
        )

    # 认知偏见检测
    detected_biases = []
    bias_map = {
        "锚定效应": ["锚定", "基准价", "起价", "原价", "参考价", "初始定价"],
        "确认偏误": ["我当然", "我一直", "正如我所料", "显然", "毫无疑问", "果然不出"],
        "可得性启发": ["最近", "经常听说", "印象中", "新闻上", "记得有", "身边"],
        "框架效应": ["损失", "收益", "存活率", "死亡率", "概率", "胜率"],
        "损失厌恶": ["舍不得", "放弃太可惜", "难以割舍", "白费了", "不能白花"],
        "沉没成本": ["已经投入", "白费", "放弃太可惜", "不能半途而废", "坚持到现在"],
        "过度自信": ["毫无疑问", "绝对正确", "100%", "一定", "必然", "绝不可能", "绝对"],
        "事后聪明": ["早就知道", "早该", "预料之中", "不出所料", "果然"],
        "光环效应": ["不仅...而且...好", "各方面都", "完美", "全面"],
        "峰终定律": ["最后的印象", "结尾", "高潮", "最难忘的"],
        "规划谬误": ["按时完成", "预算内", "乐观估计", "很快就能", "赶得上"],
        "乐观偏差": ["应该没问题", "不会发生在我", "我运气好", "不至于"],
        "禀赋效应": ["我的", "我拥有的", "舍不得卖", "自己的"],
        "现状偏好": ["一直以来", "保持不变", "维持现状", "不改变", "习惯"],
        "代表性启发": ["典型的", "看起来像", "这种人", "标准案例"],
        "基本归因错误": ["他就是", "他就是那种人", "本性如此"],
    }
    for bias, keywords in bias_map.items():
        for kw in keywords:
            if kw in text:
                detected_biases.append({"bias": bias, "trigger": kw})
                break
    analysis["认知偏见检测"] = detected_biases

    # 前景理论分析
    prospect_notes = []
    if "损失" in text and "收益" in text:
        prospect_notes.append("同时提及损失和收益 — 检查参照点和框架效应的影响")
    if any(w in text for w in ["赌", "风险", "冒险", "保守", "博弈"]):
        prospect_notes.append("涉及风险决策 — 检查:面对收益时是否风险回避?面对损失时是否风险寻求?")
    if any(w in text for w in ["舍不得", "我的", "拥有的"]):
        prospect_notes.append("禀赋效应可能: 对已拥有物品的估值显著高于未拥有时")
    if "概率" in text:
        prospect_notes.append("涉及概率判断 — 注意敏感性递减规律: 1%->2% 的感知变化远大于 50%->51%")
    analysis["前景理论分析"] = prospect_notes

    # 记忆自我特征（峰终定律）
    memory_notes = []
    if any(w in text for w in ["最后", "结尾", "高潮", "总结来说", "归根结底"]):
        memory_notes.append("涉及对结尾/高峰的评价 — 警惕峰终定律: 整体判断可能由峰值和结尾决定")
    if any(w in text for w in ["总体", "总的来说", "整体而言", "回顾"]):
        memory_notes.append("整体评价可能由记忆自我(峰终定律)驱动，而非体验自我的累计感受")
    analysis["记忆自我特征"] = memory_notes

    # 判断建议
    suggestions = []
    if detected_biases:
        bias_names = list(dict.fromkeys(b["bias"] for b in detected_biases))
        if len(bias_names) >= 3:
            suggestions.append(
                f"检测到多种偏见({', '.join(bias_names[:5])}...) — 强烈建议暂停判断，用系统2慢思考系统性地重新审视"
            )
        elif len(bias_names) == 2:
            suggestions.append(
                f"注意: 同时存在[{bias_names[0]}]和[{bias_names[1]}] — 两者可能相互强化，需警惕"
            )
        else:
            for b in detected_biases:
                suggestions.append(f"注意可能性: [{b['bias']}] — 触发词'{b['trigger']}'，建议用数据验证")
    else:
        suggestions.append("未检测到明显认知偏见，但仍需注意: 系统1的自动判断可能隐藏深层偏见")

    if analysis["系统激活状态"] and any("系统1" in s for s in analysis["系统激活状态"]):
        suggestions.append("建议: 转换到系统2慢思考模式，寻找反面证据，用数据和逻辑验证直觉判断")
    analysis["判断建议"] = suggestions

    return analysis
