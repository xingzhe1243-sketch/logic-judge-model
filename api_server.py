"""LogicJudgeModel FastAPI Web API Server (async)"""

import asyncio
import os
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

STATIC_DIR = Path(__file__).resolve().parent / "static"

try:
    _INDEX_HTML = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
except (OSError, FileNotFoundError):
    try:
        _INDEX_HTML = (Path("static/index.html")).read_text(encoding="utf-8")
    except (OSError, FileNotFoundError):
        _INDEX_HTML = "<html><body><h1>规则解剖引擎</h1><p>API 运行中</p></body></html>"

from ljmodel import LogicJudgeModel
from ljmodel.model import ALL_MODULES
from ljmodel.database import list_analyses, get_analysis, delete_analysis, search_analyses, clear_history as db_clear
from ljmodel.knowledge_base import KNOWLEDGE_BASE, reload_books

app = FastAPI(
    title="终极逻辑判断模型 API",
    version="2.0.0",
    description="九维思维矩阵 · 逻辑分析 Web API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="待分析文本")
    modules: Optional[list[str]] = Field(None, description="可选，要运行的模块列表")
    html: bool = Field(False, description="是否在响应中包含HTML报告")

class BatchRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, description="待分析文本列表")
    modules: Optional[list[str]] = Field(None, description="可选，要运行的模块列表")

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "2.0.0"

class ModuleInfo(BaseModel):
    name: str
    description: str

# --- Judge singleton ---

_judge: Optional[LogicJudgeModel] = None

def get_judge() -> LogicJudgeModel:
    global _judge
    if _judge is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        _judge = LogicJudgeModel(api_key=api_key)
    return _judge

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve Web UI"""
    return _INDEX_HTML

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()

@app.get("/modules", response_model=list[ModuleInfo])
async def list_modules():
    descriptions = {
        "formal_logic": "形式逻辑分析 — 同一律/矛盾律/排中律/充分理由律 + 论证结构 + 三段论",
        "critical_inquiry": "批判性质询 — 论题识别/结论定位/歧义分析/谬误检测/假设识别/证据评估",
        "bias_detection": "认知偏见检测 — 系统1/系统2激活状态 + 锚定效应/可得性启发/确认偏误等",
        "argumentation": "论证规则评估 — 举例/类比/权威/因果/演绎论证规则检查",
        "elements_of_thought": "思维元素分析 — 目的/问题/信息/概念/假设/视角/推理/启示",
        "structured_analysis": "结构化分析 — MECE/金字塔原理/逻辑树/四象限分析",
        "dialectical": "辩证系统分析 — 辩证张力识别/系统性交互/矛盾分析/历史动态",
        "source_thinking": "源思维深度分析 — 还原事实/辨析因果/锚定切口/层次诊断/深度思考评分",
        "simple_logic": "简单逻辑深度分析 — 逻辑基本定律/思维准备评估/非逻辑根源追溯",
        "llm_primary": "LLM综合分析 — 使用大模型进行九本书框架综合评估",
    }
    return [ModuleInfo(name=n, description=descriptions.get(n, "")) for n in ALL_MODULES]


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """对单条文本进行逻辑分析"""
    judge = get_judge()
    try:
        result = await asyncio.to_thread(judge.analyze, req.text, False, None, req.modules)
        if req.html and result["modules"].get("llm_primary"):
            from ljmodel.report_html import generate_html_report
            result["html_report"] = generate_html_report(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(req: BatchRequest):
    """批量分析多条文本"""
    judge = get_judge()
    results = []
    for i, text in enumerate(req.texts):
        try:
            r = await asyncio.to_thread(judge.analyze, text, False, None, req.modules)
            r["index"] = i
            results.append(r)
        except Exception as e:
            results.append({"index": i, "error": str(e), "input": text})
    return {"results": results}


# --- History Endpoints ---

@app.get("/history")
async def history_list(limit: int = 20, q: str = ""):
    """查询分析历史，支持 ?q=关键词 搜索"""
    if q:
        return search_analyses(q, limit)
    return list_analyses(limit)


@app.get("/history/{hid}")
async def history_detail(hid: int):
    """获取单条分析详情"""
    row = get_analysis(hid)
    if row is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return row


@app.delete("/history/{hid}")
async def history_delete(hid: int):
    """删除单条记录"""
    ok = delete_analysis(hid)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"status": "deleted", "id": hid}


@app.delete("/history")
async def history_clear():
    """清空所有历史"""
    count = db_clear()
    return {"status": "cleared", "deleted": count}


# --- Book Endpoints ---

@app.get("/books")
async def books_list():
    """列出所有可用书籍"""
    return [{"name": k, "source": v.get("source", ""), "description": v.get("description", "")}
            for k, v in KNOWLEDGE_BASE.items()]


@app.get("/books/{book_name}")
async def book_detail(book_name: str):
    """获取某本书的详细内容"""
    book = KNOWLEDGE_BASE.get(book_name)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return book


@app.post("/books/reload")
async def books_reload():
    """从磁盘重新加载所有书籍"""
    loaded = reload_books()
    return {"status": "reloaded", "books": loaded}


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """启动API服务器"""
    import uvicorn
    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print(f"  终极逻辑判断模型 API 启动于 http://{host}:{port}")
    print(f"   API文档: http://localhost:{port}/docs")
    if reload:
        print(f"  自动重载已开启 — 改代码/YAML 文件后自动重启")
    kwargs = dict(host=host, port=port)
    if reload:
        kwargs["reload"] = True
        kwargs["reload_includes"] = ["*.py", "*.yaml"]
        kwargs["app"] = "api_server:app"
    else:
        kwargs["app"] = app
    uvicorn.run(**kwargs)
