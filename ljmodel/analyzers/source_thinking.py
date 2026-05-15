"""基于《源思维：洞穿本质的深度思考法》的深度分析"""


def analyze_source_thinking(text: str, kb: dict) -> dict:
    """还原事实→辨析因果→锚定切口深度分析"""
    st = kb["source_thinking"]
    analysis = {
        "层次诊断": [], "思维模式诊断": [],
        "还原事实分析": [], "辨析因果分析": [],
        "锚定切口分析": [], "不良思维习惯": [],
        "关键概念检查": [], "深度思考评分": []
    }

    # 1. 层次诊断
    analysis["层次诊断"].append("[层次诊断] 按源思维三层模型分析本文本:")
    has_phenomenon_desc = len(text) < 50 or text.count("。") <= 1
    if has_phenomenon_desc:
        analysis["层次诊断"].append("  [现象层] 文本较简短，可能仅停留在现象描述('观其然')")
    else:
        analysis["层次诊断"].append("  [现象层] 文本有一定长度，需确认是否透过现象看到了本质")

    has_evidence_words = any(w in text for w in ["数据", "研究", "调查", "统计", "研究表明", "证据", "事实", "案例"])
    if has_evidence_words:
        analysis["层次诊断"].append("  [事实层] 检测到客观证据/数据表述 — 正在向事实层深入")
    else:
        analysis["层次诊断"].append("  [事实层] 缺少客观证据支持 — 注意一个现象背后可能有多种不同的事实")

    has_essence_words = any(w in text for w in ["因为", "所以", "因此", "原因", "本质", "根本", "为什么", "关键"])
    if has_essence_words:
        analysis["层次诊断"].append("  [本质层] 检测到因果追问或深层分析 — 正在触及本质('所以然')")
    else:
        analysis["层次诊断"].append("  [本质层] 未检测到深度因果分析 — 停留在表面，未触及本质")

    # 2. 思维模式诊断
    cause_count_text = text.count("因为")
    reason_count = sum(text.count(w) for w in ["原因是", "源于", "由于", "归因于"])
    total_cause_indicators = cause_count_text + reason_count

    internal_attribution_words = ["懒惰", "蠢", "笨", "没天赋", "性格差", "自私", "坏", "笨"]
    has_internal_attribution = any(w in text for w in internal_attribution_words)

    if total_cause_indicators == 0:
        analysis["思维模式诊断"].append("[!] 单一断定思维风险: 未给出任何原因分析 — 可能仅凭直觉下结论")
        analysis["思维模式诊断"].append("  多元因果思维要求: 提出尽可能多的假设来解释现象，而非简单断定")
    elif total_cause_indicators == 1:
        analysis["思维模式诊断"].append(f"[!] 单一断定思维风险: 仅检测到 {total_cause_indicators} 个原因 — 复杂现象很少由单一因素导致")
        analysis["思维模式诊断"].append("  建议: 运用多元因果思维，从多角度提出假设(能力/心态/制度/环境等)")
    else:
        analysis["思维模式诊断"].append(f"[OK] 多元因果倾向: 检测到 {total_cause_indicators} 个因果关系表述")
        analysis["思维模式诊断"].append("  继续深入: 在这些原因中，哪个是关键变量(关键X)？")

    if has_internal_attribution:
        analysis["思维模式诊断"].append("  [!] 注意: 检测到内部特质归因标签(如懒惰/笨/自私) — 深度思考应避免用难以界定的内在特质解释行为")

    if any(w in text for w in ["相关", "关联", "联系", "关系"]) and not any(w in text for w in ["因果", "导致", "因为"]):
        analysis["思维模式诊断"].append("  [!] 注意: 仅讨论相关性未分析因果关系 — 相关不等于因果，需要满足三个条件: 关联性/时间顺序/排除干扰")

    # 3. 还原事实分析
    abstract_concepts = ["幸福", "成功", "自由", "公平", "正义", "民主", "权利", "责任", "爱", "理想", "本质", "价值"]
    found_concepts = [c for c in abstract_concepts if c in text]
    if found_concepts:
        analysis["还原事实分析"].append(f"检测到关键抽象概念: {', '.join(found_concepts)}")
        analysis["还原事实分析"].append("  还原事实第一步: 识别这些关键概念 — 它们可能被模糊使用")
        analysis["还原事实分析"].append("  还原事实第二步: 定义关键概念 — 检查这些概念在文中的具体含义")
        analysis["还原事实分析"].append("  还原事实第三步: 重新表述事实 — 基于定义产生多种可能的事实版本")
    else:
        analysis["还原事实分析"].append("建议进行还原事实三步骤:")
        analysis["还原事实分析"].append("  1. 识别关键概念 — 找出文本中的核心概念")
        analysis["还原事实分析"].append("  2. 定义关键概念 — 明确概念的准确含义")
        analysis["还原事实分析"].append("  3. 重新表述事实 — 基于不同定义形成多种可能的事实表述")

    vague_concepts = ["不听话", "叛逆", "不好", "不行", "差", "坏", "好"]
    if any(c in text for c in vague_concepts):
        analysis["还原事实分析"].append("  [!] 注意日常模糊概念 — 如'不听话'可能有多种含义(不遵守制度/不符合要求/意见不一致)，定义精度决定解决效度")
    if found_concepts or any(c in text for c in vague_concepts):
        analysis["还原事实分析"].append("  让定义优先于讨论 — 定义问题的精度决定解决问题的效度")

    # 4. 辨析因果分析
    has_major_premise = any(w in text for w in ["所有", "凡是", "都", "总是", "每个", "人人"])
    has_minor_premise = any(w in text for w in ["这个", "这个案例", "这个例子", "例如", "比如"])
    has_conclusion = any(w in text for w in ["所以", "因此", "结论", "由此可见", "总之"])

    if has_major_premise and has_conclusion:
        analysis["辨析因果分析"].append("[三段论重建] 检测到大前提+结论结构，尝试重建完整三段论:")
        analysis["辨析因果分析"].append("  大前提: (普遍规律/原则) 是什么？")
        analysis["辨析因果分析"].append("  小前提: (具体案例/情境) 是否符合大前提？")
        analysis["辨析因果分析"].append("  结论: 是否合理地从前提推导而来？")
        analysis["辨析因果分析"].append("  关键: 检查大前提是否正确 — 大前提错误则整个演绎崩塌")
    else:
        analysis["辨析因果分析"].append("[因果分析] 未检测到完整三段论结构")

    if "因为" in text or "所以" in text:
        analysis["辨析因果分析"].append("[因果关系验证] 检查因果三条件:")
        analysis["辨析因果分析"].append("  条件1(关联性): X和Y之间是否存在关联？")
        analysis["辨析因果分析"].append("  条件2(时间顺序): 原因是否在结果之前发生？(注意: 冰激凌销量与溺水人数有先后但非因果)")
        analysis["辨析因果分析"].append("  条件3(排除干扰): 是否排除了其他可能解释？")

    analysis["辨析因果分析"].append("[因果分析两层追问]:")
    analysis["辨析因果分析"].append("  第一层: '这是因为…'(This is because) — 回溯原因，寻找关键变量")
    analysis["辨析因果分析"].append("  第二层: '这意味着什么…'(So this means) — 展望影响，找到行动切口")

    if any(w in text for w in ["都是", "全是", "都是因为", "全怪"]):
        analysis["辨析因果分析"].append("  [!] 检测到替罪羊思维 — '寻找事件背后的原因，而不是寻找事件背后的坏人'")

    if any(w in text for w in ["所有", "全部", "都", "没有一个"]):
        analysis["辨析因果分析"].append("[归纳法检查] 检测到全称判断 — 注意以偏概全风险: 个案不能代表全部")
    if any(w in text for w in ["如果", "假如", "那么"]):
        analysis["辨析因果分析"].append("[演绎法检查] 检测到条件推理 — 可尝试用三段论形式重建论证")

    key_var_found = any(w in text for w in ["关键", "核心", "最重要", "决定性", "根本原因", "主要因素"])
    if key_var_found:
        analysis["辨析因果分析"].append("  [OK] 正在寻找关键变量(X) — 在众多条件中找到决定性因素")
    else:
        analysis["辨析因果分析"].append("  [?] 是否找到了关键变量(X)？— 在众多变量中起决定性作用的因素是什么？")

    # 5. 锚定切口分析
    has_action = any(w in text for w in ["应该", "需要", "必须", "建议", "方案", "措施", "步骤", "计划"])
    if has_action:
        analysis["锚定切口分析"].append("[切口分析] 检测到行动方案:")
        analysis["锚定切口分析"].append("  步骤1(明确方向): 方案是否基于前面的因果分析？")
        analysis["锚定切口分析"].append("  步骤2(制订计划): 计划是否具体可执行？")
        analysis["锚定切口分析"].append("  步骤3(即时激励): 行动中是否有即时激励机制？")
        analysis["锚定切口分析"].append("  提示: 最重要的即时激励是'能完成' — 将大目标分解为小目标")
        analysis["锚定切口分析"].append("  思考: 行动是否足够简单以至于能立即开始？(从简单开始，小步试错)")
    else:
        analysis["锚定切口分析"].append("[切口分析] 缺少行动方案 — 深度思考必须转化为行动")
        analysis["锚定切口分析"].append("  锚定切口三步骤: 明确方向→制订计划→即时激励")

    analysis["锚定切口分析"].append("  参考505133法则: 没有50年洞见要有5年眼光→没有5年眼光要有1年梦想→至少知道自己每天最重要的三件要事")

    # 6. 不良思维习惯
    bad_habits = []
    if any(w in text for w in ["气死了", "太可恶", "太过分", "简直", "受不了", "恶心"]):
        bad_habits.append("用情绪宣泄代替辨析因果 — 情绪主导时无法冷静客观分析")
    if any(w in text for w in ["你们", "你们这些人", "你们总是", "你们从来"]):
        bad_habits.append("立场先行、对立思维 — 固守立场可能排斥其他观点")
    if len(text) < 30 and has_conclusion:
        bad_habits.append("未充分还原事实就急于下结论 — 可能导致对问题的理解偏离真相")
    if bad_habits:
        analysis["不良思维习惯"] = bad_habits

    # 7. 关键概念检查
    concept_check = []
    for c in found_concepts[:3]:
        concept_check.append(f"概念'{c}'是否有明确定义？— 定义是知识的开始，也是源思维的开始")
    if concept_check:
        analysis["关键概念检查"] = concept_check

    # 8. 综合深度思考评分
    score = 0
    depth_markers = []

    if has_evidence_words:
        score += 10
        depth_markers.append("有客观证据支撑")
    if has_essence_words:
        score += 20
        depth_markers.append("有因果分析")
    if total_cause_indicators >= 2:
        score += 15
        depth_markers.append("多元因果视角")
    if has_action:
        score += 15
        depth_markers.append("有行动方案")
    if found_concepts:
        score += 10
        depth_markers.append("涉及关键概念定义")
    if has_major_premise and has_minor_premise and has_conclusion:
        score += 10
        depth_markers.append("有三段论推理结构")
    if any(w in text for w in ["表面上", "实际上", "表面上看起来", "深层", "本质"]):
        score += 10
        depth_markers.append("区分表面与深层")
    if key_var_found:
        score += 10
        depth_markers.append("寻找关键变量")

    if total_cause_indicators == 0:
        score -= 15
    elif total_cause_indicators == 1 and len(text) > 50:
        score -= 5
    if has_internal_attribution:
        score -= 10

    score = max(0, min(100, score))

    if score >= 70:
        level = "深度思考"
        detail = "具备较强的深度思考特征，继续深化因果链分析和行动方案"
    elif score >= 40:
        level = "中等深度"
        detail = "有一定分析但深度不足，建议加强还原事实(定义关键概念)和辨析因果(寻找关键X)"
    else:
        level = "浅层思考"
        detail = "主要停留在现象层面，建议运用源思维三步法: 还原事实→辨析因果→锚定切口"

    analysis["深度思考评分"].append(f"源思维深度评分: {score}/100 — {level}")
    analysis["深度思考评分"].append(f"  特征: {', '.join(depth_markers) if depth_markers else '无明显深度思考特征'}")
    analysis["深度思考评分"].append(f"  建议: {detail}")

    return analysis
