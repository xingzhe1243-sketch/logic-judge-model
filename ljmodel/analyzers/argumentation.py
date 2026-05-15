"""基于《论证是一门学问》的论证规则评估"""


def analyze_argumentation(text: str, kb: dict) -> dict:
    """50条论证规则完整体系评估"""
    rules = kb["argumentation_rules"]
    analysis = {
        "一般规则检查": [], "论证类型识别": [],
        "举例论证评估": [], "类比论证评估": [],
        "诉诸权威评估": [], "因果论证评估": [],
        "演绎论证评估": [], "扩展论证评估": [],
        "议论写作评估": [], "公共辩论评估": [],
        "谬误检查": [], "定义检查": []
    }

    # 通则检查
    has_conclusion = any(w in text for w in ["所以", "因此", "由此可见", "结论", "总之", "故而", "于是"])
    has_premise = any(w in text for w in ["因为", "由于", "基于", "鉴于", "考虑到"])
    if has_conclusion and has_premise:
        analysis["一般规则检查"].append("规则1[OK]: 同时有前提和结论标记 — 构成完整论证")
    elif has_conclusion and not has_premise:
        analysis["一般规则检查"].append("规则1[X]: 有结论但无前提标记 — 仅为观点，非论证(规则1)")
        analysis["一般规则检查"].append("规则2提示: 理顺思路 — 结论应当有前提支撑")
    elif not has_conclusion and has_premise:
        analysis["一般规则检查"].append("规则1[X]: 有前提但无结论标记 — 论证不完整(规则1)")
    else:
        analysis["一般规则检查"].append("规则1[X]: 无法识别论证结构 — 可能为单纯描述")

    if any(w in text for w in ["研究", "数据", "统计", "证据", "史实", "事实"]):
        analysis["一般规则检查"].append("规则3[OK]: 前提有事实性支撑 — 需进一步核查来源可靠性")
    else:
        analysis["一般规则检查"].append("规则3?: 前提可靠性待确认 — 建议从可靠前提出发")

    vague_markers = sum(1 for w in ["很多", "大量", "若干", "一些", "某些", "若干"] if w in text)
    if vague_markers >= 2:
        analysis["一般规则检查"].append(f"规则4?: 使用了{vague_markers}个模糊量词 — 论证建议更具体简明")
    else:
        analysis["一般规则检查"].append("规则4[OK]: 语言较具体 — 抽象表述可控")

    emotional_count = sum(1 for w in ["太可怕", "令人发指", "极端", "可恶", "垃圾", "混蛋",
                                       "无耻", "卑鄙", "伟大", "完美", "绝对正确"] if w in text)
    if emotional_count >= 2:
        analysis["一般规则检查"].append(f"规则5[X]: 检测到{emotional_count}个诱导性/情绪化用词 — 应立足实据而非情感操控")
    else:
        analysis["一般规则检查"].append("规则5[OK]: 未检测到明显诱导性言论")
    analysis["一般规则检查"].append("规则6提示: 检查文中重复出现的关键术语含义是否前后一致")

    # 论证类型识别
    arg_type_map = {
        "举例论证": ["例如", "比如", "举例", "如", "譬如", "比方说", "举个例子"],
        "类比论证": ["如同", "就像", "好比", "类似于", "类比", "相当于", "正如"],
        "诉诸权威": ["专家", "权威", "研究表明", "科学家", "学者", "教授", "研究院"],
        "因果论证": ["导致", "引起", "因为", "所以", "使得", "促使", "造成", "影响"],
        "演绎论证": ["如果", "那么", "所有", "凡是", "每一个"],
        "扩展论证": ["第一", "第二", "第三", "首先", "其次", "再者", "最后"],
        "公共辩论": ["辩论", "争议", "双方", "同意", "反对"],
    }
    detected_types = []
    for arg_type, triggers in arg_type_map.items():
        if any(t in text for t in triggers):
            detected_types.append(arg_type)
    analysis["论证类型识别"] = detected_types if detected_types else ["未识别出明确的论证类型"]

    # 举例论证
    if "例如" in text or "比如" in text or "举例" in text:
        analysis["举例论证评估"].append("检测到举例论证:")
        example_count = text.count("例如") + text.count("比如") + text.count("举例")
        if example_count >= 2:
            analysis["举例论证评估"].append(f"  规则7[OK]: 有{example_count}个例子 — 多个例子支撑较好")
        else:
            analysis["举例论证评估"].append(f"  规则7?: 仅{example_count}个例子 — 孤例不立，建议补充更多例子")
        analysis["举例论证评估"].append("  规则8提示: 检查例子是否具有代表性 — 避免极端个案")
        if "反例" in text or "但是" in text or "然而" in text:
            analysis["举例论证评估"].append("  规则11[OK]: 文中提及了反例或相反情况 — 论证有自我批判意识")

    # 类比论证
    if any(w in text for w in ["如同", "就像", "好比", "类似于", "正如"]):
        analysis["类比论证评估"].append("检测到类比论证:")
        analysis["类比论证评估"].append("  规则12检查: 类比中的相似点是否关键且相关？差异是否被忽略？")

    # 诉诸权威
    if any(w in text for w in ["专家", "权威", "研究表明", "科学家", "学者"]):
        analysis["诉诸权威评估"].append("检测到引用权威:")
        if "专家" in text or "科学家" in text or "学者" in text:
            analysis["诉诸权威评估"].append("  规则13-14: 请检查是否列出了具体信息来源？权威在该领域的资质如何？")
        if "研究表明" in text or "研究显示" in text:
            analysis["诉诸权威评估"].append("  规则15-16: 引用了研究 — 检查研究来源的公正性和可核实的程度")
        analysis["诉诸权威评估"].append("  规则17提示: 是否考虑了反对意见？对批评的回应是否充分？")

    # 因果论证
    causal_words = ["导致", "引起", "造成", "因为", "所以", "促使"]
    if any(w in text for w in causal_words):
        analysis["因果论证评估"].append("检测到因果论证:")
        analysis["因果论证评估"].append("  规则18: 因果论证始于关联 — 是否建立了可靠的相关性？")
        analysis["因果论证评估"].append("  规则19: 一种关联有多种解释 — 是否有其他可能的原因？")
        analysis["因果论证评估"].append("  规则20: 寻求最有可能的解释 — 排除其他可能性了吗？")
        if sum(1 for w in causal_words if w in text) <= 1:
            analysis["因果论证评估"].append("  规则21提示: 原因要素较少 — 注意情况有时很复杂，避免过度简化")

    # 演绎论证
    if "如果" in text and "那么" in text:
        analysis["演绎论证评估"].append("检测到条件推理:")
        if "所以" in text or "因此" in text:
            analysis["演绎论证评估"].append("  规则22-23: 检查推理形式 — 肯定前件有效，肯定后件无效")
        if "或" in text or "要么" in text:
            analysis["演绎论证评估"].append("  规则25: 检测到选言推理 — 排除一种后剩余为真")
        if "第一" in text and "第二" in text and "第三" in text:
            analysis["演绎论证评估"].append("  规则28: 多步复合论证 — 检查各步演绎形式的有效性")

    # 扩展论证
    if sum(1 for w in ["第一", "第二", "第三", "首先", "其次"] if w in text) >= 3:
        analysis["扩展论证评估"].append("检测到多步骤扩展论证结构:")
        analysis["扩展论证评估"].append("  规则29-30: 论证有结构层次 — 将各环节按前提→结论形式组织")
        analysis["扩展论证评估"].append("  规则31: 关键前提是否都有专门的论证支持？")
        analysis["扩展论证评估"].append("  规则32: 是否考虑并回应了反驳意见？")

    # 议论写作
    if len(text) > 200:
        if any(w in text for w in ["我认为", "本文", "笔者"]):
            analysis["议论写作评估"].append("规则34: 开篇点题 — 在开头就表明立场")
        analysis["议论写作评估"].append("规则35: 检查主张是否明确且可操作？")
        analysis["议论写作评估"].append("规则36: 论证结构是否遵循'观点→论证→总结'？")
        if any(w in text for w in ["但是", "然而", "不过", "反过来说"]):
            analysis["议论写作评估"].append("规则37[OK]: 处理了反对意见")

    # 公共辩论
    if any(w in text for w in ["辩论", "争议", "双方", "我们同意", "我们反对"]):
        analysis["公共辩论评估"].append("检测到辩论性内容:")
        if "人身攻击" not in text and "你错了" not in text:
            analysis["公共辩论评估"].append("规则45-46: 聚焦论证而非攻击 — 符合建设性辩论原则")
        if any(w in text for w in ["共同", "一致", "共识", "基础"]):
            analysis["公共辩论评估"].append("规则48[OK]: 寻求共识 — 找到了分歧中的共同基础")
        analysis["公共辩论评估"].append("规则49: 注意保持礼貌 — 聚焦论证而非人身")
        analysis["公共辩论评估"].append("规则50: 留出反思空间 — 观点可能随论证而改变")

    # 谬误检查
    fallacy_checks_arg = {
        "诉诸无知": ["无法证明", "不能证伪", "没人能证明不"],
        "诉诸怜悯": ["可怜", "太惨了", "于心何忍"],
        "诉诸群众": ["大家都", "多数人", "普遍认为", "公认"],
        "以偏概全": ["所有的...都", "总是", "从来都", "个个"],
        "忽略替代解释": ["唯一原因", "根本原因", "决定性因素"],
        "诱导性语言": ["野蛮", "文明", "先进", "落后", "极端", "恐怖"],
        "循环论证": ["因为...所以...因为"],
    }
    detected_fallacies_arg = []
    for fallacy, triggers in fallacy_checks_arg.items():
        for t in triggers:
            if t in text:
                detected_fallacies_arg.append(f"{fallacy}(触发:{t})")
                break
    if detected_fallacies_arg:
        analysis["谬误检查"].append(f"潜在谬误: {'; '.join(detected_fallacies_arg)}")
    else:
        analysis["谬误检查"].append("未检测到明显谬误标记")

    # 定义检查
    ambiguous_terms_arg = ["自由", "公平", "正义", "民主", "平等", "权利",
                           "合理", "适当", "必要", "充分", "好", "坏"]
    found_ambiguous_arg = [t for t in ambiguous_terms_arg if t in text]
    if found_ambiguous_arg:
        analysis["定义检查"].append(f"关键概念可能需要定义: {', '.join(found_ambiguous_arg[:6])}")
        analysis["定义检查"].append("建议: 对这些概念进行定义 — 词典定义/操作性定义/分类式定义")
    else:
        analysis["定义检查"].append("未检测到需要定义的关键概念")

    return analysis
