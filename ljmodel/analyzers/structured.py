"""基于麦肯锡的结构化分析"""


def analyze_structured(text: str, kb: dict) -> dict:
    """MECE / 金字塔 / 逻辑树 / 四象限分析"""
    mc = kb["mckinsey_logic"]
    analysis = {
        "MECE检查": [], "金字塔结构": [],
        "逻辑树建议": [], "优先级评估": [],
        "问题解决评估": [], "逻辑技巧检查": [],
        "背景分析": [], "系统性检查": []
    }

    # MECE检查
    mece_issues = []
    if "分为" in text or "分类" in text or "类型" in text:
        mece_issues.append("检测到分类表述 — 检查是否满足MECE")
        mece_issues.append("  追问: 各类别之间是否'相互独立'(无重叠)？")
        mece_issues.append("  追问: 各类别之和是否'完全穷尽'(无遗漏)？")
    classification_words = ["一方面", "另一方面", "第一种", "第二种", "首先", "其次", "再次"]
    found_class = [w for w in classification_words if w in text]
    if found_class:
        mece_issues.append(f"检测到分类标记: {', '.join(found_class)} — 检查分类是否满足MECE")
    if not mece_issues:
        mece_issues.append("未检测到明确分类 — 若涉及分析，建议用MECE原则检查")
    analysis["MECE检查"] = mece_issues

    # 金字塔结构
    pyramid = []
    if "结论" in text or "因此" in text or "所以" in text:
        pyramid.append("结论先行: 文本包含结论 — 建议将核心结论放在开篇")
        pyramid.append("  检查: 结论是否有下一层论据支撑？")
    else:
        pyramid.append("文本无明确结论 — 金字塔原则要求结论先行")

    if sum(1 for w in ["第一", "第二", "第三", "首先", "其次", "再者"] if w in text) >= 2:
        pyramid.append("检测到分层论述 — 检查同层之间的MECE和上下层的论证关系")
    conclusion_count = sum(1 for w in ["所以", "因此", "结论", "总之"] if w in text)
    premise_count = sum(1 for w in ["因为", "由于", "基于"] if w in text)
    if conclusion_count >= 1 and premise_count >= 1:
        pyramid.append("纵向关系: 结论在上，论据在下 — 符合金字塔结构")
    analysis["金字塔结构"] = pyramid

    # 逻辑树
    tree_notes = []
    if any(w in text for w in ["为什么", "原因是什么", "根源", "根本原因"]):
        tree_notes.append("why-why分析: 反复追问'为什么'直达根本原因")
    if any(w in text for w in ["如果", "那么", "假设"]):
        tree_notes.append("假设树: 检测到假设表述 — 可构建假设验证框架")
    if any(w in text for w in ["选择", "选项", "方案", "替代", "可能"]):
        tree_notes.append("决策树: 检测到多个选项 — 可构建决策树评估各选项")
    if not tree_notes:
        tree_notes.append("建议: 对复杂问题使用逻辑树(议题树/假设树/决策树)进行MECE分解")
    analysis["逻辑树建议"] = tree_notes

    # 优先级评估
    priority_notes = []
    if "紧急" in text or "重要" in text:
        priority_notes.append("检测到优先级判断 — 可套用四象限矩阵:")
        priority_notes.append("  - 重要且紧急: 立即处理")
        priority_notes.append("  - 重要不紧急: 计划处理(战略投入)")
        priority_notes.append("  - 紧急不重要: 委托/快速处理")
        priority_notes.append("  - 不紧急不重要: 减少/不做")
        priority_notes.append("  核心原则: 优先处理'重要不紧急'可从根本上减少紧急事务")
    else:
        priority_notes.append("未检测到明确的优先级判断 — 建议对多项任务用四象限矩阵排序")
    analysis["优先级评估"] = priority_notes

    # 问题解决过程
    ps_notes = []
    if "问题" in text or "挑战" in text or "困难" in text:
        ps_notes.append("检测到问题导向的论述 — 建议按以下步骤:")
        ps_notes.append("  步骤1: 定义问题 — 明确问题的边界和本质")
        ps_notes.append("  步骤2: 分解问题 — 用MECE将大问题拆分为小问题")
        ps_notes.append("  步骤3: 提出假设 — 针对每个子问题提出假设")
        ps_notes.append("  步骤4: 验证假设 — 用事实和数据验证")
        ps_notes.append("  步骤5: 得出结论 — 基于验证结果形成判断")
    if any(w in text for w in ["经验", "过去", "传统"]):
        ps_notes.append("注意: 警惕经验主义 — 过去成功的经验在新环境中可能不适用")
    analysis["问题解决评估"] = ps_notes

    # 逻辑技巧
    skill_notes = []
    if "概念" in text or "定义" in text or "含义" in text:
        skill_notes.append("澄清概念: 对关键概念进行了界定 — 良好思维习惯")
    if any(w in text for w in ["前提", "假设", "假定"]):
        skill_notes.append("质疑前提: 检测到对前提的检视 — 建议检查前提是否成立")
    if any(w in text for w in ["角度", "视角", "方面", "层面"]):
        skill_notes.append("多角度思考: 从多个视角审视问题 — 避免固化思维")
    if not skill_notes:
        skill_notes.append("建议运用麦肯锡逻辑技巧: 澄清概念/质疑前提/多角度思考/结构化表达")
    analysis["逻辑技巧检查"] = skill_notes

    # 背景分析
    context_notes = []
    if any(w in text for w in ["背景", "环境", "条件", "原因", "历史", "现状"]):
        context_notes.append("检测到背景/环境分析 — 良好的问题意识")
        context_notes.append("  追问: 问题的来源是什么？利益相关方有哪些？")
        context_notes.append("  追问: 有哪些约束条件和限制因素？")
    else:
        context_notes.append("建议: 分析问题背景(context) — 理解问题产生的环境和条件")
    analysis["背景分析"] = context_notes

    # 系统性检查(7S)
    sys_notes = []
    if any(w in text for w in ["战略", "策略", "目标", "定位"]):
        sys_notes.append("涉及战略维度 — 7S中的'战略'要素")
    if any(w in text for w in ["组织", "结构", "架构", "部门"]):
        sys_notes.append("涉及结构维度 — 7S中的'结构'要素")
    if any(w in text for w in ["流程", "制度", "系统", "机制", "体系"]):
        sys_notes.append("涉及系统维度 — 7S中的'系统'要素")
    if any(w in text for w in ["文化", "价值观", "使命", "愿景"]):
        sys_notes.append("涉及共享价值观 — 7S中的'共享价值观'(核心要素)")
    if any(w in text for w in ["管理", "风格", "领导", "沟通"]):
        sys_notes.append("涉及风格维度 — 7S中的'风格'要素")
    if any(w in text for w in ["人才", "员工", "团队", "能力", "培训"]):
        sys_notes.append("涉及人员/技能维度 — 7S中的'人员'和'技能'要素")
    if sys_notes:
        sys_notes.append("7S原则: 所有要素必须相互匹配，组织才能有效运转")
    else:
        sys_notes.append("建议对复杂问题使用7S模型进行系统性分析")
    analysis["系统性检查"] = sys_notes

    return analysis
