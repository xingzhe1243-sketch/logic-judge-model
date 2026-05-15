"""基于《世界的逻辑》的辩证系统分析"""


def analyze_dialectical(text: str, kb: dict) -> dict:
    """辩证系统分析·马克思主义方法论·资本空间逻辑"""
    analysis = {
        "系统思维检查": [], "资本/结构分析": [],
        "辩证矛盾": [], "替代性思考": []
    }

    if any(w in text for w in ["系统", "整体", "全局", "生态", "结构"]):
        analysis["系统思维检查"].append("具备系统思维视角 — 关注了整体关联")
    else:
        analysis["系统思维检查"].append("可能缺乏系统性思考，建议从整体结构和关系角度审视")

    if any(w in text for w in ["历史", "发展", "过程", "演变", "长期"]):
        analysis["系统思维检查"].append("具有历史/过程视角 — 将事物放在发展过程中理解")

    structural = []
    if any(w in text for w in ["资本", "市场", "经济", "利润", "成本"]):
        structural.append("涉及资本/经济维度 — 检查:谁拥有资源?资本循环是否顺畅?")
    if any(w in text for w in ["权力", "政治", "制度", "政策", "阶级"]):
        structural.append("涉及权力/制度维度 — 检查:谁受益?谁受损?现存安排服务于谁?")
    if any(w in text for w in ["全球化", "国际", "发达国家", "发展中"]):
        structural.append("涉及空间/全球维度 — 可能包含不平衡发展的逻辑，检查中心和边缘关系")
    if any(w in text for w in ["资源", "环境", "土地", "自然"]):
        structural.append("涉及自然资源维度 — 检查:是否涉及剥夺性积累?公共资源被私有化?")
    if any(w in text for w in ["创新", "技术", "数字", "互联网"]):
        structural.append("涉及技术/时空压缩维度 — 新技术是否加速了资本周转?是否改变了时空感知?")
    if any(w in text for w in ["泡沫", "危机", "崩溃", "风险", "债务"]):
        structural.append("涉及危机/虚拟资本维度 — 金融资本是否脱离实际生产?泡沫根源何在?")

    if structural:
        analysis["资本/结构分析"] = structural
    else:
        analysis["资本/结构分析"].append("建议引入结构性和权力维度进行分析")

    contradictions = []
    if "但是" in text or "然而" in text or "不过" in text:
        contradictions.append("检测到转折关系 — 可能蕴含辩证矛盾或内在张力")
    if any(w in text for w in ["一方面", "另一方面"]):
        contradictions.append("两面性表述 — 体现了矛盾的统一和斗争")
    if any(w in text for w in ["悖论", "矛盾", "困境", "两难"]):
        contradictions.append("明确承认矛盾 — 矛盾是发展的动力而非需要消除的缺陷")
    analysis["辩证矛盾"] = contradictions if contradictions else ["未检测到明确的辩证矛盾表述"]

    alternatives = []
    if any(w in text for w in ["不可避免", "别无选择", "唯一出路", "必须"]):
        alternatives.append("宿命论/必然性表述 — 辩证地看: 当前安排是历史的、可替代的")
    alternatives.append("建议: 追问'替代方案是什么?替代方案服务于谁的利益?'")
    analysis["替代性思考"] = alternatives

    return analysis
