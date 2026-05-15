"""测试各个分析模块"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ljmodel.knowledge_base import KNOWLEDGE_BASE
from ljmodel.analyzers import (
    analyze_formal_logic, analyze_critical_inquiry, analyze_biases,
    analyze_argumentation, analyze_elements_of_thought, analyze_structured,
    analyze_dialectical, analyze_source_thinking, analyze_simple_logic,
)


SAMPLE_TEXT = "因为所有人都应该享有自由，所以政府不应限制言论自由。研究显示，言论自由能促进社会进步。"

SAMPLE_FALLACY = "要么支持我们的政策，要么就是反对进步。大家都知道这是个好政策，所以我们应该继续执行。"

SAMPLE_ANALOGY = "就像汽车需要定期保养一样，人的身体也需要定期检查。研究表明定期体检能及早发现疾病。"


def test_formal_logic():
    """测试形式逻辑分析"""
    result = analyze_formal_logic(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "逻辑定律检查" in result
    assert "谬误检测" in result
    assert "论证结构" in result
    assert len(result["逻辑定律检查"]) >= 1
    print("[OK] test_formal_logic")


def test_formal_logic_fallacy():
    """测试谬误检测"""
    # 检测文本明确提及谬误名称的情形
    fallacy_named_text = "这个论证存在诉诸公众谬误和滑坡谬误"
    result = analyze_formal_logic(fallacy_named_text, KNOWLEDGE_BASE)
    assert len(result["谬误检测"]) >= 1
    print("[OK] test_formal_logic_fallacy")


def test_critical_inquiry_fallacy():
    """测试批判性质询的谬误检测"""
    result = analyze_critical_inquiry(SAMPLE_FALLACY, KNOWLEDGE_BASE)
    has_fallacy = any("诉诸公众" in s or "谬误" in s for s in result.get("谬误检测", []))
    assert has_fallacy
    print("[OK] test_critical_inquiry_fallacy")


def test_critical_inquiry():
    """测试批判性质询"""
    result = analyze_critical_inquiry(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "论题识别" in result
    assert "结论定位" in result
    assert "理由提取" in result
    print("[OK] test_critical_inquiry")


def test_biases():
    """测试认知偏见检测"""
    biased_text = "毫无疑问，这个方案绝对正确。我已经投入了大量时间，不能半途而废。"
    result = analyze_biases(biased_text, KNOWLEDGE_BASE)
    assert "认知偏见检测" in result
    assert "系统激活状态" in result
    print("[OK] test_biases")


def test_argumentation():
    """测试论证规则评估"""
    result = analyze_argumentation(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "一般规则检查" in result
    assert "论证类型识别" in result
    print("[OK] test_argumentation")


def test_elements_of_thought():
    """测试思维元素分析"""
    result = analyze_elements_of_thought(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "思维8元素" in result
    assert "理智标准评价" in result
    assert "自我中心检测" in result
    print("[OK] test_elements_of_thought")


def test_structured():
    """测试结构化分析"""
    structured_text = "问题分为三个方面：第一是成本，第二是效率，第三是质量。"
    result = analyze_structured(structured_text, KNOWLEDGE_BASE)
    assert "MECE检查" in result
    assert "金字塔结构" in result
    print("[OK] test_structured")


def test_dialectical():
    """测试辩证系统分析"""
    result = analyze_dialectical(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "系统思维检查" in result
    assert "资本/结构分析" in result
    print("[OK] test_dialectical")


def test_source_thinking():
    """测试源思维深度分析"""
    result = analyze_source_thinking(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "层次诊断" in result
    assert "思维模式诊断" in result
    assert "深度思考评分" in result
    print("[OK] test_source_thinking")


def test_simple_logic():
    """测试简单逻辑分析"""
    result = analyze_simple_logic(SAMPLE_TEXT, KNOWLEDGE_BASE)
    assert "比较与类比分析" in result
    assert "论证基本形式识别" in result
    assert "论证四步评估" in result
    print("[OK] test_simple_logic")


def test_simple_logic_fallacy():
    """测试简单逻辑谬误检测"""
    result = analyze_simple_logic(SAMPLE_FALLACY, KNOWLEDGE_BASE)
    assert "谬误检测" in result
    print("[OK] test_simple_logic_fallacy")


def test_analogy_analysis():
    """测试类比论证"""
    result = analyze_simple_logic(SAMPLE_ANALOGY, KNOWLEDGE_BASE)
    assert len(result["比较与类比分析"]) >= 1
    print("[OK] test_analogy_analysis")


def test_empty_text():
    """测试空文本或极短文本"""
    empty = "是"
    for analyzer in [
        analyze_formal_logic, analyze_critical_inquiry, analyze_biases,
        analyze_argumentation, analyze_structured, analyze_dialectical,
        analyze_source_thinking, analyze_simple_logic,
    ]:
        result = analyzer(empty, KNOWLEDGE_BASE)
        assert isinstance(result, dict)
    print("[OK] test_empty_text")


def test_emotional_text():
    """测试情绪化文本的偏见检测"""
    emotional = "太可怕了！简直令人发指！这种行为绝对不可接受！"
    result = analyze_biases(emotional, KNOWLEDGE_BASE)
    # 情绪化文本应被检测到系统1激活
    system_status = result.get("系统激活状态", [])
    has_emotional = any("情绪化" in s for s in system_status)
    assert has_emotional
    print("[OK] test_emotional_text")


def test_causal_text():
    """测试因果文本"""
    causal = "研究数据显示，A导致B的发生率显著上升。因为A增加了C的活性，所以B更容易发生。"
    result = analyze_critical_inquiry(causal, KNOWLEDGE_BASE)
    assert len(result.get("替代原因", [])) >= 1
    print("[OK] test_causal_text")


if __name__ == "__main__":
    test_formal_logic()
    test_formal_logic_fallacy()
    test_critical_inquiry_fallacy()
    test_critical_inquiry()
    test_biases()
    test_argumentation()
    test_elements_of_thought()
    test_structured()
    test_dialectical()
    test_source_thinking()
    test_simple_logic()
    test_simple_logic_fallacy()
    test_analogy_analysis()
    test_empty_text()
    test_emotional_text()
    test_causal_text()
    print("\n" + "=" * 40)
    print("所有分析器测试通过!")
    print("=" * 40)
