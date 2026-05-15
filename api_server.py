"""LogicJudgeModel FastAPI Web API Server (async)"""

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


_INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>逻辑判断模型</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, 'Segoe UI', 'Noto Sans SC', sans-serif; background:#0f1419; color:#e1e8ed; line-height:1.6; }
  .container { max-width:800px; margin:0 auto; padding:20px; }
  h1 { font-size:1.4em; margin-bottom:4px; background:linear-gradient(135deg,#3498db,#9b59b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .sub { color:#657786; font-size:0.85em; margin-bottom:24px; }
  textarea { width:100%; padding:12px; border:1px solid #2f3d4a; border-radius:8px; background:#1a232e; color:#e1e8ed; font-size:0.95em; resize:vertical; min-height:100px; font-family:inherit; outline:none; transition:border 0.15s; }
  textarea:focus { border-color:#3498db; }
  .modules { display:flex; flex-wrap:wrap; gap:6px; margin:12px 0; }
  .modules label { padding:4px 10px; border:1px solid #2f3d4a; border-radius:14px; font-size:0.82em; cursor:pointer; transition:all 0.15s; user-select:none; }
  .modules label:hover { border-color:#657786; }
  .modules input { display:none; }
  .modules input:checked + span { color:#3498db; }
  .modules label:has(input:checked) { border-color:#3498db; background:rgba(52,152,219,0.1); }
  .mod-toggle { color:#657786; font-size:0.8em; cursor:pointer; margin-left:8px; }
  button { padding:10px 28px; border:none; border-radius:8px; background:linear-gradient(135deg,#3498db,#9b59b6); color:#fff; font-size:0.95em; cursor:pointer; transition:opacity 0.15s; }
  button:hover { opacity:0.85; }
  button:disabled { opacity:0.4; cursor:not-allowed; }
  .btn-secondary { background:#2f3d4a; }
  .btn-secondary:hover { background:#3d4d5c; }
  .btn-sm { padding:4px 12px; font-size:0.8em; border-radius:4px; }
  .btn-danger { background:#e74c3c; }
  .btn-danger:hover { background:#c0392b; }
  .status { margin:12px 0; color:#657786; font-size:0.85em; }
  .score { text-align:center; padding:24px; margin:16px 0; background:#1a232e; border-radius:12px; }
  .score-badge { display:inline-flex; width:80px; height:80px; border-radius:50%; align-items:center; justify-content:center; font-size:1.6em; font-weight:700; color:#fff; }
  .score-badge.high { background:#27ae60; }
  .score-badge.mid { background:#f39c12; }
  .score-badge.low { background:#e74c3c; }
  .score-label { margin-top:8px; color:#657786; font-size:0.85em; }
  .section { margin:12px 0; }
  .section-title { font-size:0.9em; font-weight:600; margin-bottom:6px; color:#8899a6; }
  .items { display:flex; flex-direction:column; gap:4px; }
  .item { padding:8px 12px; border-radius:6px; font-size:0.88em; }
  .item.warning { background:rgba(231,76,60,0.1); border-left:3px solid #e74c3c; }
  .item.finding { background:rgba(39,174,96,0.1); border-left:3px solid #27ae60; }
  .item.suggestion { background:rgba(52,152,219,0.1); border-left:3px solid #3498db; }
  .card { background:#1a232e; border-radius:8px; margin:8px 0; overflow:hidden; }
  .card-header { padding:10px 14px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; font-size:0.88em; user-select:none; }
  .card-header:hover { background:#1f2a36; }
  .card-header .arrow { color:#657786; transition:transform 0.2s; }
  .card.open .arrow { transform:rotate(180deg); }
  .card-body { padding:0 14px 14px; display:none; }
  .card.open .card-body { display:block; }
  .card-body .line { padding:3px 0; font-size:0.83em; color:#a0aec0; }
  .card-body .line.warn { color:#e74c3c; }
  .card-body .line.ok { color:#27ae60; }
  .error { background:rgba(231,76,60,0.15); border:1px solid #e74c3c; border-radius:8px; padding:12px; margin:12px 0; font-size:0.88em; text-align:center; }
  .footer { text-align:center; padding:24px 0; color:#2f3d4a; font-size:0.78em; }
  .history-panel { display:none; margin:12px 0; max-height:400px; overflow-y:auto; }
  .history-panel.open { display:block; }
  .history-item { display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:6px; cursor:pointer; transition:background 0.1s; }
  .history-item:hover { background:#1f2a36; }
  .history-item .h-score { min-width:48px; text-align:center; font-weight:700; font-size:0.85em; }
  .history-item .h-text { flex:1; font-size:0.83em; color:#a0aec0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .history-item .h-time { font-size:0.75em; color:#657786; min-width:120px; text-align:right; }
  @media (max-width:600px) { .container { padding:12px; } }
</style>
</head>
<body>
<div class="container">
  <h1>终极逻辑判断模型</h1>
  <div class="sub">九维思维矩阵 · 逻辑分析</div>
  <textarea id="input" placeholder="输入要分析的文本..."></textarea>
  <div style="display:flex;align-items:center;margin-top:8px;">
    <span style="font-size:0.82em;color:#657786;">分析模块</span>
    <span class="mod-toggle" id="toggleAll">全选/取消</span>
  </div>
  <div class="modules" id="modules"></div>
  <button id="analyzeBtn">分析</button>
  <button id="historyBtn" class="btn-secondary" style="margin-left:8px;">历史</button>
  <div class="status" id="status"></div>
  <div class="history-panel" id="historyPanel">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <span style="font-size:0.85em;color:#8899a6;">最近分析记录</span>
      <span id="historyCount" style="font-size:0.78em;color:#657786;"></span>
    </div>
    <div id="historyList"></div>
    <div id="historyEmpty" style="text-align:center;padding:20px;color:#657786;font-size:0.85em;display:none;">暂无分析记录</div>
  </div>
  <div id="results"></div>
  <div class="footer">终极逻辑判断模型 · 九维思维矩阵 v2.0</div>
</div>
<script>
const modules = ["formal_logic","critical_inquiry","bias_detection","argumentation","elements_of_thought","structured_analysis","dialectical","source_thinking","simple_logic","llm_primary"];
const modLabels = {formal_logic:"形式逻辑",critical_inquiry:"批判性质询",bias_detection:"认知偏见",argumentation:"论证规则",elements_of_thought:"思维元素",structured_analysis:"结构化分析",dialectical:"辩证系统",source_thinking:"源思维",simple_logic:"简单逻辑",llm_primary:"LLM分析"};
let allSelected = true;
const mc = document.getElementById('modules');
modules.forEach(m => { const l = document.createElement('label'); l.innerHTML = '<input type="checkbox" checked data-mod="'+m+'"><span>'+modLabels[m]+'</span>'; l.querySelector('input').addEventListener('change',()=>{allSelected=false}); mc.appendChild(l); });
document.getElementById('toggleAll').addEventListener('click',()=>{allSelected=!allSelected; document.querySelectorAll('#modules input').forEach(cb=>cb.checked=allSelected)});
document.getElementById('analyzeBtn').addEventListener('click',async()=>{
  const text = document.getElementById('input').value.trim(); if(!text) return;
  const sel = [...document.querySelectorAll('#modules input:checked')].map(cb=>cb.dataset.mod);
  const btn = document.getElementById('analyzeBtn'); const status = document.getElementById('status'); const results = document.getElementById('results');
  btn.disabled=true; status.textContent='分析中...'; results.innerHTML='';
  try {
    const res = await fetch('/analyze', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,modules:sel.length===modules.length?null:sel})});
    if(!res.ok) throw new Error('HTTP '+res.status);
    renderResults(await res.json(), results); status.textContent='分析完成';
  } catch(e) { results.innerHTML='<div class="error">请求失败: '+e.message+'</div>'; status.textContent='分析失败'; }
  btn.disabled=false;
});
function renderResults(data,el){
  const syn = data.synthesis||{}; const s = (syn['逻辑质量评分']||'').match(/(\d+)\/100/); const sc = s?parseInt(s[1]):0; const cls = sc>=70?'high':sc>=40?'mid':'low';
  let html = '<div class="score"><div class="score-badge '+cls+'">'+sc+'</div><div class="score-label">'+esc(syn['逻辑质量评分']||'')+'</div></div>';
  const warns = syn['警告']||[]; if(warns.length && !(warns.length==1 && warns[0].includes('未检测到'))){ html+='<div class="section"><div class="section-title">警告</div><div class="items">'; warns.forEach(w=>html+='<div class="item warning">'+esc(w)+'</div>'); html+='</div></div>'; }
  const findings = syn['主要发现']||[]; if(findings.length){ html+='<div class="section"><div class="section-title">主要发现</div><div class="items">'; findings.forEach(f=>html+='<div class="item finding">'+esc(f)+'</div>'); html+='</div></div>'; }
  const sug = syn['行动建议']||[]; if(sug.length){ html+='<div class="section"><div class="section-title">行动建议</div><div class="items">'; sug.forEach(s=>html+='<div class="item suggestion">'+esc(s)+'</div>'); html+='</div></div>'; }
  const md = data.modules||{}; ['formal_logic','critical_inquiry','bias_detection','argumentation','elements_of_thought','structured_analysis','dialectical','source_thinking','simple_logic','llm_primary'].forEach(k=>{
    const m = md[k]; if(!m||!Object.keys(m).length) return;
    const lines=[]; Object.values(m).forEach(v=>{if(Array.isArray(v)) v.forEach(x=>lines.push(typeof x==='string'?x:JSON.stringify(x))); else if(typeof v==='object') Object.entries(v).forEach(([k,v])=>lines.push(k+': '+v)); });
    if(!lines.length) return;
    html+='<div class="card open"><div class="card-header"><span>'+esc(modLabels[k]||k)+'</span><span class="arrow">▼</span></div><div class="card-body">';
    lines.forEach(l=>html+='<div class="line'+(l.includes('谬误')?' warn':'')+'">'+esc(l)+'</div>');
    html+='</div></div>';
  });
  // 逻辑问题猎手 — 独立LLM审查（特殊渲染）
  function renderHunter(moduleKey, label, fallback){
    let h = md[moduleKey];
    if(!h && fallback) h = md[fallback];
    if(!h || !h['问题列表'] || !h['问题列表'].length) return;
    html+='<div class="card open"><div class="card-header"><span>'+label+'</span><span class="arrow">▼</span></div><div class="card-body">';
    h['问题列表'].forEach(function(item){
      const sev = item['严重程度']||'中';
      const cls = sev==='高'?'warn':sev==='中'?'':'ok';
      const ptype = item['问题类型']||'';
      html+='<div class="line '+cls+'">'+esc(item['修正建议']||'')+'</div>';
      html+='<div style="padding:0 0 2px 12px;font-size:0.78em;color:#657786;">↳ '+esc(ptype)+' ('+esc(sev)+') — '+esc((item['问题说明']||'').slice(0,150))+'</div>';
    });
    html+='</div></div>';
  }
  renderHunter('logic_problem_hunter_1', '逻辑问题猎手1 — DeepSeek 深度审查', 'logic_problem_hunter');
  renderHunter('logic_problem_hunter_2', '逻辑问题猎手2 — 豆包大模型 深度审查');
  el.innerHTML = html;
  el.querySelectorAll('.card-header').forEach(h => h.addEventListener('click',()=>h.parentElement.classList.toggle('open')));
}
function esc(s){ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
document.getElementById('historyBtn').addEventListener('click',()=>{document.getElementById('historyPanel').classList.toggle('open'); if(document.getElementById('historyPanel').classList.contains('open')) fetchHistory();});
async function fetchHistory(){
  const list = document.getElementById('historyList'); const empty = document.getElementById('historyEmpty'); const count = document.getElementById('historyCount');
  list.innerHTML='<div style="text-align:center;padding:12px;color:#657786;">加载中...</div>'; empty.style.display='none';
  try {
    const res = await fetch('/history?limit=20'); if(!res.ok) throw new Error('HTTP '+res.status);
    const rows = await res.json(); if(!rows.length){ list.innerHTML=''; empty.style.display='block'; count.textContent=''; return; }
    count.textContent='共 '+rows.length+' 条';
    list.innerHTML = rows.map(r=>'<div class="history-item" data-id="'+r.id+'"><span class="h-score" style="color:'+(r.score>=70?'#27ae60':r.score>=40?'#f39c12':'#e74c3c')+'">'+r.score+'</span><span class="h-text">'+esc(r.text)+'</span><span class="h-time">'+esc(r.created_at||'')+'</span><button class="btn-sm btn-secondary view-btn" data-id="'+r.id+'">查看</button><button class="btn-sm btn-danger del-btn" data-id="'+r.id+'">删除</button></div>').join('');
    list.querySelectorAll('.view-btn').forEach(btn=>btn.addEventListener('click',async e=>{e.stopPropagation(); const id=e.target.dataset.id; document.getElementById('historyPanel').classList.remove('open'); const res=await fetch('/history/'+id); const data=await res.json(); renderResults(data.result||data,document.getElementById('results'));}));
    list.querySelectorAll('.del-btn').forEach(btn=>btn.addEventListener('click',async e=>{e.stopPropagation(); if(!confirm('确定删除？')) return; await fetch('/history/'+e.target.dataset.id,{method:'DELETE'}); fetchHistory();}));
  } catch(e){ list.innerHTML='<div style="text-align:center;padding:12px;color:#e74c3c;">加载失败: '+e.message+'</div>'; }
}
</script>
</body>
</html>"""

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
