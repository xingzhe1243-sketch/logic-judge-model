"""格式化报告输出"""


def _section_header(title: str):
    print(f"\n{'-' * 60}")
    print(f"  【{title}】")
    print(f"{'-' * 60}")


def _print_module_list(module_key: str, modules: dict, section_map: dict):
    """Print a module section if the module data exists."""
    data = modules.get(module_key, {})
    if not data:
        return
    for data_key, label in section_map:
        items = data.get(data_key, [])
        for item in items:
            if isinstance(item, dict):
                kw = item.get("keyword", item.get("bias", ""))
                desc = item.get("description", "")
                if kw:
                    print(f"  {'!' if '谬误' in data_key or '谬误' in label else '?'} {kw}: {desc[:200]}")
                else:
                    print(f"  {item.get('type', '')}: {item.get('description', '')[:200]}")
            elif isinstance(item, str):
                print(f"  {item}")
            elif isinstance(item, (int, float)):
                print(f"  {item}")


def print_report(result: dict):
    """格式化打印完整分析报告"""
    modules = result["modules"]
    synthesis = result["synthesis"]

    print(f"\n{'-' * 60}")
    print(f"  【综合评分】{synthesis['逻辑质量评分']}")
    print(f"{'-' * 60}")

    if synthesis["警告"]:
        print(f"\n  [!] 警告:")
        for w in synthesis["警告"]:
            print(f"    * {w}")

    # --- Module 1: 形式逻辑 ---
    fl = modules.get("formal_logic", {})
    if fl:
        _section_header("模块1 . 形式逻辑分析 — 逻辑学十五讲")
        for item in fl.get("逻辑定律检查", []):
            print(f"  * {item}")
        for item in fl.get("命题逻辑分析", []):
            print(f"  * {item}")
        for f in fl.get("谬误检测", []):
            print(f"  ! 谬误: {f['keyword']} — {f['description']}")
        for item in fl.get("论证结构", []):
            print(f"  $ {item}")
        for item in fl.get("悖论检测", []):
            print(f"  ? {item}")

    # --- Module 2: 批判性质询 ---
    ci = modules.get("critical_inquiry", {})
    if ci:
        _section_header("模块2 . 批判性质询 — 学会提问")
        for key, _ in [("论题识别", "论题"), ("结论定位", "结论"), ("理由提取", "理由"),
                        ("歧义分析", "歧义"), ("假设识别", "假设"), ("谬误检测", "谬误"),
                        ("证据评估", "证据"), ("替代原因", "替代原因"), ("数据检查", "数据"),
                        ("省略信息", "省略信息"), ("合理结论", "合理结论"),
                        ("思维模式诊断", "思维模式"), ("认知障碍检测", "认知障碍")]:
            items = ci.get(key, [])
            for item in items:
                if isinstance(item, str) and (item.startswith("  -") or item.startswith("  >>") or item.startswith("  [") or item.startswith("  建议") or item.startswith("  追问") or item.startswith("  提示")):
                    print(f"  {item}")
                elif isinstance(item, dict):
                    print(f"  * {item.get('type', '')}: {item.get('description', '')}")
                elif isinstance(item, str):
                    print(f"  * {item}")

    # --- Module 3: 认知偏见 ---
    bd = modules.get("bias_detection", {})
    if bd:
        _section_header("模块3 . 认知偏见检测 — 思考,快与慢")
        for item in bd.get("系统激活状态", []):
            print(f"  * {item}")
        for item in bd.get("认知放松/紧张检测", []):
            print(f"  * {item}")
        for b in bd.get("认知偏见检测", []):
            print(f"  ? 偏见: {b['bias']} (触发词: {b['trigger']})")
        for item in bd.get("前景理论分析", []):
            print(f"  $ 前景: {item}")
        for item in bd.get("记忆自我特征", []):
            print(f"  $ 记忆: {item}")
        for s in bd.get("判断建议", []):
            print(f"  -> {s}")

    # --- Module 4: 论证规则 ---
    ar = modules.get("argumentation", {})
    if ar:
        _section_header("模块4 . 论证规则评估 — 论证是一门学问")
        for item in ar.get("一般规则检查", []):
            print(f"  * {item}")
        print(f"  论证类型: {', '.join(ar.get('论证类型识别', []))}")
        for key in ["举例论证评估", "类比论证评估", "诉诸权威评估", "因果论证评估",
                    "演绎论证评估", "扩展论证评估", "议论写作评估", "公共辩论评估"]:
            items = ar.get(key, [])
            if items:
                for item in items:
                    print(f"  {item}")
        for item in ar.get("谬误检查", []):
            print(f"  [!] {item}")
        for item in ar.get("定义检查", []):
            print(f"  ? {item}")

    # --- Module 5: 思维元素 ---
    et = modules.get("elements_of_thought", {})
    if et:
        _section_header("模块5 . 思维元素分析 — 批判性思维工具")
        for key, val in et.get("思维8元素", {}).items():
            print(f"  * {key}: {val}")
        for item in et.get("自我中心检测", []):
            print(f"  ! 自我中心: {item}")
        for item in et.get("社会中心检测", []):
            print(f"  ! 社会中心: {item}")

    # --- Module 6: 结构化分析 ---
    sa = modules.get("structured_analysis", {})
    if sa:
        _section_header("模块6 . 结构化分析 — 麦肯锡逻辑思维")
        for item in sa.get("MECE检查", []):
            print(f"  * {item}")
        for item in sa.get("金字塔结构", []):
            print(f"  * {item}")

    # --- Module 7: 辩证系统 ---
    dl = modules.get("dialectical", {})
    if dl:
        _section_header("模块7 . 辩证系统分析 — 世界的逻辑")
        for item in dl.get("系统思维检查", []):
            print(f"  * {item}")
        for item in dl.get("资本/结构分析", []):
            print(f"  * {item}")
        for item in dl.get("辩证矛盾", []):
            print(f"  $ {item}")
        for item in dl.get("替代性思考", []):
            print(f"  ? {item}")

    # --- Module 8: 源思维 ---
    st = modules.get("source_thinking", {})
    if st:
        _section_header("模块8 . 源思维深度分析 — 源思维")
        for item in st.get("层次诊断", []):
            print(f"  * {item}")
        for item in st.get("思维模式诊断", []):
            print(f"  {'[!]' if '!' in item else '  *'} {item}")
        for item in st.get("还原事实分析", []):
            print(f"  $ {item}")
        for item in st.get("辨析因果分析", []):
            print(f"  -> {item}")
        for item in st.get("锚定切口分析", []):
            print(f"  ~ {item}")
        for item in st.get("不良思维习惯", []):
            print(f"  [!] {item}")
        for item in st.get("关键概念检查", []):
            print(f"  ? {item}")
        for item in st.get("深度思考评分", []):
            print(f"  {'[OK]' if '深度思考' in item else '  '} {item}")

    # --- Module 10: 简单逻辑 ---
    sl = modules.get("simple_logic", {})
    if sl:
        _section_header("模块10 . 简单逻辑深度分析 — 简单的逻辑学")
        for item in sl.get("比较与类比分析", []):
            print(f"  * {item}")
        for item in sl.get("论证基本形式识别", []):
            print(f"  * {item}")
        for item in sl.get("演绎/归纳判别", []):
            print(f"  * {item}")
        for item in sl.get("知识来源评估", []):
            print(f"  * {item}")
        for item in sl.get("非逻辑思维根源检测", []):
            print(f"  ! 非逻辑根源: {item}")
        for item in sl.get("谬误检测", []):
            print(f"  ! 谬误: {item['keyword']} — {item['description']}")
        for item in sl.get("论证四步评估", []):
            print(f"  $ {item}")

    # --- Module 9: LLM综合 ---
    llm_primary = modules.get("llm_primary", {})
    if llm_primary and "error" not in llm_primary:
        _section_header("模块9 . LLM综合分析 — DeepSeek (9本书框架)")
        dims = llm_primary.get("维度分析", {})
        dim_labels = {
            "形式逻辑": "逻辑学十五讲", "批判性质询": "学会提问",
            "认知偏见": "思考,快与慢", "论证规则": "论证是一门学问",
            "思维元素": "批判性思维工具", "结构化": "麦肯锡逻辑思维",
            "辩证系统": "世界的逻辑", "源思维": "源思维"
        }
        for dim_key, dim_label in dim_labels.items():
            dim_data = dims.get(dim_key, {})
            if dim_data:
                analysis_text = dim_data.get("分析", "")
                problems = dim_data.get("问题", [])
                if analysis_text or problems:
                    print(f"\n  > {dim_key} ({dim_label}):")
                    if analysis_text:
                        print(f"    {analysis_text[:300]}")
                    for p in problems:
                        print(f"    [!] {p}")
        suggestions = llm_primary.get("行动建议", [])
        if suggestions:
            print(f"\n  >> LLM行动建议:")
            for s in suggestions:
                print(f"    - {s}")

    # --- 知乎智囊团 ---
    ze = modules.get("zhihu_expert", {})
    if ze and ze.get("洞见"):
        _section_header("知乎智囊团 — 真实世界经验视角")
        print(f"  {ze['状态']}")
        for ins in ze["洞见"][:5]:
            print(f"    * {ins[:150]}")
        if ze.get("领域分布"):
            domains = ", ".join(d["domain"] for d in ze["领域分布"])
            print(f"  >> 相关知识领域: {domains}")

    # --- 规则引擎交叉验证摘要 ---
    rule_crosscheck = []
    for item in modules.get("formal_logic", {}).get("谬误检测", []):
        rule_crosscheck.append(f"谬误 {item['keyword']}")
    for item in modules.get("bias_detection", {}).get("认知偏见检测", []):
        rule_crosscheck.append(f"偏见: {item['bias']}")
    for item in modules.get("source_thinking", {}).get("思维模式诊断", []):
        if "风险" in item:
            rule_crosscheck.append("单一断定思维")
    if rule_crosscheck:
        _section_header("规则引擎交叉验证 — 关键词级别检测")
        for item in rule_crosscheck:
            print(f"  * {item}")

    # --- 智囊团协调报告 ---
    coord = result.get("coordination", {})
    if coord and coord.get("活跃专家数", 0) > 0:
        print(f"\n{'=' * 60}")
        print(f"  【智囊团协调报告】")
        print(f"{'=' * 60}")
        print(f"  活跃专家数: {coord['活跃专家数']} / 总发现数: {coord['总发现数']}")
        print(f"\n  专家分组活跃度:")
        for group, info in coord.get("专家分组活跃度", {}).items():
            status = " ✓" if info.get("active") else " ✗"
            mods = ", ".join(info.get("modules", [])) if info.get("modules") else "-"
            print(f"    {group}:{status} [{mods}]")
        if coord.get("共识点"):
            print(f"\n  多专家共识:")
            for c in coord["共识点"]:
                print(f"    * {c[:120]}")
        if coord.get("潜在分歧"):
            print(f"\n  潜在分歧:")
            for c in coord["潜在分歧"]:
                print(f"    * {c[:120]}")
        if coord.get("视角缺口"):
            print(f"\n  视角缺口:")
            for g in coord["视角缺口"]:
                print(f"    * {g}")

    print(f"\n{'=' * 60}")
    print(f"  分析完成")
    print(f"{'=' * 60}\n")
