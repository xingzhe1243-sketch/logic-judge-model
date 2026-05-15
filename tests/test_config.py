"""配置测试 — 验证 YAML 配置加载"""
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ljmodel.config import _load_yaml, _load_config


SAMPLE_YAML = """
api_key: test-key-123
model: gpt-4
base_url: https://custom.api.com/v1
log_level: DEBUG
modules:
  - formal_logic
  - critical_inquiry
server:
  host: 127.0.0.1
  port: 9999
"""


def test_load_yaml():
    """测试 YAML 文件加载"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(SAMPLE_YAML)
        path = f.name
    try:
        data = _load_yaml(path)
        assert data["api_key"] == "test-key-123"
        assert data["model"] == "gpt-4"
        assert data["log_level"] == "DEBUG"
        assert "formal_logic" in data["modules"]
        assert data["host"] == "127.0.0.1"  # server 子字段已展平
        assert data["port"] == 9999
    finally:
        os.unlink(path)
    print("[OK] test_load_yaml")


def test_load_yaml_nonexistent():
    """测试不存在的 YAML 文件"""
    data = _load_yaml("/nonexistent/file.yaml")
    assert data == {}
    print("[OK] test_load_yaml_nonexistent")


def test_load_config_with_custom_path():
    """测试通过 config_path 参数加载配置"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write("log_level: WARNING\n")
        path = f.name
    try:
        cfg = _load_config(path)
        assert cfg["log_level"] == "WARNING"
        # 未指定的字段应有默认值
        assert cfg["model"] == "deepseek-reasoner"
    finally:
        os.unlink(path)
    print("[OK] test_load_config_with_custom_path")


if __name__ == "__main__":
    test_load_yaml()
    test_load_yaml_nonexistent()
    test_load_config_with_custom_path()
    print("\n" + "=" * 40)
    print("所有配置测试通过!")
    print("=" * 40)
