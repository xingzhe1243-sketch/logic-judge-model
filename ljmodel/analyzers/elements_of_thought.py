"""基于《批判性思维工具》的思维元素分析"""


def analyze_elements_of_thought(text: str, kb: dict) -> dict:
    """思维8元素 + 通用理智标准 + 自我中心/社会中心思维"""
    tools = kb["critical_thinking_tools"]
    analysis = {
        "思维8元素": {}, "理智标准评价": {},
        "自我中心检测": [], "社会中心检测": [],
        "思维发展建议": []
    }

    elements_summary = {
        "目的": "文本试图达成什么目标？需要进一步明确",
        "问题": "文本试图回答的核心问题是什么？",
        "信息": f"文本包含 {len(text)} 个字符的信息量",
        "解释": "文本如何组织信息并得出结论？",
        "概念": "需要提取核心概念并检查定义",
        "假设": "未明确陈述的前提假设是什么？",
        "结果": "如果接受此推理，后果是什么？",
        "观点": "这是从什么视角出发的论述？",
    }
    for elem in tools["elements_of_thought"]:
        label = elem.split(":")[0]
        if label in elements_summary:
            analysis["思维8元素"][label] = elements_summary[label]

    for std in tools["intellectual_standards"]:
        name = std.split(":")[0]
        analysis["理智标准评价"][name] = "需要进一步检查"

    # 自我中心思维检测
    egocentric_signs = []
    if any(w in text for w in ["我认为", "我觉得", "我的观点", "我坚信", "我始终"]):
        egocentric_signs.append("大量第一人称判断 — 可能存在自利偏误，用他人视角检视")
    if any(w in text for w in ["我当然", "我一直认为", "正合我意"]):
        egocentric_signs.append("自我验证倾向 — 选择性关注支持己见的证据")
    if any(w in text for w in ["这是对的", "我没错", "事实如此", "不接受反驳"]):
        egocentric_signs.append("防御性表述 — 受到质疑时启动情绪防御而非理性回应")
    if any(w in text for w in ["显然", "毫无疑问", "不用想都知道"]):
        egocentric_signs.append("自以为是 — 高估自身判断的确定性")

    # 社会中心思维检测
    sociocentric_signs = []
    if any(w in text for w in ["众所周知", "人人都知道", "这是常识"]):
        sociocentric_signs.append("诉诸群体共识 — '常识'可能是内化的群体信念，需检查有没有独立验证")
    if any(w in text for w in ["我们", "咱们", "国人", "中华民族"]):
        sociocentric_signs.append("群体认同表述 — 注意'我们vs他们'的框架可能影响客观判断")
    if any(w in text for w in ["外国人", "西方", "东方", "发达国家"]):
        sociocentric_signs.append("文化/民族群体参照 — 检查是否存在文化中心主义")
    if any(w in text for w in ["学术界", "专家认为", "研究表明", "权威"]):
        sociocentric_signs.append("学术/领域依赖 — '权威共识'不等于真理，需检查证据本身")

    analysis["自我中心检测"] = egocentric_signs if egocentric_signs else ["未检测到明显自我中心倾向"]
    analysis["社会中心检测"] = sociocentric_signs if sociocentric_signs else ["未检测到明显社会中心倾向"]

    analysis["思维发展建议"] = [
        "养成对论证进行系统性分析的习惯(阶段2->阶段3)",
        "持续练习批判性思维工具(阶段3->阶段4)"
    ]

    return analysis
