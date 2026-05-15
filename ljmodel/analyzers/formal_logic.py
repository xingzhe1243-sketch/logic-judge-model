"""基于《逻辑学十五讲》的形式逻辑分析"""


def analyze_formal_logic(text: str, kb: dict) -> dict:
    """形式逻辑分析—命题逻辑/词项逻辑/谓词逻辑/归纳逻辑/谬误论"""
    principles = kb["formal_logic"]
    analysis = {
        "逻辑定律检查": [],
        "推理类型识别": [],
        "命题逻辑分析": [],
        "谬误检测": [],
        "论证结构": [],
        "悖论检测": [],
        "反驳策略建议": []
    }

    # 检查逻辑基本定律
    law_checks = []
    if any(w in text for w in ["概念", "意义上"]):
        if "偷换" in text or "混淆" in text:
            law_checks.append("违反同一律: 检测到概念混淆或偷换")
        else:
            law_checks.append("同一律检查: 涉及概念表述，建议检查概念是否前后保持同一")
    else:
        law_checks.append("同一律检查: 未检测到明显违反同一律")

    contradict_pairs = [
        ("是", "不是"), ("肯定", "否定"), ("真", "假"),
        ("存在", "不存在"), ("有", "没有")
    ]
    found_contradiction = False
    for a, b in contradict_pairs:
        if a in text and b in text:
            last_a = text.rfind(a)
            last_b = text.rfind(b)
            if abs(last_a - last_b) < 200:
                found_contradiction = True
                law_checks.append(f"矛盾律: 检测到'{a}'和'{b}'同时出现 — 检查是否自相矛盾")
                break
    if not found_contradiction:
        law_checks.append("矛盾律检查: 未发现明显自相矛盾")

    if ("既不是" in text and "也不是" in text) or "不肯定也不否定" in text or "模棱两可" in text:
        law_checks.append("排中律: 可能出现'两不可'错误 — 对矛盾命题需明确表态")

    if "因为" in text or "由于" in text:
        law_checks.append("充足理由律: 有理由陈述 — 需要检查理由是否真实且能推出结论")
    else:
        law_checks.append("充足理由律: 没有明确给出理由 — 论证可能缺乏支撑")
    analysis["逻辑定律检查"] = law_checks

    # 识别推理类型
    inferences = [
        {"type": "演绎推理", "desc": "从一般到特殊，前提真则结论必真(必然性推理)"},
        {"type": "归纳推理", "desc": "从特殊到一般，前提真结论可能真(或然性推理)"},
        {"type": "类比推理", "desc": "从特殊到特殊"},
        {"type": "溯因推理", "desc": "从结果推原因"}
    ]
    analysis["推理类型识别"] = inferences

    # 命题逻辑分析
    pl_analysis = []
    if "并且" in text or "而且" in text or "不仅" in text:
        pl_analysis.append("联言推理: 检测到'并且/而且' — 联言支须全部为真")
    if "或者" in text or "要么" in text:
        pl_analysis.append("选言推理: 检测到'或者/要么' — 区分相容选言(至少一真)和不相容选言(仅一真)")
    has_conditional = False
    if "如果" in text and "那么" in text:
        pl_analysis.append("假言推理(充分条件): 检测到'如果...那么' — 肯定前件可推出后件,否定后件可推出前件否定")
        has_conditional = True
    if "只有" in text and "才" in text:
        pl_analysis.append("假言推理(必要条件): 检测到'只有...才' — 否定前件推出后件否定,肯定后件推出前件")
        has_conditional = True
    if "无论" in text or "无论如何" in text or ("如果" in text and text.count("如果") >= 2):
        pl_analysis.append("可能涉及二难推理: 注意前提是否一致(不能同时依赖矛盾的前提)")
    if has_conditional:
        if "所以" in text or "因此" in text:
            pl_analysis.append("建议: 检查推理模式是有效(肯定前件/否定后件)还是无效(否定前件/肯定后件)")
    analysis["命题逻辑分析"] = pl_analysis

    # 谬误检测 — 初级：原有书名关键词匹配
    detected_fallacies = []
    fallacy_map = {
        "人身攻击": "关联性谬误 — 攻击人而非论点",
        "诉诸情感": "关联性谬误 — 用情绪替代推理",
        "诉诸权威": "关联性谬误 — 权威不是证据",
        "诉诸无知": "关联性谬误 — 无法证伪即真",
        "偷换概念": "歧义性谬误 — 概念前后不一致",
        "循环论证": "假设性谬误 — 窃取论题",
        "非黑即白": "假设性谬误 — 忽略中间选项",
        "滑坡谬误": "假设性谬误 — 夸大连锁反应",
        "以偏概全": "假设性谬误 — 轻率概括",
        "稻草人": "关联性谬误 — 歪曲对方观点再驳斥",
        "虚假原因": "假设性谬误 — 把相关当因果",
        "以先后为因果": "假设性谬误 — 先后关系不等于因果关系",
        "复杂问语": "假设性谬误 — 问句包含虚假预设",
        "诉诸强力": "关联性谬误 — 以威胁代替说理",
        "诉诸公众": "关联性谬误 — 以多数代替论证",
        "赌徒谬误": "假设性谬误 — 独立事件受历史影响",
        "预期理由": "假设性谬误 — 用未证实的命题作论据",
        "合举/合成": "歧义性谬误 — 部分属性推整体属性",
        "分举/分解": "歧义性谬误 — 整体属性推每个部分都有",
        "以全概偏": "假设性谬误 — 通则无条件应用于特殊情况",
    }
    for keyword, desc in fallacy_map.items():
        if keyword in text:
            detected_fallacies.append({"keyword": keyword, "description": desc})

    # 谬误检测 — 进阶：使用统一注册表进行名称匹配（补充新增谬误类型）
    from ..fallacy_registry import match_name_fallacies
    existing_names = {d["keyword"] for d in detected_fallacies}
    for f in match_name_fallacies(text, category_filter=[
        "形式谬误", "歧义性谬误", "关联性谬误", "假设性谬误"
    ]):
        all_names = {f.chinese_name} | set(a.strip() for a in f.chinese_name.split("/") if a.strip())
        if not all_names & existing_names:
            detected_fallacies.append({
                "keyword": f.chinese_name,
                "description": f"{f.category} — {f.description[:100]}"
            })
            existing_names.add(f.chinese_name)
    analysis["谬误检测"] = detected_fallacies

    # 论证结构分析
    structure_notes = []
    if "所以" in text or "因此" in text or "结论" in text:
        structure_notes.append("结论标记: 检测到结论性表述")
    if "因为" in text or "由于" in text or "基于" in text:
        structure_notes.append("前提标记: 检测到前提/理由表述")
    if structure_notes:
        analysis["论证结构"].append("论证结构可识别: 建议明确区分前提和结论")
    else:
        analysis["论证结构"].append("论证结构不清晰: 建议使用'因为/所以'等标记明确推理关系")

    has_premise = any(w in text for w in ["因为", "由于", "基于", "根据"])
    has_conclusion = any(w in text for w in ["所以", "因此", "由此可见", "总之", "结论"])
    if has_premise and has_conclusion:
        analysis["论证结构"].append("完整论证: 包含前提和结论，可进行有效性分析")
    elif has_premise and not has_conclusion:
        analysis["论证结构"].append("不完整论证: 有前提无明确结论")
    elif not has_premise and has_conclusion:
        analysis["论证结构"].append("不完整论证: 有结论无明确前提")

    if "鲁迅" in text and text.count("鲁迅") > 1:
        analysis["论证结构"].append("注意: '鲁迅的著作不是一天能读完的, 《孔乙己》是鲁迅的著作' — 集合与非集合意义混淆")

    # 悖论检测
    paradox_notes = []
    if any(w in text for w in ["这句话是假的", "自指", "自我指涉"]):
        paradox_notes.append("检测到自指悖论 — 如'这句话是假的'会导致矛盾等价式")
    if "所有" in text and "集合" in text and "包含" in text:
        paradox_notes.append("可能涉及集合论悖论 — 检查自指性定义")
    analysis["悖论检测"] = paradox_notes

    if has_premise and has_conclusion:
        analysis["反驳策略建议"] = [
            "反驳结论: 举反例或构造相反论证(最强反驳)",
            "反驳前提: 指出前提虚假(但不等同于驳倒结论)",
            "反驳推理: 指出推不出(论证有缺陷但结论仍可能真)"
        ]

    # 忽略限定谬误检测 — 前提中有限定词但结论中悄悄去掉
    qualifier_fallacies = _detect_secundum_quid(text)
    analysis["谬误检测"].extend(qualifier_fallacies)

    return analysis


def _detect_secundum_quid(text: str) -> list[dict]:
    """检测「忽略限定」谬误 (secundum quid / a dicto simpliciter)

    识别模式：
      前提对某类事物带有限定条件（正常/通常/一般/大多数），
      结论却将限定条件去掉，当作无条件的一般命题使用。

      也检测「以全概偏」(accident fallacy / dicto simpliciter)：
      将一般规则不加分辨地应用于可能例外的特殊子类。
    """
    found = []

    qualifiers = ["正常", "通常", "一般", "大多数", "大部分", "多数", "许多"]
    # 跟在名词后的常见谓词（都/会/总是/有 + 常见动词）
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
            # 模式1: "正常/大多数 X 都/会/有 ...Y" → 结论中限定词消失
            pattern = re.compile(
                re.escape(qual) + r"(\w{1,8})(?:" + predicate_particles + r"|" + common_verbs + r")"
            )
            for m in pattern.finditer(premise_area):
                noun = m.group(1)
                if qual not in conclusion_area:
                    # 提取谓词（匹配到的最后一个字之后的内容）
                    match_end = m.end()
                    pred_snippet = text[match_end:match_end+20].split("，")[0].split("。")[0].split("的")[0]
                    found.append({
                        "keyword": "忽略限定",
                        "description": (
                            f"前提中「{qual}{noun}」带有限定词「{qual}」，"
                            f"但结论中去掉了该限定，构成忽略限定谬误。"
                            f"{qual}{noun}的特性不一定适用于所有{noun}。"
                        )
                    })
                    break

    return found
