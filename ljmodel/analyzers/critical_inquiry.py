"""基于《学会提问》的批判性质询分析"""


def analyze_critical_inquiry(text: str, kb: dict) -> dict:
    """淘金式思维·批判性质询框架"""
    analysis = {
        "论题识别": [], "结论定位": [], "理由提取": [],
        "歧义分析": [], "假设识别": [], "谬误检测": [],
        "证据评估": [], "替代原因": [], "数据检查": [],
        "省略信息": [], "合理结论": [],
        "思维模式诊断": [], "认知障碍检测": []
    }

    # Q1: 论题和结论是什么？
    issue_type = None
    if any(w in text for w in ["应该", "应不应该", "好不", "对不对", "值不值得", "妥不妥"]):
        issue_type = "规定性论题(关注'应该/好/坏/对/错')"
    elif any(w in text for w in ["原因", "影响", "导致", "结果", "是什么", "为什么", "如何"]):
        issue_type = "描述性论题(关注'是什么/为什么/如何')"
    else:
        issue_type = "未明确识别论题类型 — 建议主动判断"
    analysis["论题识别"].append(f"论题类型: {issue_type}")

    issue_sensitivity = "高" if any(w in text for w in ["政策", "宗教", "政治", "道德", "伦理", "性别", "种族"]) else "一般"
    analysis["论题识别"].append(f"论题敏感度: {issue_sensitivity} — 敏感话题更需要强势批判性思维")

    conclusion_markers = ["所以", "因此", "由此可见", "结论是", "表明", "证明", "总之",
                          "故而", "于是", "因而", "可见", "故"]
    found_conclusions = []
    lines = text.split("。")
    for line in lines:
        for marker in conclusion_markers:
            if marker in line and len(line.strip()) > len(marker) + 1:
                found_conclusions.append(f"[{marker}] {line.strip()[:80]}")
                break
    if found_conclusions:
        analysis["结论定位"] = found_conclusions[:3]
        analysis["结论定位"].append(f"提示: 共检测到{len(found_conclusions)}个结论标记 — 注意结论是否都有理由支撑")
    else:
        if issue_type and "规定性" in issue_type:
            analysis["结论定位"].append("未检测到明确结论标记 — 规定性论证应包含明确的立场声明")
        else:
            analysis["结论定位"].append("未检测到明确结论标记 — 文本可能仅为描述/叙事而非论证")

    if not found_conclusions and not any(w in text for w in ["因为", "由于", "基于", "鉴于"]):
        analysis["结论定位"].append("警告: 仅表达观点没有提供理由 — 不符合批判性思维要求")

    # Q3: 歧义分析
    abstract_terms = ["公平", "正义", "自由", "权利", "责任", "民主", "平等", "尊严",
                      "合理", "适当", "充分", "必要", "好", "坏", "优秀", "落后",
                      "改革", "进步", "保守", "激进", "正常", "异常"]
    found_ambiguous = [t for t in abstract_terms if t in text]
    if found_ambiguous:
        analysis["歧义分析"].append(f"检测到潜在歧义关键词: {', '.join(found_ambiguous[:8])}")
        analysis["歧义分析"].append("建议: 对这些抽象词进行定义检查 — 作者是否明确定义了含义？")
        analysis["歧义分析"].append("角色扮演测试: 换一个持不同立场的人理解这些词，含义会不同吗？")
    else:
        analysis["歧义分析"].append("未检测到明显歧义的抽象词")

    loaded_terms = ["极端", "激进", "官僚", "腐败", "反动", "伪", "真正", "纯粹",
                    "野蛮", "文明", "先进", "落后", "科学", "迷信"]
    found_loaded = [t for t in loaded_terms if t in text]
    if found_loaded:
        analysis["歧义分析"].append(f"情感负载词: {', '.join(found_loaded[:5])} — 这些词含价值预设，需剥离情感后再分析")

    quantifiers = ["很多", "大量", "少数", "若干", "一些", "许多", "极少", "多数"]
    found_quant = [q for q in quantifiers if q in text]
    if found_quant:
        analysis["歧义分析"].append(f"模糊量词: {', '.join(found_quant[:5])} — '多少？'需要具体数字")

    # Q2: 理由提取
    reason_markers = ["因为", "由于", "基于", "鉴于", "考虑到", "理由是",
                      "第一", "第二", "第三", "首先", "其次", "再次", "最后"]
    found_reasons = [m for m in reason_markers if m in text]
    if found_reasons:
        analysis["理由提取"].append(f"检测到理由标记: {', '.join(found_reasons)}")
        if len(found_reasons) >= 3:
            analysis["理由提取"].append("有多个理由支撑 — 论证基础较好")
        else:
            analysis["理由提取"].append("理由数量较少 — 建议追问'还有其他理由吗？'")
    else:
        analysis["理由提取"].append("未检测到明确的理由标记 — 论证可能缺乏支撑")

    reason_count = len(found_reasons)
    conclusion_count = len(found_conclusions)
    if reason_count > 0 and conclusion_count == 0:
        analysis["理由提取"].append("有理由但无结论 — 论证不完整")
    elif reason_count == 0 and conclusion_count > 0:
        analysis["理由提取"].append("有结论但无理由 — 仅为观点，非论证")
    elif reason_count > 0 and conclusion_count > 0:
        analysis["理由提取"].append("包含前提和结论 — 构成完整论证")

    # Q4: 假设识别
    value_conflicts = {
        "自由安全": (["自由", "权利"], ["安全", "管控", "秩序"], "自由 vs 安全"),
        "公平效率": (["公平", "平等"], ["效率", "效益", "增长"], "公平 vs 效率"),
        "竞争合作": (["竞争", "优胜劣汰"], ["合作", "协作", "团结"], "竞争 vs 合作"),
        "传统变革": (["传统", "保守", "继承"], ["变革", "改革", "创新"], "传统 vs 变革"),
        "个人集体": (["个人", "私人", "个体"], ["集体", "整体", "公共"], "个人主义 vs 集体主义"),
        "环境经济": (["环境", "生态", "自然"], ["经济", "发展", "增长"], "环境保护 vs 经济发展"),
        "质量数量": (["质量", "品质", "优质"], ["数量", "规模", "覆盖"], "质量 vs 数量"),
    }
    detected_conflicts = []
    for _, (a_words, b_words, label) in value_conflicts.items():
        if any(w in text for w in a_words) and any(w in text for w in b_words):
            detected_conflicts.append(label)
    if detected_conflicts:
        analysis["假设识别"].append(f"检测到潜在价值冲突: {'; '.join(detected_conflicts)}")
        analysis["假设识别"].append("提示: 作者默认了哪种价值优先？如果换一种优先级会得出不同结论吗？")
    else:
        analysis["假设识别"].append("未检测到明确的价值冲突 — 注意可能隐藏的价值假设")

    desc_assumption_triggers = ["假设", "前提", "假定", "预设", "先决条件"]
    found_da = [t for t in desc_assumption_triggers if t in text]
    if found_da:
        analysis["假设识别"].append(f"检测到描述性假设标记: {', '.join(found_da)} — 检查这些假设是否成立")

    if any(w in text for w in ["导致", "引起", "使得", "促使"]):
        analysis["假设识别"].append("存在因果假设 — 默认了A导致B，需要验证因果关系是否成立")

    # Q5: 谬误检测
    fallacy_checks = {
        "人身攻击": ["你就是", "你这种人", "你是", "你这个"],
        "诉诸情感": ["可怜", "恐怖", "可怕", "令人发指", "毛骨悚然", "惨无人道"],
        "虚假两难": ["要么...要么...", "不是...就是...", "别无选择", "唯一出路", "非此即彼"],
        "稻草人": ["极端", "过分", "过度"],
        "滑坡谬误": ["最终会", "迟早", "总有一天会"],
        "诉诸公众": ["大家都", "多数人", "普遍认为", "公认", "主流"],
        "诉诸传统": ["从来如此", "向来", "自古以来"],
        "诉诸中庸": ["折中", "中庸", "中间立场"],
        "诉诸可疑权威": ["明星", "网红", "名人", "知名"],
    }
    detected_fallacies_ci = []
    for fallacy, triggers in fallacy_checks.items():
        for t in triggers:
            if t in text:
                detected_fallacies_ci.append(f"{fallacy}(触发词:{t})")
                break
    if detected_fallacies_ci:
        analysis["谬误检测"].append(f"检测到潜在谬误: {'; '.join(detected_fallacies_ci)}")
    else:
        analysis["谬误检测"].append("未检测到明显谬误标记 — 但仍需仔细检查论证结构")

    # Q6: 证据评估
    evidence_map = {
        "直觉": ("直觉", "直觉性证据 — 无法验证，可靠性最低"),
        "个人经验": ("经验", "个人经历证据 — 样本量N=1，不能代表整体"),
        "典型案例": ("案例", "案例证据 — 生动但不一定具有代表性"),
        "当事人证言": ("证言", "证言证据 — 可能有选择性偏见和利益相关"),
        "专家意见": ("专家", "专家意见 — 需评估专家资质/领域/公正性"),
        "研究报告": ("研究", "研究证据 — 相对可靠，需检查方法学质量"),
        "数据统计": ("数据", "数据/统计证据 — 需检查来源和解读方式"),
        "类比": ("类比", "类比证据 — 帮助理解但不能证明结论"),
    }
    evidence_found = [{"type": ev_type, "description": desc}
                      for ev_type, (keyword, desc) in evidence_map.items() if keyword in text]

    if evidence_found:
        analysis["证据评估"].append(f"检测到 {len(evidence_found)} 种证据类型:")
        for ev in evidence_found:
            analysis["证据评估"].append(f"  - {ev['type']}: {ev['description']}")
        ev_types = [e["type"] for e in evidence_found]
        followups = {
            "直觉": "  >> 追问直觉: 直觉来源可靠吗？有相反直觉吗？",
            "个人经验": "  >> 追问个人经验: 这个经历典型吗？有系统数据支持吗？",
            "典型案例": "  >> 追问案例: 案例是精心挑选的吗？反面案例有多少？",
            "当事人证言": "  >> 追问证言: 提供者是否有利益关系？信息是否全面？",
            "专家意见": "  >> 追问专家: 专家的领域相关吗？有利益冲突吗？其他专家怎么说？",
            "研究报告": "  >> 追问研究: 样本量和代表性如何？控制组？可重复验证？",
            "数据统计": "  >> 追问数据: 来源？平均值类型？全距和分布？",
            "类比": "  >> 追问类比: 相似点是关键性的还是表面的？差异被忽略了吗？",
        }
        for et in ev_types:
            if et in followups:
                analysis["证据评估"].append(followups[et])
    else:
        analysis["证据评估"].append("未检测到明确的证据引用 — 论证可能建立在观点而非证据之上")

    # Q7: 替代原因
    causal_markers = ["导致", "引起", "因为...所以", "由于", "使得", "促使", "因果关系"]
    if any(w in text for w in causal_markers) or ("因为" in text and "所以" in text):
        analysis["替代原因"].append("检测到因果关系表述 — 相关性不等于因果！")
        analysis["替代原因"].append("4种可能解释: (1)A→B (2)B→A (3)X同时→A和B (4)纯属巧合")
        if text.count("因为") < 2:
            analysis["替代原因"].append("可能原因过度简化 — 复杂结果很少由单一原因导致")
        if any(w in text for w in ["之后", "此后", "随后", "然后"]):
            analysis["替代原因"].append("注意事后归因谬误: A在B之前不等于A导致B")
        if any(w in text for w in ["他就是", "这种人", "本性", "性格"]):
            analysis["替代原因"].append("可能犯基本归因错误: 高估个人因素，低估环境因素")
    else:
        analysis["替代原因"].append("未检测到明确的因果关系表述")

    # Q8: 数据检查
    if any(w in text for w in ["数据", "统计", "比例", "百分比", "平均", "中位数"]):
        analysis["数据检查"].append("检测到数据/统计 — 执行数据检查清单:")
        if "平均" in text:
            analysis["数据检查"].append("  [!] 检查平均值类型: 平均数/中位数/众数？平均数易受极端值影响")
        if "比例" in text or "百分比" in text:
            analysis["数据检查"].append("  [!] 注意百分比基数: 百分比变化是否伴随着基数的变化？")
        if "最大" in text or "最小" in text or "范围" in text:
            analysis["数据检查"].append("  [!] 已提供全距信息 — 有利于理解数据分布")
        else:
            analysis["数据检查"].append("  [!] 未提供全距/分布 — 平均值掩盖了内部差异")
        analysis["数据检查"].append("  追问: 数据来源是什么？样本如何选择的？")
        analysis["数据检查"].append("  追问: 是否拿一件事的数据证明另一件事？")
        analysis["数据检查"].append("  追问: 是否有缺失的比较(同比/环比)？")
    else:
        analysis["数据检查"].append("未检测到统计数据的引用")

    # Q9: 省略信息
    analysis["省略信息"].append("主动寻找被省略的信息:")
    one_sided = not any(w in text for w in ["但是", "然而", "不过", "另一方面", "缺点", "风险", "负面", "代价"])
    if one_sided:
        analysis["省略信息"].append("  可能是单面论证 — 没有提及反面观点或负面效果")
    if any(w in text for w in ["优点", "好处", "优势", "收益", "利益"]) and not any(w in text for w in ["缺点", "坏处", "风险", "代价"]):
        analysis["省略信息"].append("  只说了好处没提坏处 — 注意被省略的负面效果")
    if any(w in text for w in ["更好", "更多", "更快", "更大", "更小", "更少"]):
        analysis["省略信息"].append("  检测到比较级 — 和什么比较？需要具体参照物")
    analysis["省略信息"].append("  建议追问: 反对者会提出什么理由？")
    analysis["省略信息"].append("  建议追问: 这个行动的长期负面效果是什么？")
    analysis["省略信息"].append("  建议追问: 谁没有受益？谁蒙受了损失？")

    # Q10: 合理结论
    binary_thinking = any(w in text for w in ["要么...要么...", "不是...就是...", "非此即彼",
                                               "只有两种", "两种可能", "不是对就是错"])
    if binary_thinking:
        analysis["合理结论"].append("警告: 存在二分式思维 — 重大问题很少有简单的是/否答案")
    else:
        analysis["合理结论"].append("未检测到明显二分式思维")
    if found_conclusions:
        analysis["合理结论"].append(f"现有结论数量: {len(found_conclusions)} — 同一套理由可能推导出多个合理结论")
        analysis["合理结论"].append("使用条件句限定: 问'这个结论在什么时候/什么地方/为什么目的成立？'")
        analysis["合理结论"].append("重新表述论题: 从'是/否'转向'我们该怎么处理这个问题？'")

    # 思维模式诊断
    self_ref_count = sum(1 for w in ["我", "我的", "我认为", "我觉得"] if w in text)
    if self_ref_count >= 3:
        analysis["思维模式诊断"].append("大量第一人称 — 可能处于弱势批判性思维(捍卫己见)或海绵式思维(未加批判地吸收)")
    elif self_ref_count >= 1:
        analysis["思维模式诊断"].append("有第一人称表述 — 注意区分'我的观点'和'有充分理由的结论'")

    if any(w in text for w in ["为什么", "如何证明", "证据", "根据", "理由"]):
        analysis["思维模式诊断"].append("有质疑性语言 — 倾向于淘金式思维(主动筛选)")
    elif any(w in text for w in ["毫无疑问", "显然", "众所周知", "不可否认"]):
        analysis["思维模式诊断"].append("使用绝对化表述 — 可能处于弱势批判性思维(拒绝质疑)")
    else:
        analysis["思维模式诊断"].append("思维模式待判断 — 建议主动采用淘金式思维和强势批判性思维审视文本")

    # 认知障碍检测
    obstacle_map = {
        "思考太快": ["简单", "显然", "一目了然", "常识"],
        "刻板印象": ["都", "全都", "所有...都", "总是"],
        "信念固着": ["我当然", "我一直", "我始终认为"],
        "一厢情愿": ["一定会好", "应该没问题", "不至于", "不会发生"],
        "可得性启发": ["最近", "经常", "印象中", "新闻"],
        "知识的诅咒": ["众所周知", "大家都知道", "很显然"],
    }
    obstacle_hits = []
    for obstacle, triggers in obstacle_map.items():
        if any(t in text for t in triggers):
            obstacle_hits.append(obstacle)
    if obstacle_hits:
        analysis["认知障碍检测"].append(f"可能存在的认知障碍: {', '.join(set(obstacle_hits))}")
    else:
        analysis["认知障碍检测"].append("未检测到明显认知障碍标记")

    return analysis
