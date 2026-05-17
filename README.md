# 终极逻辑判断模型 · 九维思维矩阵

<h1 align="center">🔬 终极逻辑判断模型 · 九维思维矩阵</h1>
<p align="center"><strong>Logic Judge Model · 9-Dimensional Thinking Matrix</strong></p>
<p align="center">三合一智能分析系统：逻辑评分 + 规则解剖 + 多模型深度辩论</p>

---

## 📖 目录 / Table of Contents

- [概述 / Overview](#概述--overview)
- [三大核心系统 / Three Core Systems](#三大核心系统--three-core-systems)
- [项目结构 / Project Structure](#项目结构--project-structure)
- [快速开始 / Quick Start](#快速开始--quick-start)
- [CLI 使用指南 / CLI Usage](#cli-使用指南--cli-usage)
- [Web API 部署 / Web API Deployment](#web-api-部署--web-api-deployment)
- [知识库 / Knowledge Base](#知识库--knowledge-base)
- [配置说明 / Configuration](#配置说明--configuration)
- [架构设计 / Architecture](#架构设计--architecture)
- [依赖 / Dependencies](#依赖--dependencies)

---

## 概述 / Overview

**终极逻辑判断模型**是一套三合一智能分析系统，整合了40本经典著作的思维框架，覆盖逻辑学、心理学、经济学、社会学、博弈论、战略学六大领域。

| 特性 | 说明 |
|------|------|
| 🧠 **三大系统** | 逻辑评分 + 规则解剖 + 多模型辩论 |
| 📚 **知识库** | 40本书，685+ 结构化概念 |
| 🌐 **Web API** | FastAPI + 内联 HTML UI，开箱即用 |
| 💾 **持久化** | SQLite 历史记录，完整可追溯 |
| 🔌 **多 LLM** | DeepSeek + 豆包 双模型审查 |
| 🐳 **可部署** | Railway / Docker / 任意云平台 |

**The Logic Judge Model** is a three-in-one intelligent analysis system integrating the thinking frameworks of 40 classic works across six domains: logic, psychology, economics, sociology, game theory, and strategy.

---

## 三大核心系统 / Three Core Systems

### 系统一：逻辑评分管道 / Logic Scoring Pipeline

对任意文本进行10维度逻辑质量评估，输出 0-100 量化评分。

```
输入文本
  │
  ├─ 1. formal_logic        形式逻辑分析（三段论/谬误检测）
  ├─ 2. critical_inquiry    批判性质询（论题/歧义/假设/证据）
  ├─ 3. bias_detection      认知偏见检测（系统1/2，20+种偏见）
  ├─ 4. argumentation       论证规则评估（24条论证规则）
  ├─ 5. elements_of_thought 思维元素分析（8元素+9标准）
  ├─ 6. structured_analysis 结构化分析（MECE/金字塔/逻辑树）
  ├─ 7. dialectical         辩证系统分析（矛盾/张力/历史动态）
  ├─ 8. source_thinking     源思维深度分析（还原→因果→锚定）
  ├─ 9. simple_logic        简单逻辑（基本定律/思维准备）
  ├─ 10. zhihu_expert       知乎集体智慧（真实世界经验）
  │
  ├─ LLM 综合分析（DeepSeek 深度评审）
  ├─ 逻辑问题猎手1（DeepSeek 深度扫描）
  ├─ 逻辑问题猎手2（豆包大模型交叉验证）
  │
  └─ 综合合成 → 评分 + 发现 + 警告 + 行动建议
```

**10个分析模块并行执行**，每个模块基于特定书籍的知识框架独立分析，最终由合成器汇总生成结构化报告。

### 系统二：规则解剖模型 V4.0 / Dissection Engine V4.0

独立于评分管道的决策推理系统，**不评分，只解剖**。

#### 模式A：解剖引擎（博弈分析）
- **14条公理 × 3层**：L1（不可违背）> L2（强约束）> L3（情境约束）
- **22条实战规则**：利益格局、权力动态、信息不对称、沉没成本等
- **四步分析流程**：博弈地图 → 风险计算 → 公理冲突检查 → 行动指令
- **自动模式检测**：根据问题特征自动判断应该用模式A还是模式B

#### 模式B：共鸣拓扑（方向导航）
- **6条核心公理**：世界是流动的场 / 博弈是场的局部冻结 / 痛苦是导航信号
- **3套操作协议**：痛苦分类 / 场域感知 / 深度打开
- **适用场景**：方向迷茫、过度分析死循环、价值冲突

### 系统三：多模型智囊团深度辩论 / Multi-Expert Deep Debate

5位专家 × 三阶段辩论流程，基于全部知识库进行深度对抗分析。

| 专家 | 领域 | 代表书籍 |
|------|------|----------|
| 🛡️ **逻辑卫士** | 形式逻辑、论证规则 | 逻辑学十五讲、论证是一门学问 |
| 🔍 **认知侦探** | 认知偏见、批判思维 | 思考快与慢、学会提问 |
| 📊 **系统分析师** | 结构化分析、辩证系统 | 麦肯锡、世界的逻辑 |
| 🌊 **源思维师** | 还原→因果→锚定 | 源思维 |
| ♟️ **博弈策略家** | 利益格局、权力动态 | 规则解剖模型 |

**三阶段辩论流程**：
1. **独立分析** — 5位专家各自基于领域知识独立分析
2. **交叉辩论** — 专家互相质疑、补充、反驳
3. **综合裁决** — 主持人综合所有观点，给出最终判断

---

## 项目结构 / Project Structure

```
LogicJudgeModel/
├── run.py                          # CLI 入口（评分 + 解剖 + 辩论）
├── 思维解剖.py                      # 独立思维解剖入口
├── 思维解剖.bat                     # Windows 批处理启动
├── api_server.py                   # FastAPI Web 服务器（含内联 HTML）
├── config.py                       # 配置管理（环境变量 + YAML）
├── logger.py                       # 日志系统
├── requirements.txt                # Python 依赖
│
├── ljmodel/                        # 核心引擎包
│   ├── model.py                    # LogicJudgeModel 主类
│   ├── config.py                   # 配置加载
│   ├── knowledge_base.py           # 40本书知识库管理
│   ├── synthesis.py                # 综合合成器
│   ├── coordinator.py              # 分析协调器
│   ├── report.py                   # 终端报告渲染
│   ├── report_html.py              # HTML 报告生成
│   ├── database.py                 # SQLite 持久化层
│   ├── logger.py                   # 日志工具
│   │
│   ├── dissection_engine.py        # 解剖引擎（模式A）
│   ├── resonance_engine.py         # 共鸣拓扑引擎（模式B）
│   ├── debate_engine.py            # 多模型辩论引擎
│   │
│   └── analyzers/                  # 10个分析模块
│       ├── __init__.py
│       └── zhihu_expert.py         # 知乎集体智慧分析器
│
├── books/                          # 40本书 YAML 知识库
│   ├── logic_lectures.yaml         # 逻辑学十五讲
│   ├── thinking_fast_slow.yaml     # 思考，快与慢
│   ├── capital.yaml                # 资本论
│   ├── black_swan.yaml             # 黑天鹅
│   ├── sapiens.yaml                # 人类简史
│   └── ... (35 more)
│
├── zhihu_scraper/                  # 知乎爬虫工具包
│   ├── api.py                      # API 接口
│   ├── auth.py                     # 认证模块
│   ├── cli.py                      # 命令行工具
│   ├── config.py                   # 爬虫配置
│   ├── extractor.py                # 内容提取
│   ├── search.py                   # 搜索模块
│   └── storage.py                  # 数据存储
│
├── data/                           # 运行时数据
├── docs/                           # 文档
└── tests/                          # 测试
```

---

## 快速开始 / Quick Start

### 环境要求 / Prerequisites
- Python 3.10+
- DeepSeek API Key（可选，但强烈推荐）

### 安装 / Installation

```bash
# 1. 克隆仓库
git clone https://github.com/xingzhe1243-sketch/logic-judge-model.git
cd logic-judge-model

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置 API Key
# Windows PowerShell:
$env:DEEPSEEK_API_KEY = "your-api-key"

# Linux / macOS:
export DEEPSEEK_API_KEY="your-api-key"

# 或写入 .env 文件（项目根目录）
echo DEEPSEEK_API_KEY=your-api-key > .env

# 4. 运行
python run.py                     # 交互模式
python run.py "你的文本"           # 单次分析
python 思维解剖.py                 # 思维解剖交互模式
```

### 获取 API Key

| 提供商 | 注册地址 | 用途 |
|--------|----------|------|
| DeepSeek | https://platform.deepseek.com | 主分析引擎（必选） |
| 豆包/火山引擎 | https://console.volcengine.com | 第二视角审查（可选） |

---

## CLI 使用指南 / CLI Usage

### 逻辑评分模式

```bash
# 交互式分析
python run.py

# 单次分析
python run.py "所有天鹅都是白的，因为我没见过黑的"

# JSON 输出
python run.py "你的文本" --json

# 生成 HTML 报告
python run.py "你的文本" --html

# 指定模块
python run.py "你的文本" --modules formal_logic,bias_detection

# 批量分析（从文件）
python run.py --input texts.json --output results.json --json

# 查看历史
python run.py --history           # 最近10条
python run.py --history 3         # 查看 #3 详情
python run.py --history --clear   # 清空历史

# 查看知识库
python run.py --books             # 列出所有书籍
python run.py --books logic_lectures  # 查看指定书籍
```

### 规则解剖模式

```bash
# 自动模式检测
python run.py --dissect "我应该辞职创业还是继续打工？"

# 手动指定模式
python run.py --dissect --mode a "这个商业合作是否公平？"   # 博弈分析
python run.py --dissect --mode b "我的人生方向在哪里？"     # 方向导航

# 解剖 + 深度辩论（全流程）
python run.py --dissect --deep "某个复杂决策问题"

# 纯辩论模式
python run.py --debate "某个需要多角度分析的问题"
```

### 思维解剖独立入口

```bash
python 思维解剖.py                              # 交互模式
python 思维解剖.py "问题" --mode a               # 博弈分析
python 思维解剖.py "问题" --deep                 # 全流程
python 思维解剖.py "问题" --debate --json        # 辩论 + JSON输出
```

### 交互模式命令

```
analyze <文本>    — 全面逻辑分析
dissect <问题>    — 解剖分析
game <问题>       — 模式A：博弈分析
nav <问题>        — 模式B：方向导航
debate <问题>     — 多模型深度辩论
deep <问题>       — 解剖 + 辩论全流程
models            — 查看知识库
books             — 列出所有书籍
history           — 查看历史记录
help              — 帮助
exit              — 退出
```

---

## Web API 部署 / Web API Deployment

### 本地启动

```bash
# 启动 Web 服务（含可视化界面）
python run.py --serve --port 8000

# 开启热重载（代码或 YAML 变更自动重启）
python run.py --serve --port 8000 --reload
```

打开浏览器访问：
- **Web UI**: http://localhost:8000
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/` | Web UI（内联 HTML） |
| `GET` | `/health` | 健康检查 |
| `GET` | `/modules` | 列出所有分析模块 |
| `POST` | `/analyze` | 单文本分析 |
| `POST` | `/analyze/batch` | 批量分析 |
| `GET` | `/history` | 历史记录列表 |
| `GET` | `/history/{id}` | 历史记录详情 |
| `DELETE` | `/history/{id}` | 删除单条记录 |
| `DELETE` | `/history` | 清空全部历史 |
| `GET` | `/books` | 列出所有书籍 |
| `GET` | `/books/{name}` | 书籍详情 |
| `POST` | `/books/reload` | 从磁盘重载书籍 |

### 请求示例

```bash
# 分析文本
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "所有成功人士都早起，所以早起就能成功"}'

# 批量分析
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["文本1", "文本2", "文本3"]}'

# 搜索历史
curl "http://localhost:8000/history?q=成功&limit=10"
```

### 部署到 Railway / 云平台

本项目已支持一键部署 Railway。关键文件：

```bash
# Procfile（Railway 自动检测）
web: python run.py --serve --port $PORT

# 或直接指定
uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

**部署步骤**：
1. Fork 本仓库
2. 在 Railway 中连接 GitHub 仓库
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. （可选）设置 `DOUBAO_API_KEY` 启用双模型审查
5. 部署

**Railway 环境变量**：
```
DEEPSEEK_API_KEY=sk-xxx
DOUBAO_API_KEY=xxx        # 可选
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-pro-32k
```

### Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["sh", "-c", "python run.py --serve --port ${PORT:-8000}"]
```

```bash
docker build -t logic-judge-model .
docker run -p 8000:8000 -e DEEPSEEK_API_KEY=sk-xxx logic-judge-model
```

---

## 知识库 / Knowledge Base

40本书籍，685+ 结构化概念，覆盖六大领域：

| 领域 | 书目 |
|------|------|
| **逻辑学** | 逻辑学十五讲、简单的逻辑学、论证是一门学问、世界的逻辑、批判性思维工具、学会提问、源思维、清晰思考的艺术 |
| **心理学** | 思考快与慢、影响力、亲密关系、乌合之众、犯罪心理学、操纵心理学、终身成长、我的作弊人生 |
| **经济学** | 资本论、国富论、21世纪资本论、金钱心理学 |
| **社会学** | 人类简史、丑陋的中国人、乡土中国、邓小平时代、中县干部 |
| **博弈论** | 黑天鹅、非对称风险、权力的48条法则、自私的基因、进化心理学 |
| **战略学** | 孙子兵法·三十六计·论持久战、麦肯锡教我的逻辑思维、刻意练习 |

知识库以 YAML 格式存储在 `books/` 目录中，支持热重载（Web API 调用 `POST /books/reload` 即可生效，无需重启服务）。

---

## 配置说明 / Configuration

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `DOUBAO_API_KEY` | 豆包/火山引擎 API 密钥 | - |
| `DOUBAO_BASE_URL` | 豆包 API 地址 | `https://ark.cn-beijing.volces.com/api/v3` |
| `DOUBAO_MODEL` | 豆包模型名称 | `doubao-pro-32k` |

### config.yaml（可选）

```yaml
# LLM 配置
api_key: ""           # 留空则从环境变量读取
model: "deepseek-chat"
llm_provider: "deepseek"
base_url: "https://api.deepseek.com/v1"

# 日志级别
log_level: "WARNING"

# 缓存
cache_size: 64
```

### API Key 未设置时的行为

系统在未检测到 API Key 时仍可运行，但仅使用本地规则引擎进行分析（无 LLM 增强）。**强烈建议配置 DeepSeek API Key 以获得完整功能**。

---

## 架构设计 / Architecture

### 设计原则

1. **解剖模型独立**：规则解剖模型（dissect/debate）完全独立于逻辑评分管道，不侵入 analyze()，不共享评分标准
2. **并行执行**：10个分析模块在线程池中并行计算
3. **双模型交叉验证**：DeepSeek（主分析）+ 豆包（第二视角），降低单模型偏见
4. **知识库驱动**：所有分析逻辑根植于经典著作，而非黑盒规则

### 数据流

```
用户输入
  │
  ├── analyze() ──→ 10模块并行 ──→ LLM主分析 ──→ 逻辑猎手1+2 ──→ 合成器 ──→ 报告
  │
  ├── dissect() ──→ 模式检测(A/B) ──→ 解剖引擎/共鸣引擎 ──→ 报告
  │
  └── debate()  ──→ 解剖分析(可选) ──→ 5专家×3阶段 ──→ 综合裁决 ──→ 报告
```

---

## 依赖 / Dependencies

```
openai >= 1.0.0         # LLM 客户端（DeepSeek / OpenAI 兼容）
requests >= 2.31.0      # HTTP 请求
fastapi >= 0.100.0      # Web API 框架
uvicorn >= 0.20.0       # ASGI 服务器
pyyaml >= 6.0           # YAML 知识库解析
httpx >= 0.24.0         # 异步 HTTP
```

### 可选依赖

- `aiofiles` — 异步文件操作（大规模批量处理时推荐）
- `python-dotenv` — .env 文件自动加载
- `beautifulsoup4` / `lxml` — 知乎爬虫数据清洗

---

## 扩展指南 / Extension Guide

### 添加新书籍

在 `books/` 目录创建 YAML 文件，系统自动热加载：

```yaml
# books/my_new_book.yaml
source: "书名 / Book Title"
description: "一句话描述 / One-line description"
core_concepts:
  - name: "概念1"
    definition: "定义..."
  - name: "概念2"
    definition: "定义..."
```

Web API 调用 `POST /books/reload` 即可生效，无需重启。

### 添加新分析模块

在 `ljmodel/analyzers/` 创建 Python 文件，实现分析函数：

```python
# ljmodel/analyzers/my_analyzer.py
def analyze_my_module(text: str, kb: dict) -> dict:
    """对新文本执行自定义分析"""
    return {
        "关键发现": [...],
        "评分": 85,
    }
```

然后在 `ljmodel/analyzers/__init__.py` 注册，在 `ljmodel/model.py` 的 `ALL_MODULES` 中添加条目。

### 添加新 LLM Provider

```python
# ljmodel/providers/my_provider.py
# 1. 继承 OpenAIClient 兼容接口
# 2. 在 config.py 添加环境变量
# 3. 在 model.py 的 PROVIDERS 字典注册
```

---

## 许可证 / License

本项目仅用于学习和研究目的。

---

<p align="center">
  <strong>Logic Judge Model · 9-Dimensional Thinking Matrix</strong><br>
  Built with 40 classic books · 685+ structured concepts · 10 parallel analyzers<br>
  Dual LLM review · 5-expert debate · Pure reasoning, no black boxes
</p>
