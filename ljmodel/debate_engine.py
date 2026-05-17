"""多模型智囊团深度辩论系统

输入: 解剖分析（模式A）+ 共鸣拓扑（模式B）+ 全部书籍 + 知乎
输出: 多专家辩论后的综合裁决

架构:
  第二阶段分析 — 踩在解剖模型的结果之上做更高维度的综合判断

  5 位专家基于全部输入材料进行三阶段辩论:
  逻辑卫士     — 形式逻辑/简单逻辑/论证规则
  认知侦探     — 认知偏见/批判性质询/批判性思维工具
  系统分析师   — 麦肯锡结构化/辩证系统
  源思维师     — 源思维 (还原事实→辨析因果→锚定切口)
  博弈策略家   — 规则解剖模型 (利益/权力/策略/公理)
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


# =============================================================================
# 专家定义
# =============================================================================

EXPERT_DEFS = {
    "逻辑卫士": {
        "domain": "形式逻辑、简单逻辑、论证规则",
        "books": ["逻辑学十五讲", "简单的逻辑学", "论证是一门学问"],
        "focus": "推理有效性、逻辑谬误、论证结构、概念清晰度",
    },
    "认知侦探": {
        "domain": "认知偏见、批判性质询、批判性思维工具",
        "books": ["思考,快与慢", "学会提问", "批判性思维工具"],
        "focus": "隐藏假设、认知偏差、思维元素、替代解释",
    },
    "系统分析师": {
        "domain": "麦肯锡结构化思维、辩证系统分析",
        "books": ["麦肯锡教我的逻辑思维", "世界的逻辑"],
        "focus": "结构性约束、MECE、系统动力、矛盾分析",
    },
    "源思维师": {
        "domain": "源思维",
        "books": ["源思维"],
        "focus": "还原事实→辨析因果→锚定切口、多元因果思维",
    },
    "博弈策略家": {
        "domain": "规则解剖模型",
        "books": ["规则解剖模型 V4.0"],
        "focus": "利益格局、权力动态、公理冲突、策略评估",
    },
}


def _format_analysis_context(dissection_result: dict = None,
                              resonance_result: dict = None) -> str:
    """将解剖分析和共鸣拓扑的结构化结果格式化为上下文文本"""
    parts = []

    if dissection_result:
        parts.append("【解剖分析结果（模式A — 博弈分析）】")
        mode_judge = dissection_result.get("模式判定", {})
        if mode_judge:
            parts.append(f"模式判定: {mode_judge.get('依据', '')} (置信度: {mode_judge.get('置信度', '')})")

        gm = dissection_result.get("博弈地图", {})
        if gm:
            gm_lines = ["博弈地图:"]
            for k, v in gm.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, list):
                    for item in v:
                        gm_lines.append(f"  {k}: {item}")
                elif isinstance(v, str):
                    gm_lines.append(f"  {k}: {v}")
            parts.append("\n".join(gm_lines))

        risks = dissection_result.get("风险计算", {})
        if risks:
            risk_lines = ["风险扫描:"]
            for k, v in risks.items():
                if not k.startswith("_"):
                    risk_lines.append(f"  {k}: {v}")
            parts.append("\n".join(risk_lines))

        conflicts = dissection_result.get("公理冲突检查", {})
        if conflicts:
            parts.append(f"活跃公理: {'、'.join(conflicts.get('活跃公理列表', []))}")
            for c in conflicts.get("冲突列表", []):
                if isinstance(c, dict):
                    parts.append(f"公理冲突: {c.get('公理A','')} vs {c.get('公理B','')} → {c.get('裁决','')}")

        actions = dissection_result.get("行动指令", [])
        if actions:
            parts.append("行动指令: " + "; ".join(actions))

        preds = dissection_result.get("预测", [])
        if preds:
            for p in preds:
                parts.append(f"预测 [置信度:{p.get('置信度','?')}]: {p.get('text','')[:200]}")

    if resonance_result:
        if parts:
            parts.append("")
        parts.append("【共鸣拓扑结果（模式B — 方向导航）】")
        pain = resonance_result.get("痛苦分类", {})
        if pain:
            parts.append(f"痛苦分类: {pain.get('类型', '未分类')}")
            parts.append(f"状态: {pain.get('状态', '')}")
            parts.append(f"建议: {pain.get('建议操作', '')}")
        for s in resonance_result.get("感知扫描", []):
            parts.append(f"感知: {s}")
        for f in resonance_result.get("场域检查", []):
            parts.append(f"场域: {f}")
        ladder = resonance_result.get("梯子检查", {})
        if isinstance(ladder, dict):
            for k, v in ladder.items():
                if isinstance(v, list):
                    for item in v:
                        parts.append(f"[{k}] {item}")
                else:
                    parts.append(f"[{k}] {v}")

    return "\n".join(parts) if parts else "（无预分析结果）"


def _format_zhihu_context(kb: dict) -> str:
    """从知识库提取知乎相关信息"""
    ze = kb.get("zhihu_expert", {})
    if not ze:
        return ""
    parts = []
    if ze.get("洞见"):
        parts.append("知乎高赞洞见样例:")
        for ins in ze["洞见"][:5]:
            parts.append(f"  • {ins[:200]}")
    if ze.get("领域分布"):
        domains = [d["domain"] for d in ze["领域分布"]]
        parts.append(f"覆盖领域: {', '.join(domains)}")
    if ze.get("状态"):
        parts.append(f"状态: {ze['状态']}")
    return "\n".join(parts)


def _format_all_books_summary(kb: dict) -> str:
    """动态生成全部书籍的摘要列表"""
    # 更有意义的描述映射（仅对已知书籍）
    known_descriptions = {
        "formal_logic": "形式逻辑/谬误/悖论",
        "dual_system": "双系统认知/偏见/前景理论",
        "critical_inquiry": "批判性质询10问/证据评估",
        "simple_logic": "逻辑定律/非逻辑根源",
        "argumentation_rules": "50条论证规则大全",
        "critical_thinking_tools": "思维8元素/理智标准/思维特质",
        "mckinsey_logic": "MECE/金字塔/逻辑树",
        "dialectical_system": "辩证系统/资本循环/空间修复",
        "source_thinking": "还原事实→辨析因果→锚定切口",
        "dissection_model": "博弈分析/公理系统/共鸣拓扑",
        "black_swan": "极端斯坦/黑天鹅事件/叙述谬误/火鸡问题",
        "capital": "商品拜物教/剩余价值/资本积累/利润率下降",
        "clear_thinking_art": "清晰思考/决策框架/认知陷阱",
        "county_cadre": "基层运作/官僚体系/中国政治",
        "criminal_psychology": "犯罪心理/犯罪行为分析",
        "crowd": "群体心理/乌合之众/领袖煽动",
        "dales_carnegie": "人际关系/影响力/沟通技巧",
        "deliberate_practice": "刻意练习/专业技能/心智表征",
        "deng_xiaoping_era": "改革开放/邓小平时代/中国转型",
        "evolutionary_psychology": "进化心理学/生存策略/择偶心理",
        "influence": "影响力六大原则/说服心理学",
        "intimate_relationship": "亲密关系/依恋理论/冲突管理",
        "manipulation_psychology": "操纵心理学/情感控制/防御",
        "mindset": "成长型思维/固定型思维/心智模式",
        "my_cheating_life": "骗婚现象/两性关系/社会伦理",
        "power_48": "权力48法则/博弈策略/权谋",
        "psychology_of_money": "金钱心理学/财富观念/投资行为",
        "sapiens": "认知革命/农业革命/科学革命/人类史",
        "selfish_gene": "自私的基因/进化论/利他行为",
        "skin_in_the_game": "非对称风险/风险共担/反脆弱",
        "three_strategy_classics": "孙子兵法/六韬/三略/战略学",
        "twenty_first_capital": "21世纪资本论/不平等/财富分配",
        "ugly_chinese": "国民性批判/文化心理/社会观察",
        "wealth_of_nations": "国富论/市场经济/分工/价值理论",
        "world_logic": "世界逻辑/多维思维/认知框架",
        "zhihu_expert": "知乎集体智慧/真实世界经验",
        "ask_questions": "批判性提问/论证分析/关键问题",
        "logic_lectures": "逻辑学系统讲义/推理方法",
        "mckinsey": "麦肯锡方法论/商业分析策略",
        "thinking_fast_slow": "思考快与慢完整版/双系统/偏见",
    }
    summaries = []
    for key in sorted(kb.keys()):
        if key == "zhihu_expert":
            continue
        name = kb[key].get("source", key)[:40]
        desc = known_descriptions.get(key, "")
        concepts = len(kb[key].get("core_concepts", []))
        tag = f" [{concepts}概念]" if concepts else ""
        summaries.append(f"  • {name}{tag}")

    # 知乎单独列出
    ze = kb.get("zhihu_expert", {})
    if ze:
        answers = len(ze.get("洞见", []))
        summaries.append(f"  • 知乎集体智慧 [{answers}条高赞回答]")

    return "可用书籍知识库 (" + str(len(kb)) + " 本):\n" + "\n".join(summaries)


def _build_expert_system_prompt(name: str, text: str, kb: dict,
                                 analysis_context: str,
                                 zhihu_context: str,
                                 books_summary: str) -> str:
    """为指定专家构建完整的系统提示词"""
    expert = EXPERT_DEFS[name]

    # 提取该专家相关的领域知识
    kb_snippets = []

    if name == "逻辑卫士":
        fl = kb.get("formal_logic", {})
        if fl:
            laws = fl.get("laws", [])
            if laws:
                kb_snippets.append("逻辑基本定律: " + "; ".join(laws))
            fal = fl.get("fallacies", [])
            if fal:
                names = [f["keyword"] for f in fal[:10]]
                kb_snippets.append("常检测的谬误: " + ", ".join(names))
        al = kb.get("simple_logic", {})
        if al:
            roots = al.get("non_logical_roots", [])
            if roots:
                kb_snippets.append("非逻辑思维根源: " + "; ".join(roots))
        ar = kb.get("argumentation_rules", {})
        if ar:
            gr = ar.get("general_rules", [])
            if gr:
                kb_snippets.append("论证一般规则: " + "; ".join(gr))

    elif name == "认知侦探":
        ds = kb.get("dual_system", {})
        if ds:
            biases = ds.get("biases", [])
            if biases:
                names = [b["bias"] for b in biases]
                kb_snippets.append("认知偏见清单: " + ", ".join(names))
        ci = kb.get("critical_inquiry", {})
        if ci:
            cq = ci.get("core_questions", [])
            if cq:
                kb_snippets.append("批判性质询10问: " + "; ".join(cq))
            obs = ci.get("obstacles", [])
            if obs:
                kb_snippets.append("思维障碍: " + "; ".join(obs))
        ct = kb.get("critical_thinking_tools", {})
        if ct:
            elem = ct.get("elements_of_thought", [])
            if elem:
                kb_snippets.append("思维8元素: " + "; ".join(e[:40] for e in elem))

    elif name == "系统分析师":
        ml = kb.get("mckinsey_logic", {})
        if ml:
            principles = ml.get("logical_thinking_foundations", [])
            if principles:
                kb_snippets.append("结构化思维原则: " + "; ".join(principles))
        dl = kb.get("dialectical_system", {})
        if dl:
            dp = dl.get("dialectical_principles", [])
            if dp:
                kb_snippets.append("辩证分析原则: " + "; ".join(dp))
            dims = dl.get("analytical_dimensions", [])
            if dims:
                kb_snippets.append("分析维度: " + "; ".join(dims))

    elif name == "源思维师":
        st = kb.get("source_thinking", {})
        if st:
            core = st.get("core_model", {})
            if core:
                desc = core.get("description", "")
                kb_snippets.append(f"核心模型: {desc}")
            habits = st.get("bad_thinking_habits", [])
            if habits:
                kb_snippets.append("不良思维习惯: " + "; ".join(habits))

    elif name == "博弈策略家":
        dm = kb.get("dissection_model", {})
        if dm:
            mode_a = dm.get("mode_a", {})
            if mode_a:
                axioms = mode_a.get("axioms", [])
                for ax in axioms:
                    kb_snippets.append(f"公理 {ax.get('id','')}: {ax.get('text','')}")
                rules = mode_a.get("rules", [])
                for r in rules[:8]:
                    kb_snippets.append(f"规则{r.get('id','')}({r.get('category','')}): {r.get('text','')}")

    knowledge_context = "\n".join(kb_snippets) if kb_snippets else "（该领域知识库内容）"

    # 构建完整的 user prompt — 包含所有输入材料
    user_prompt_parts = [
        f"请从【{name}】的视角对以下问题进行深度分析。",
        f"",
        f"=== 原始问题 ===",
        f"{text}",
        f"",
        f"=== 规则解剖模型的分析结果（第一阶段分析）===",
        f"以下内容是解剖引擎（模式A）和/或共鸣拓扑（模式B）已经产生的结构化分析，",
        f"请基于这些分析结果做更高层面的综合判断，而非从零开始分析：",
        f"",
        analysis_context,
    ]

    if zhihu_context:
        user_prompt_parts.extend([
            f"",
            f"=== 知乎集体智慧参考 ===",
            zhihu_context,
        ])

    user_prompt_parts.extend([
        f"",
        f"=== {name} 的专业领域知识 ===",
        knowledge_context,
        f"",
        f"=== 全部可用书籍知识库 ===",
        books_summary,
        f"",
        f"=== 分析要求 ===",
        f"1. 首先阅读并理解规则解剖模型已经得出的分析结果",
        f"2. 从你的专业视角，对这些结果做出评判：哪些认同？哪些遗漏了什么？",
        f"3. 结合全部书籍知识库和你的领域专长，给出超越第一阶段的深层洞见",
        f"4. 特别关注其他领域专家可能会忽略的盲区",
        f"5. 如果规则解剖分析有遗漏或偏差，明确指出",
        f"6. 最终要触及问题的底层结构，而非停留在表面",
        f"",
        f"=== 输出格式 ===",
        f"【对解剖分析的评价】你对第一阶段分析结果的评价（认同/补充/纠正）",
        f"【你的核心判断】一句话总结你的立场",
        f"【深度分析】3-5条从你视角出发的深度分析",
        f"【盲区提醒】其他专家可能忽略的 1-2 个关键点",
        f"【底层追问】穿透到最底层的问题是什么？",
    ])

    return "\n".join(user_prompt_parts)


class DebateEngine:
    """多模型智囊团深度辩论系统

    接收解剖分析（模式A）和/或共鸣拓扑（模式B）的结构化结果作为输入，
    结合全部书籍知识库和知乎集体智慧，让 5 位领域专家进行三阶段辩论，
    最终由主持人综合裁决，产出高于第一阶段的深度结论。
    """

    def __init__(self, kb: dict, llm_client=None, llm_model: str = None,
                 doubao_client=None, doubao_model: str = None):
        self.kb = kb
        self.client = llm_client
        self.model = llm_model or "deepseek-chat"
        self.doubao_client = doubao_client
        self.doubao_model = doubao_model or "doubao-pro-32k"

    def debate(self, text: str,
               dissection_result: dict = None,
               resonance_result: dict = None) -> dict:
        """执行完整的三阶段辩论

        Args:
            text: 用户原始问题
            dissection_result: 解剖分析结果（模式A），可选
            resonance_result: 共鸣拓扑结果（模式B），可选

        Returns:
            dict: 辩论完整结果
        """
        if not self._has_llm():
            return self._fallback(text, dissection_result, resonance_result)

        # 预计算输入材料
        analysis_context = _format_analysis_context(dissection_result, resonance_result)
        zhihu_context = _format_zhihu_context(self.kb)
        books_summary = _format_all_books_summary(self.kb)

        print("  [辩论开始] 5 位专家基于解剖分析结果进行深度辩论...")
        print(f"  [输入材料] 解剖分析={'✓' if dissection_result else '✗'} "
              f"共鸣拓扑={'✓' if resonance_result else '✗'} "
              f"知乎={'有' if zhihu_context else '无'} "
              f"书籍={len([k for k in self.kb if k != 'zhihu_expert'])}本")

        # 阶段 1: 每位专家基于全部材料做开场分析（5 路并行）
        openings = self._phase_openings(text, analysis_context, zhihu_context, books_summary)

        # 阶段 2: 交叉辩论（5 路并行）
        print("  [交叉辩论] 专家互相挑战...")
        cross_exams = self._phase_cross_examination(text, openings)

        # 阶段 3: 主持人综合
        print("  [综合裁决] 主持人整合全部辩论...")
        synthesis = self._phase_synthesis(text, openings, cross_exams)

        return {
            "模式": "多模型智囊团深度辩论（基于解剖分析+全部书籍+知乎）",
            "专家数": len(EXPERT_DEFS),
            "输入材料": {
                "解剖分析": dissection_result is not None,
                "共鸣拓扑": resonance_result is not None,
                "知乎": bool(zhihu_context),
                "书籍数": len([k for k in self.kb if k != "zhihu_expert"]),
            },
            "开场陈述": {n: {"opening": o} for n, o in openings.items()},
            "交叉辩论": {n: {"cross": c} for n, c in cross_exams.items()},
            "综合裁决": synthesis,
        }

    def _has_llm(self) -> bool:
        return self.client is not None

    def _llm_chat(self, system_prompt: str, user_prompt: str,
                  temperature: float = 0.4, max_tokens: int = 3500) -> str:
        if not self.client:
            return ""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"[LLM调用异常: {e}]"

    def _phase_openings(self, text: str, analysis_context: str,
                        zhihu_context: str, books_summary: str) -> dict:
        """阶段 1: 所有专家并行做开场分析"""
        results = {}
        with ThreadPoolExecutor(max_workers=len(EXPERT_DEFS)) as pool:
            fut = {}
            for name in EXPERT_DEFS:
                system_prompt = _build_expert_system_prompt(
                    name, text, self.kb, analysis_context, zhihu_context, books_summary
                )
                fut[pool.submit(
                    self._llm_chat, system_prompt,
                    f"从{name}的视角，基于所有输入材料做出深度分析。"
                )] = name

            for f in as_completed(fut):
                name = fut[f]
                try:
                    results[name] = f.result()
                    print(f"    ✓ {name} 开场分析完成")
                except Exception as e:
                    results[name] = f"[异常: {e}]"
                    print(f"    ✗ {name} 异常: {e}")

        return results

    def _phase_cross_examination(self, text: str, openings: dict) -> dict:
        """阶段 2: 所有专家并行做交叉辩论"""
        others_per_expert = {}
        for name in EXPERT_DEFS:
            others = {}
            for other_name, content in openings.items():
                if other_name == name:
                    continue
                others[other_name] = content[:1200]
            others_per_expert[name] = others

        results = {}
        with ThreadPoolExecutor(max_workers=len(EXPERT_DEFS)) as pool:
            fut = {}
            for name in EXPERT_DEFS:
                others_text_parts = []
                for oname, otext in others_per_expert[name].items():
                    others_text_parts.append(f"── {oname} ──\n{otext}")
                others_text = "\n\n".join(others_text_parts)

                prompt = f"""你是 <终极逻辑判断模型·智囊团辩论系统> 的 {name}。

现在进入【交叉辩论】环节。你已经看到了其他 {len(EXPERT_DEFS)-1} 位专家的开场分析：

{others_text}

你的任务：
1. 质疑/挑战其他专家分析中不成立或不完整的部分
2. 指出其他专家之间的分歧，给出你的判断
3. 认同并深化其他专家中你认为正确的分析
4. 如果其他专家的分析让你修正了自己原先的观点，承认并说明为什么
5. 最终，指出你认为主持人必须关注的 1-2 个最核心的问题

输出格式：
【我认同的】
【我质疑的】
【分歧判断】
【修正】（如有）
【主持人必须关注】"""
                fut[pool.submit(self._llm_chat, prompt,
                                f"交叉辩论环节：请{name}对同行做出回应。")] = name

            for f in as_completed(fut):
                name = fut[f]
                try:
                    results[name] = f.result()
                    print(f"    ✓ {name} 交叉辩论完成")
                except Exception as e:
                    results[name] = f"[异常: {e}]"
                    print(f"    ✗ {name} 交叉辩论异常: {e}")

        return results

    def _phase_synthesis(self, text: str, openings: dict, cross_exams: dict) -> str:
        """阶段 3: 主持人综合裁决"""
        all_debate_parts = []
        for name in EXPERT_DEFS:
            opening = openings.get(name, "")
            cross = cross_exams.get(name, "")
            all_debate_parts.append(f"===== {name} 开场分析 =====")
            all_debate_parts.append(opening[:1500] if opening else "(无)")
            if cross:
                all_debate_parts.append(f"===== {name} 交叉辩论 =====")
                all_debate_parts.append(cross[:1500])

        debates_text = "\n\n".join(all_debate_parts)

        prompt = f"""你是 <终极逻辑判断模型·智囊团辩论系统> 的【主持人/综合裁决者】。

原始问题: {text}

以下是 5 位领域专家基于规则解剖分析结果+全部书籍知识库+知乎集体智慧的完整辩论记录：

{debates_text}

你的核心任务：穿透所有专家的分析，勘破问题的底层结构。

具体要求：
1. 【核心共识】所有专家达成一致的关键判断是什么？
2. 【关键分歧】专家间无法统一的根本分歧是什么？分歧的根源（视角差异/信息缺失/底层价值观不同）？
3. 【深层洞见】穿透所有分析后，你看到了什么每位专家单独看不到的东西？
4. 【底层结构】这个问题的本质是什么？表面争论之下的真正博弈/矛盾/结构性约束是什么？
5. 【超越解剖分析】相比第一阶段（规则解剖模型）的结论，这次辩论产生了哪些新的、更深的认知？
6. 【行动启示】基于全部深度分析，对问题提出者最有价值的行动指引（不超过3条）

输出格式：
【核心共识】
• ...

【关键分歧】
• ...

【深层洞见】
• ...

【底层结构】
• ...

【超越第一阶段的新认知】
• ...

【行动启示】
• ..."""
        return self._llm_chat(prompt,
                              "请综合全部辩论，给出最终裁决。",
                              temperature=0.3,
                              max_tokens=4000)

    def _fallback(self, text: str,
                  dissection_result: dict = None,
                  resonance_result: dict = None) -> dict:
        """无 API Key 时降级"""
        insights = []
        for name, expert in EXPERT_DEFS.items():
            domain_keywords = {
                "逻辑卫士": ["推理", "逻辑", "谬误", "论证", "矛盾", "概念"],
                "认知侦探": ["偏见", "假设", "认知", "思维", "证据", "心理"],
                "系统分析师": ["系统", "结构", "MECE", "组织", "制度", "环境"],
                "源思维师": ["事实", "原因", "因果", "本质", "维度", "深层"],
                "博弈策略家": ["利益", "博弈", "风险", "策略", "权力", "筹码"],
            }
            matched = [k for k in domain_keywords.get(name, []) if k in text]
            if matched:
                insights.append({
                    "专家": name,
                    "领域": expert["domain"],
                    "匹配信号": matched,
                    "覆盖书籍": expert["books"],
                })

        return {
            "模式": "多模型智囊团深度辩论（规则降级版 — 未检测到 LLM）",
            "专家数": len(EXPERT_DEFS),
            "说明": "设置 DEEPSEEK_API_KEY 以启用 LLM 驱动的多模型辩论",
            "知识覆盖": insights,
            "输入材料": {
                "解剖分析": dissection_result is not None,
                "共鸣拓扑": resonance_result is not None,
            },
            "综合裁决": "【规则降级】无 LLM 客户端，无法进行深度辩论。请配置 API Key 后重试。",
        }


def print_debate_report(result: dict):
    """打印辩论报告"""
    mode = result.get("模式", "")
    print(f"\n{'=' * 60}")
    print(f"  多模型智囊团深度辩论")
    print(f"  模式: {mode}")
    print(f"{'=' * 60}")

    if "规则降级" in mode:
        insights = result.get("知识覆盖", [])
        if insights:
            for ins in insights:
                print(f"  [{ins['专家']}] ({ins['领域']}) → {', '.join(ins['匹配信号'])}")
        print(f"\n  {result.get('综合裁决', '')}")
        print(f"\n{'=' * 60}")
        return

    # 输入材料摘要
    materials = result.get("输入材料", {})
    if materials:
        print(f"  输入材料: 解剖分析={'✓' if materials.get('解剖分析') else '✗'} "
              f"共鸣拓扑={'✓' if materials.get('共鸣拓扑') else '✗'} "
              f"书籍={materials.get('书籍数', 0)}本")

    # 开场陈述
    openings = result.get("开场陈述", {})
    if openings:
        print(f"\n{'-' * 60}")
        print(f"  第一轮 · 专家开场分析（基于全部输入材料）")
        print(f"{'-' * 60}")
        for name, content in openings.items():
            text = (content.get("opening", "") or "")[:500]
            print(f"\n  ▶ {name}")
            for line in text.split("\n"):
                if line.strip():
                    print(f"    {line.strip()}")

    # 交叉辩论
    cross = result.get("交叉辩论", {})
    if cross:
        print(f"\n{'-' * 60}")
        print(f"  第二轮 · 交叉辩论")
        print(f"{'-' * 60}")
        for name, content in cross.items():
            text = (content.get("cross", "") or "")[:350]
            if text:
                print(f"\n  ▶ {name}")
                for line in text.split("\n"):
                    if line.strip():
                        print(f"    {line.strip()}")

    # 综合裁决
    synthesis = result.get("综合裁决", "")
    if synthesis:
        print(f"\n{'-' * 60}")
        print(f"  主持人 · 综合裁决")
        print(f"{'-' * 60}")
        for line in synthesis.split("\n"):
            if line.strip():
                print(f"  {line.strip()}")

    print(f"\n{'-' * 60}")
    print(f"  辩论结束")
    print(f"{'-' * 60}")
    print()
