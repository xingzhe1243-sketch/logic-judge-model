"""集成测试 — 验证 LogicJudgeModel 完整分析流程"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ljmodel import LogicJudgeModel, ReasoningEngine


SAMPLE_TEXT = "因为所有人都应该享有自由，所以政府不应限制言论自由。研究显示，言论自由能促进社会进步。"


def test_analyze_structure():
    """测试 analyze 返回结构"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    assert "input" in result
    assert result["input"] == SAMPLE_TEXT
    assert "modules" in result
    assert "synthesis" in result
    print("[OK] test_analyze_structure")


def test_all_modules_present():
    """测试所有分析模块都在结果中"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    modules = result["modules"]
    expected = [
        "llm_primary", "formal_logic", "critical_inquiry", "bias_detection",
        "argumentation", "elements_of_thought", "structured_analysis",
        "dialectical", "source_thinking", "simple_logic"
    ]
    for name in expected:
        assert name in modules, f"缺少模块: {name}"
        assert isinstance(modules[name], dict)
    print("[OK] test_all_modules_present")


def test_synthesis_fields():
    """测试综合合成字段"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    syn = result["synthesis"]
    assert "逻辑质量评分" in syn
    assert "主要发现" in syn
    assert "警告" in syn
    assert "行动建议" in syn
    assert isinstance(syn["主要发现"], list)
    assert isinstance(syn["警告"], list)
    assert isinstance(syn["行动建议"], list)
    print("[OK] test_synthesis_fields")


def test_synthesis_has_content():
    """测试合成内容非空"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    syn = result["synthesis"]
    assert len(syn["主要发现"]) >= 1
    assert len(syn["警告"]) >= 1
    assert len(syn["行动建议"]) >= 1
    print("[OK] test_synthesis_has_content")


def test_formal_logic_has_analysis():
    """测试形式逻辑模块有分析内容"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    fl = result["modules"]["formal_logic"]
    # 应检测到逻辑定律和论证结构
    assert len(fl.get("逻辑定律检查", [])) >= 1
    assert len(fl.get("论证结构", [])) >= 1
    print("[OK] test_formal_logic_has_analysis")


def test_critical_inquiry_has_analysis():
    """测试批判性质询模块有分析内容"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    ci = result["modules"]["critical_inquiry"]
    assert len(ci.get("论题识别", [])) >= 1
    assert len(ci.get("结论定位", [])) >= 1
    assert len(ci.get("歧义分析", [])) >= 1
    print("[OK] test_critical_inquiry_has_analysis")


def test_bias_detection_has_analysis():
    """测试偏见检测模块有分析内容"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    bd = result["modules"]["bias_detection"]
    assert len(bd.get("系统激活状态", [])) >= 1
    print("[OK] test_bias_detection_has_analysis")


def test_source_thinking_has_analysis():
    """测试源思维模块有分析内容"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False)
    st = result["modules"]["source_thinking"]
    assert len(st.get("层次诊断", [])) >= 1
    assert len(st.get("深度思考评分", [])) >= 1
    print("[OK] test_source_thinking_has_analysis")


def test_reasoning_engine():
    """测试推理引擎"""
    engine = ReasoningEngine()
    result = engine.syllogism_check(
        "所有人都会死",
        "苏格拉底是人",
        "苏格拉底会死"
    )
    assert "大前提" in result
    assert "小前提" in result
    assert "结论" in result
    assert "分析" in result
    print("[OK] test_reasoning_engine")


def test_reasoning_causal():
    """测试因果分析"""
    engine = ReasoningEngine()
    result = engine.analyze_causal("因为下雨所以地湿了")
    assert len(result["原因"]) >= 1
    assert len(result["结果"]) >= 1
    print("[OK] test_reasoning_causal")


def test_reasoning_deduce():
    """测试演绎推理"""
    engine = ReasoningEngine()
    result = engine.logical_deduce(
        ["如果下雨那么地湿", "下雨了"],
        "地湿了"
    )
    assert "演绎有效" in result
    print("[OK] test_reasoning_deduce")


def test_fallacy_rich_text():
    """测试富含谬误的文本"""
    judge = LogicJudgeModel(api_key="")
    fallacy_text = "大家都知道这是对的，因为专家都这么说。要么支持要么反对，没有中间选项。"
    result = judge.analyze(fallacy_text, verbose=False)
    # critical_inquiry 模块应检测到谬误
    ci = result["modules"]["critical_inquiry"]
    has_fallacy = any("诉诸公众" in s or "虚假两难" in s or "谬误" in s for s in ci.get("谬误检测", []))
    assert has_fallacy
    print("[OK] test_fallacy_rich_text")


def test_html_report():
    """测试HTML报告生成"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze("测试文本", verbose=False)
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    try:
        from ljmodel.report_html import generate_html_report
        html = generate_html_report(result, tmp.name)
        assert "<!DOCTYPE html>" in html
        assert "score-badge" in html or "评分" in html
        assert "综合分析报告" in html or "逻辑质量评分" in html
        tmp.flush()
        tmp.close()
        assert os.path.getsize(tmp.name) > 1000
    finally:
        os.unlink(tmp.name)
    print("[OK] test_html_report")


def test_selective_modules():
    """测试选择性运行模块"""
    judge = LogicJudgeModel(api_key="")
    result = judge.analyze(SAMPLE_TEXT, verbose=False, modules=["formal_logic"])
    modules = result["modules"]
    assert "formal_logic" in modules
    assert modules["formal_logic"] != {}
    # 其他模块不应运行
    assert "critical_inquiry" not in modules or modules["critical_inquiry"] == {}
    assert "bias_detection" not in modules or modules["bias_detection"] == {}
    # 合成应始终存在
    assert "synthesis" in result
    print("[OK] test_selective_modules")


if __name__ == "__main__":
    test_analyze_structure()
    test_all_modules_present()
    test_synthesis_fields()
    test_synthesis_has_content()
    test_formal_logic_has_analysis()
    test_critical_inquiry_has_analysis()
    test_bias_detection_has_analysis()
    test_source_thinking_has_analysis()
    test_reasoning_engine()
    test_reasoning_causal()
    test_reasoning_deduce()
    test_fallacy_rich_text()
    test_html_report()
    test_selective_modules()
    print("\n" + "=" * 40)
    print("所有集成测试通过!")
    print("=" * 40)
