"""配置管理 — 支持 .env、YAML 文件、环境变量"""

import os

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: str) -> dict:
    """从 YAML 文件加载配置"""
    if yaml is None:
        return {}
    real = os.path.realpath(path)
    if os.path.exists(real):
        with open(real, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            # 展平 server 子字段
            if "server" in data and isinstance(data["server"], dict):
                for k, v in data["server"].items():
                    if k not in data:
                        data[k] = v
                del data["server"]
            return data
    return {}


def _load_config(config_path: str = None) -> dict:
    """加载配置，优先级: config_path 参数 > YAML 搜索路径 > .env > 环境变量 > 默认值

    Args:
        config_path: 可选，指定的配置文件路径
    """
    # 硬编码默认值
    config = {
        "api_key": "",
        "model": "deepseek-reasoner",
        "base_url": "https://api.deepseek.com/v1",
        "doubao_api_key": "",
        "doubao_base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "doubao_model": "doubao-pro-32k",
        "log_level": "WARNING",
        "modules": None,
    }

    # 1. YAML 配置（优先级：显式路径 > ./config.yaml > ~/.logic_judge.yaml）
    yaml_paths = []
    if config_path:
        yaml_paths.append(config_path)
    yaml_paths += [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml"),
        os.path.join(os.path.expanduser("~"), ".logic_judge.yaml"),
    ]
    for yp in yaml_paths:
        data = _load_yaml(yp)
        if data:
            config.update({k: v for k, v in data.items() if v is not None})
            break

    # 2. .env 文件
    env_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        os.path.join(os.path.expanduser("~"), ".logic_judge.env"),
    ]
    for env_path in env_paths:
        real = os.path.realpath(env_path)
        if os.path.exists(real):
            with open(real, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip().upper()
                    val = val.strip().strip("\"'")
                    if key == "DEEPSEEK_API_KEY" and not config["api_key"]:
                        config["api_key"] = val
                    elif key == "DEEPSEEK_MODEL":
                        config["model"] = val
                    elif key == "DEEPSEEK_BASE_URL":
                        config["base_url"] = val
                    elif key == "DOUBAO_API_KEY":
                        config["doubao_api_key"] = val
                    elif key == "DOUBAO_BASE_URL":
                        config["doubao_base_url"] = val
                    elif key == "DOUBAO_MODEL":
                        config["doubao_model"] = val
                    elif key == "LOG_LEVEL":
                        config["log_level"] = val
            break

    # 3. 环境变量（最高优先级，覆盖 YAML 和 .env）
    env_map = {
        "DEEPSEEK_API_KEY": "api_key",
        "DEEPSEEK_MODEL": "model",
        "DEEPSEEK_BASE_URL": "base_url",
        "DOUBAO_API_KEY": "doubao_api_key",
        "DOUBAO_BASE_URL": "doubao_base_url",
        "DOUBAO_MODEL": "doubao_model",
        "LOG_LEVEL": "log_level",
    }
    for env_key, cfg_key in env_map.items():
        val = os.environ.get(env_key)
        if val:
            config[cfg_key] = val

    return config


CONFIG = _load_config()
