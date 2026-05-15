"""基于《简单的逻辑学》的简明逻辑分析"""


def analyze_simple_logic(text: str, kb: dict) -> dict:
    """逻辑基本定律、论证结构与谬误分析"""
    sl = kb["simple_logic"]
    analysis = {
        "比较与类比分析": [], "论证基本形式识别": [],
        "演绎/归纳判别": [], "非逻辑思维根源检测": [],
        "谬误检测": [], "知识来源评估": [],
        "论证四步评估": []
    }

    # 比较与类比分析
    comparison_notes = []
    has_comparison = any(w in text for w in ["比较", "相似", "类似", "如同", "好比", "像", "同样"])
    if has_comparison:
        comparison_notes.append("检测到比较/类比表述 — 注意共享特性的重要性和数量是否足够")
        if ("不同" in text or "差别" in text) and ("相同" in text or "相似" in text):
            comparison_notes.append("部分相似+部分不同 — 关注关键特性的重要性而非相似特征的数量")
        if any(w in text for w in ["就像", "正如", "好比", "相当于"]):
            comparison_notes.append("存在类比推理 — 类比不能证明结论，只能提供可能性")
        if not any(w in text for w in ["但是", "然而", "不过", "区别", "差异"]):
            comparison_notes.append("注意: 比较时是否遗漏了反面的重要差异特征？")
    else:
        comparison_notes.append("未检测到明显的比较/类比论证")
    analysis["比较与类比分析"] = comparison_notes

    # 论证基本形式识别
    forms_notes = []
    if "并且" in text or "而且" in text or "同时" in text:
        forms_notes.append("联言论证(A·B): 各联言支须全部为真才能成立")
    if "或者" in text or "要么" in text:
        if "或者...或者..." in text or text.count("或者") >= 2:
            forms_notes.append("选言论证(A∨B): 区分相容(至少一真)与不相容(仅一真)")
    if "如果" in text:
        if "那么" in text:
            forms_notes.append("条件论证(A→B): 检查是否肯定前件(有效)或肯定后件(无效)")
        else:
            forms_notes.append("条件语句: 缺'那么' — 推理关系可能不完整")
    if "只有" in text and "才" in text:
        forms_notes.append("必要条件推理: 只有A才B — 否定前件推出否后(有效), 肯定后件推出前件(有效)")
    if text.count("是") >= 3 and text.count("所有") >= 1:
        forms_notes.append("可能包含三段论推理 — 检查中项是否至少周延一次")
    analysis["论证基本形式识别"] = forms_notes

    # 演绎/归纳判别
    di_notes = []
    if any(w in text for w in ["所有", "每个", "一切", "凡是"]):
        if any(w in text for w in ["有些", "部分", "个别", "这个"]):
            di_notes.append("从全称到特称推理(演绎) — 若全称前提真，则特称结论必然真")
    if any(w in text for w in ["有些", "几个", "部分", "案例", "例子"]):
        if any(w in text for w in ["所有", "总是", "都", "一切"]):
            di_notes.append("从特称到全称推理(归纳) — 结论不必然，注意以偏概全风险")
    if any(w in text for w in ["观察到", "实验中", "样本", "统计", "数据显示", "反复"]):
        di_notes.append("归纳推理: 基于观察/数据 — 检查样本代表性和范围")
    if "假设" in text or "猜想" in text or "推测" in text:
        if any(w in text for w in ["验证", "证实", "证明", "数据", "证据"]):
            di_notes.append("假设-检验模式: 假设驱动的归纳推理 — 注意假设是否可证伪")
    analysis["演绎/归纳判别"] = di_notes

    # 非逻辑思维根源检测
    roots_detected = []
    if any(w in text for w in ["没有真相", "无所谓真假", "什么都不确定"]):
        roots_detected.append("极端怀疑论倾向 — 声称没有真相，自相矛盾")
    if any(w in text for w in ["没人知道", "永远无法知道", "说不清楚", "无从判断"]):
        roots_detected.append("逃避性不可知论 — 用无知为借口回避判断")
    if any(w in text for w in ["全都是假的", "都是骗人的", "全是套路", "没一个好东西"]):
        roots_detected.append("玩世不恭 — 预设性悲观判断，未分析先下结论")
    if any(w in text for w in ["不可能", "绝对不行", "别无选择", "只能这样", "想都别想"]):
        roots_detected.append("眼界狭窄 — 自我设限，拒绝考虑其他可能性")
    if any(w in text for w in ["我气就气在", "我受不了", "太可恶", "太可恨"]):
        roots_detected.append("情感遮蔽 — 强烈情绪可能干扰理性判断")
    if any(w in text for w in ["你输了", "我赢了", "你错了", "你根本不懂"]):
        roots_detected.append("论证异化为争吵 — 从探寻真相转向击败对手")
    if any(w in text for w in ["我坚信", "我深信", "我凭良心说"]):
        roots_detected.append("真诚陷阱 — 诚实的信念不等于正确的论证")
    analysis["非逻辑思维根源检测"] = roots_detected

    # 谬误检测 — 初级：原有书名关键词匹配
    detected_fallacies = []
    fallacy_map_sl = {
        "误用传统": "非形式谬误 — 因'过去如此'而认为必须如此",
        "以暴易暴": "非形式谬误 — 以已发生的错误为当前错误辩护",
        "以笑饰非": "关联性谬误 — 以嘲笑代替严肃回应",
        "以泪掩过": "关联性谬误 — 以博取同情代替论证",
        "无力反驳": "非形式谬误 — 对方不能证伪即证明",
        "两难陷阱": "非形式谬误 — 只给两种选择，隐藏其他选项",
        "民主谬误": "非形式谬误 — 以多数人认同作为正确标准",
        "压制理性": "非形式谬误 — 用强制代替理性说服",
        "质的量化": "非形式谬误 — 将不可量化的事物强行量化",
        "以出身论英雄": "非形式谬误 — 以来源的类别性质推定个体的性质",
        "止于分析": "非形式谬误 — 能分解却不能重组综合",
        "简化主义": "非形式谬误 — 把整体等同于部分之和",
        "分类错误": "非形式谬误 — 将事物归入错误的类别",
        "避免结论": "非形式谬误 — 用推理来否认得出结论的可能性",
        "简化推理": "非形式谬误 — 过度简化复杂现实",
        "情感误导": "非形式谬误 — 选择性忽略与信念抵触的信息",
        "功利误导": "非形式谬误 — 为达目的不择手段",
        "无关前提": "关联性谬误 — 前提与结论毫不相关",
    }
    for keyword, desc in fallacy_map_sl.items():
        if keyword in text:
            detected_fallacies.append({"keyword": keyword, "description": desc})

    # 谬误检测 — 进阶：使用统一注册表进行名称匹配（补充新增谬误类型）
    from ..fallacy_registry import match_name_fallacies
    existing_names = {d["keyword"] for d in detected_fallacies}
    for f in match_name_fallacies(text, category_filter=[
        "关联性谬误", "假设性谬误", "非逻辑思维根源"
    ]):
        # 避免重复：检查中文名是否已被检测
        all_names = {f.chinese_name} | set(a.strip() for a in f.chinese_name.split("/") if a.strip())
        if not all_names & existing_names:
            detected_fallacies.append({
                "keyword": f.chinese_name,
                "description": f"{f.category} — {f.description[:100]}"
            })
            existing_names.add(f.chinese_name)

    # 忽略限定谬误检测
    detected_fallacies.extend(_detect_secundum_quid_sl(text))

    analysis["谬误检测"] = detected_fallacies

    # 知识来源评估
    source_notes = []
    if "根据" in text and ("研究表明" in text or "研究显示" in text or "调查" in text):
        source_notes.append("知识来源: 研究/数据 — 需评估方法论和研究范围")
    if "专家" in text or "教授" in text or "学者" in text:
        source_notes.append("知识来源: 专家意见 — 专家必须在相关领域内才有权威性")
    if "我" in text and ("经历" in text or "经验" in text or "觉得" in text):
        source_notes.append("知识来源: 个人经验 — 样本量有限，不能作为普遍结论的依据")
    if "大家都" in text or "所有人" in text or "人人都" in text:
        source_notes.append("知识来源: 普遍共识声称 — 注意民主谬误风险")
    if "直觉" in text or "本能" in text:
        source_notes.append("知识来源: 直觉 — 直觉不能作为可靠论证的基础")
    analysis["知识来源评估"] = source_notes

    # 四步论证评估
    eval_notes = []
    has_premise = any(w in text for w in ["因为", "由于", "基于", "根据", "鉴于"])
    has_conclusion = any(w in text for w in ["所以", "因此", "由此可见", "总之", "结论"])
    if has_premise and has_conclusion:
        eval_notes.append("步骤1(结构): 包含前提和结论 — 真实论证")
    elif has_premise and not has_conclusion:
        eval_notes.append("步骤1(结构): 有前提无结论 — 论证不完整")
    elif not has_premise and has_conclusion:
        eval_notes.append("步骤1(结构): 有结论无前提 — 仅为观点，非论证")
    else:
        eval_notes.append("步骤1(结构): 无法识别论证结构 — 可能为单纯描述")

    fact_markers = sum(1 for w in ["数据", "研究", "证据", "史实", "统计"] if w in text)
    if fact_markers >= 2:
        eval_notes.append("步骤2(真实性): 有事实性支撑 — 建议进一步核查证据来源")
    else:
        eval_notes.append("步骤2(真实性): 前提真实性待确认 — 需检查是否基于可验证信息")
    if has_premise and has_conclusion:
        eval_notes.append("步骤3(相关性): 需判断前提是否直接支持结论 — 排除无关前提干扰")
    has_cond = any(w in text for w in ["如果", "只有", "只要", "假设"])
    if has_cond:
        if not ("所以" in text or "因此" in text):
            eval_notes.append("步骤4(有效性): 有条件推理但未给出结论 — 需明确推理结果")
    analysis["论证四步评估"] = eval_notes

    return analysis


def _detect_secundum_quid_sl(text: str) -> list[dict]:
    """检测「忽略限定」谬误 — 前提带限定条件，结论悄悄去掉限定"""
    found = []
    qualifiers = ["正常", "通常", "一般", "大多数", "大部分", "多数", "许多"]
    predicate_particles = "都|会|总是|有|可以|要|能"
    common_verbs = "喜欢|讨厌|擅长|适合|需要|具有|具备|拥有|热爱|反对|支持|认为|觉得|知道|明白|了解"

    import re
    for marker in ["所以", "因此", "由此可见", "故"]:
        if marker not in text:
            continue
        idx = text.rindex(marker)
        premise_area = text[:idx]
        conclusion_area = text[idx:]

        for qual in qualifiers:
            pattern = re.compile(
                re.escape(qual) + r"(\w{1,8})(?:" + predicate_particles + r"|" + common_verbs + r")"
            )
            for m in pattern.finditer(premise_area):
                noun = m.group(1)
                if qual not in conclusion_area:
                    found.append({
                        "keyword": "忽略限定",
                        "description": (
                            f"前提中「{qual}{noun}」带有限定词「{qual}」，"
                            f"结论中去掉了该限定，构成忽略限定谬误。"
                            f"{qual}{noun}的特性不一定适用于所有{noun}。"
                        )
                    })
                    break

    return found
