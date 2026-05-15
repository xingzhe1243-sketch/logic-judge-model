"""批处理测试 — 验证文件批量分析"""
import json
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from run import _read_input, _batch_analyze


SAMPLE_TEXTS = [
    "因为所有人都应该享有自由，所以政府不应限制言论自由。",
    "大家都知道这是对的，因为专家都这么说。",
]


def test_batch_from_text_file():
    """测试从文本文件读取"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n".join(SAMPLE_TEXTS) + "\n")
        path = f.name
    try:
        texts = _read_input(path)
        assert len(texts) == 2
        assert texts[0] == SAMPLE_TEXTS[0]
        assert texts[1] == SAMPLE_TEXTS[1]
    finally:
        os.unlink(path)
    print("[OK] test_batch_from_text_file")


def test_batch_from_json_file():
    """测试从JSON文件读取"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(SAMPLE_TEXTS, f, ensure_ascii=False)
        path = f.name
    try:
        texts = _read_input(path)
        assert len(texts) == 2
    finally:
        os.unlink(path)
    print("[OK] test_batch_from_json_file")


def test_batch_happy_path():
    """测试批量分析正常执行"""
    results = _batch_analyze(SAMPLE_TEXTS[:1], modules=["formal_logic"])
    assert len(results) == 1
    assert "input" in results[0]
    assert "modules" in results[0]
    assert "formal_logic" in results[0]["modules"]
    print("[OK] test_batch_happy_path")


def test_batch_output_json():
    """测试批量分析输出JSON格式"""
    results = _batch_analyze(SAMPLE_TEXTS[:1], modules=["formal_logic"])
    output = json.dumps(results, ensure_ascii=False)
    assert isinstance(output, str)
    assert SAMPLE_TEXTS[0] in output
    print("[OK] test_batch_output_json")


if __name__ == "__main__":
    test_batch_from_text_file()
    test_batch_from_json_file()
    test_batch_happy_path()
    test_batch_output_json()
    print("\n" + "=" * 40)
    print("所有批处理测试通过!")
    print("=" * 40)
