"""LogicJudgeModel FastAPI Web API Server — 三系统完整版 (评分+解剖+辩论)"""

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>终极逻辑判断模型 · 九维思维矩阵</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Segoe UI','Noto Sans SC',sans-serif;background:#0f1419;color:#e1e8ed;line-height:1.6}
.container{max-width:860px;margin:0 auto;padding:20px}
h1{font-size:1.3em;margin-bottom:2px;background:linear-gradient(135deg,#3498db,#9b59b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:#657786;font-size:0.82em;margin-bottom:16px}
.tabs{display:flex;gap:0;margin-bottom:16px;border-bottom:2px solid #2f3d4a}
.tab-btn{padding:10px 20px;border:none;background:transparent;color:#657786;font-size:0.9em;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all 0.15s}
.tab-btn:hover{color:#e1e8ed}
.tab-btn.active{color:#3498db;border-bottom-color:#3498db}
.tab-content{display:none}
.tab-content.active{display:block}
textarea{width:100%;padding:12px;border:1px solid #2f3d4a;border-radius:8px;background:#1a232e;color:#e1e8ed;font-size:0.95em;resize:vertical;min-height:120px;font-family:inherit;outline:none;transition:border 0.15s}
textarea:focus{border-color:#3498db}
.mode-select{display:flex;gap:12px;margin:10px 0;flex-wrap:wrap}
.mode-select label{padding:6px 16px;border:1px solid #2f3d4a;border-radius:18px;font-size:0.84em;cursor:pointer;transition:all 0.15s;user-select:none}
.mode-select label:hover{border-color:#657786}
.mode-select input{display:none}
.mode-select input:checked+span{color:#3498db}
.mode-select label:has(input:checked){border-color:#3498db;background:rgba(52,152,219,0.1)}
.modules{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.modules label{padding:4px 10px;border:1px solid #2f3d4a;border-radius:14px;font-size:0.8em;cursor:pointer;transition:all 0.15s;user-select:none}
.modules label:hover{border-color:#657786}
.modules input{display:none}
.modules input:checked+span{color:#3498db}
.modules label:has(input:checked){border-color:#3498db;background:rgba(52,152,219,0.1)}
.mod-toggle{color:#657786;font-size:0.78em;cursor:pointer;margin-left:8px}
.btn-row{display:flex;gap:10px;margin:12px 0;flex-wrap:wrap}
.btn-primary{padding:10px 28px;border:none;border-radius:8px;background:linear-gradient(135deg,#3498db,#9b59b6);color:#fff;font-size:0.95em;cursor:pointer;transition:opacity 0.15s}
.btn-primary:hover{opacity:0.85}
.btn-primary:disabled{opacity:0.4;cursor:not-allowed}
.btn-secondary{padding:10px 20px;border:none;border-radius:8px;background:#2f3d4a;color:#e1e8ed;font-size:0.9em;cursor:pointer;transition:background 0.15s}
.btn-secondary:hover{background:#3d4d5c}
.btn-sm{padding:4px 12px;font-size:0.78em;border-radius:4px;border:none;cursor:pointer}
.btn-danger{background:#e74c3c;color:#fff}
.btn-danger:hover{background:#c0392b}
.status{margin:10px 0;color:#657786;font-size:0.83em;min-height:20px}
.score{text-align:center;padding:24px;margin:16px 0;background:#1a232e;border-radius:12px}
.score-badge{display:inline-flex;width:80px;height:80px;border-radius:50%;align-items:center;justify-content:center;font-size:1.6em;font-weight:700;color:#fff}
.score-badge.high{background:#27ae60}.score-badge.mid{background:#f39c12}.score-badge.low{background:#e74c3c}
.score-label{margin-top:8px;color:#657786;font-size:0.83em}
.section{margin:12px 0}
.section-title{font-size:0.88em;font-weight:600;margin-bottom:6px;color:#8899a6}
.items{display:flex;flex-direction:column;gap:4px}
.item{padding:8px 12px;border-radius:6px;font-size:0.85em}
.item.warning{background:rgba(231,76,60,0.1);border-left:3px solid #e74c3c}
.item.finding{background:rgba(39,174,96,0.1);border-left:3px solid #27ae60}
.item.suggestion{background:rgba(52,152,219,0.1);border-left:3px solid #3498db}
.item.neutral{background:#1a232e;border-left:3px solid #657786}
.card{background:#1a232e;border-radius:8px;margin:8px 0;overflow:hidden}
.card-header{padding:10px 14px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-size:0.86em;user-select:none}
.card-header:hover{background:#1f2a36}
.card-header .arrow{color:#657786;transition:transform 0.2s}
.card.open .arrow{transform:rotate(180deg)}
.card-body{padding:0 14px 14px;display:none}
.card.open .card-body{display:block}
.card-body .line{padding:3px 0;font-size:0.81em;color:#a0aec0}
.card-body .line.warn{color:#e74c3c}
.card-body .line.ok{color:#27ae60}
.error{background:rgba(231,76,60,0.15);border:1px solid #e74c3c;border-radius:8px;padding:12px;margin:12px 0;font-size:0.86em;text-align:center}
.footer{text-align:center;padding:24px 0;color:#2f3d4a;font-size:0.76em}
.history-panel{display:none;margin:12px 0;max-height:400px;overflow-y:auto}
.history-panel.open{display:block}
.history-item{display:flex;flex-direction:column;padding:10px 12px;border-radius:6px;cursor:pointer;transition:background 0.1s;border-bottom:1px solid rgba(47,61,74,0.3)}
.history-item:hover{background:#1f2a36}
.history-item .h-row{display:flex;align-items:center;gap:8px}
.h-type{min-width:48px;text-align:center;font-size:0.72em;padding:2px 6px;border-radius:4px;font-weight:600}
.h-type.analyze{background:rgba(52,152,219,0.15);color:#3498db}
.h-type.dissect{background:rgba(155,89,182,0.15);color:#9b59b6}
.h-type.debate{background:rgba(241,196,15,0.15);color:#f1c40f}
.h-text{font-size:0.85em;color:#c8d6e5;margin-top:6px;line-height:1.45;word-break:break-word;max-height:3em;overflow:hidden}
.h-time{font-size:0.72em;color:#657786;min-width:105px;text-align:right}
.h-score{min-width:38px;text-align:center;font-weight:700;font-size:0.83em}
.meta-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:4px 0}
.tag{font-size:0.74em;padding:2px 8px;border-radius:10px;background:rgba(52,152,219,0.12);color:#3498db}
@media(max-width:600px){.container{padding:12px}.tab-btn{padding:8px 14px;font-size:0.82em}}
pre{white-space:pre-wrap;word-wrap:break-word;font-family:inherit;font-size:0.84em;line-height:1.7;color:#c8d6e5}
</style>
</head>
<body>
<div class="container">
<h1>终极逻辑判断模型 · 九维思维矩阵</h1>
<div class="sub">三合一智能分析系统 — 逻辑评分 · 规则解剖 · 深度辩论</div>

<div class="tabs">
  <button class="tab-btn active" data-tab="analyze">📊 逻辑评分</button>
  <button class="tab-btn" data-tab="dissect">🔪 规则解剖</button>
  <button class="tab-btn" data-tab="debate">⚔️ 深度辩论</button>
</div>

<!-- ========== Tab 1: 逻辑评分 ========== -->
<div class="tab-content active" id="tab-analyze">
  <textarea id="analyzeInput" placeholder="输入要分析的文本...&#10;例: 所有成功人士都早起，所以只要早起就能成功"></textarea>
  <div style="display:flex;align-items:center;margin-top:8px">
    <span style="font-size:0.8em;color:#657786">分析模块</span>
    <span class="mod-toggle" id="toggleAll">全选/取消</span>
  </div>
  <div class="modules" id="modules"></div>
  <div class="btn-row">
    <button class="btn-primary" id="analyzeBtn">开始分析</button>
    <button class="btn-secondary" id="historyBtn">📋 历史记录</button>
  </div>
  <div class="status" id="analyzeStatus"></div>
</div>

<!-- ========== Tab 2: 规则解剖 ========== -->
<div class="tab-content" id="tab-dissect">
  <textarea id="dissectInput" placeholder="输入你的决策问题...&#10;例: 我的合伙人想稀释我的股份，怎么判断这是合理融资还是变相夺权？"></textarea>
  <div class="mode-select">
    <label><input type="radio" name="dissectMode" value="auto" checked><span>🔍 自动检测</span></label>
    <label><input type="radio" name="dissectMode" value="a"><span>♟️ 模式A 博弈分析</span></label>
    <label><input type="radio" name="dissectMode" value="b"><span>🧭 模式B 方向导航</span></label>
  </div>
  <div class="btn-row">
    <button class="btn-primary" id="dissectBtn">开始解剖</button>
    <button class="btn-primary" id="dissectDeepBtn" style="background:linear-gradient(135deg,#e74c3c,#f39c12)">解剖 + 深度辩论</button>
    <button class="btn-secondary" id="historyBtn2">📋 历史记录</button>
  </div>
  <div class="status" id="dissectStatus"></div>
</div>

<!-- ========== Tab 3: 深度辩论 ========== -->
<div class="tab-content" id="tab-debate">
  <textarea id="debateInput" placeholder="输入需要多角度深度分析的问题...&#10;例: 是否应该放弃稳定工作去追求高风险高回报的创业机会？"></textarea>
  <div class="btn-row">
    <button class="btn-primary" id="debateBtn" style="background:linear-gradient(135deg,#f39c12,#e74c3c)">5专家 × 3阶段深度辩论</button>
    <button class="btn-secondary" id="historyBtn3">📋 历史记录</button>
  </div>
  <div class="status" id="debateStatus"></div>
</div>

<!-- ========== Results ========== -->
<div id="results"></div>

<!-- ========== History ========== -->
<div class="history-panel" id="historyPanel">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-size:0.83em;color:#8899a6">分析历史</span>
    <div>
      <span id="historyCount" style="font-size:0.76em;color:#657786;margin-right:12px"></span>
      <button class="btn-sm btn-danger" id="clearHistoryBtn" style="margin-right:4px">清空</button>
      <button class="btn-sm btn-secondary" id="closeHistoryBtn">关闭</button>
    </div>
  </div>
  <div id="historyList"></div>
  <div id="historyEmpty" style="text-align:center;padding:20px;color:#657786;font-size:0.83em;display:none">暂无记录</div>
</div>

<div class="footer">终极逻辑判断模型 · 九维思维矩阵 v3.0 — 三合一智能分析系统</div>
</div>

<script>
// ===================== Tab Switching =====================
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    document.getElementById('results').innerHTML = '';
  });
});

// ===================== Tab 1: 逻辑评分 =====================
const mods = ["formal_logic","critical_inquiry","bias_detection","argumentation","elements_of_thought","structured_analysis","dialectical","source_thinking","simple_logic","zhihu_expert","llm_primary"];
const modLabels = {formal_logic:"形式逻辑",critical_inquiry:"批判性质询",bias_detection:"认知偏见",argumentation:"论证规则",elements_of_thought:"思维元素",structured_analysis:"结构化分析",dialectical:"辩证系统",source_thinking:"源思维",simple_logic:"简单逻辑",zhihu_expert:"知乎智慧",llm_primary:"LLM综合分析"};
let allSelected = true;
const mc = document.getElementById('modules');
mods.forEach(m => {
  const l = document.createElement('label');
  l.innerHTML = '<input type="checkbox" checked data-mod="'+m+'"><span>'+modLabels[m]+'</span>';
  l.querySelector('input').addEventListener('change',()=>{allSelected=false});
  mc.appendChild(l);
});
document.getElementById('toggleAll').addEventListener('click',()=>{
  allSelected = !allSelected;
  document.querySelectorAll('#modules input').forEach(cb => cb.checked = allSelected);
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const text = document.getElementById('analyzeInput').value.trim();
  if(!text) return;
  const sel = [...document.querySelectorAll('#modules input:checked')].map(cb => cb.dataset.mod);
  const btn = document.getElementById('analyzeBtn');
  const status = document.getElementById('analyzeStatus');
  btn.disabled = true; status.textContent = '分析中...';
  document.getElementById('results').innerHTML = '';
  try {
    const res = await fetch('/analyze', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text, modules:sel.length===mods.length?null:sel})});
    if(!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    renderAnalyzeResult(data);
    status.textContent = '分析完成';
  } catch(e) {
    document.getElementById('results').innerHTML = '<div class="error">请求失败: '+esc(e.message)+'</div>';
    status.textContent = '分析失败';
  }
  btn.disabled = false;
});

function renderAnalyzeResult(data) {
  const syn = data.synthesis || {};
  const s = (syn['逻辑质量评分']||'').match(/(\d+)\/100/);
  const sc = s ? parseInt(s[1]) : 0;
  const cls = sc>=70?'high':sc>=40?'mid':'low';
  let html = '<div class="score"><div class="score-badge '+cls+'">'+sc+'</div><div class="score-label">'+esc(syn['逻辑质量评分']||'')+'</div></div>';
  const warns = syn['警告']||[];
  if(warns.length && !(warns.length===1 && warns[0].includes('未检测到'))) {
    html += '<div class="section"><div class="section-title">⚠️ 警告</div><div class="items">';
    warns.forEach(w => html += '<div class="item warning">'+esc(w)+'</div>');
    html += '</div></div>';
  }
  const findings = syn['主要发现']||[];
  if(findings.length) {
    html += '<div class="section"><div class="section-title">💡 主要发现</div><div class="items">';
    findings.forEach(f => html += '<div class="item finding">'+esc(f)+'</div>');
    html += '</div></div>';
  }
  const sug = syn['行动建议']||[];
  if(sug.length) {
    html += '<div class="section"><div class="section-title">🎯 行动建议</div><div class="items">';
    sug.forEach(s => html += '<div class="item suggestion">'+esc(s)+'</div>');
    html += '</div></div>';
  }
  const md = data.modules||{};
  ['formal_logic','critical_inquiry','bias_detection','argumentation','elements_of_thought','structured_analysis','dialectical','source_thinking','simple_logic','llm_primary'].forEach(k => {
    const m = md[k]; if(!m||!Object.keys(m).length) return;
    const lines = [];
    Object.values(m).forEach(v => {
      if(Array.isArray(v)) v.forEach(x => lines.push(typeof x==='string'?x:JSON.stringify(x)));
      else if(typeof v==='object') Object.entries(v).forEach(([k,v]) => lines.push(k+': '+v));
    });
    if(!lines.length) return;
    html += '<div class="card open"><div class="card-header"><span>'+esc(modLabels[k]||k)+'</span><span class="arrow">▼</span></div><div class="card-body">';
    lines.forEach(l => html += '<div class="line'+(l.includes('谬误')?' warn':'')+'">'+esc(l)+'</div>');
    html += '</div></div>';
  });
  // 逻辑猎手
  function renderHunter(mk, label) {
    let h = md[mk]; if(!h||!h['问题列表']||!h['问题列表'].length) return;
    html += '<div class="card open"><div class="card-header"><span>'+label+'</span><span class="arrow">▼</span></div><div class="card-body">';
    h['问题列表'].forEach(item => {
      const sev = item['严重程度']||'中';
      const cls2 = sev==='高'?'warn':sev==='中'?'':'ok';
      html += '<div class="line '+cls2+'">'+esc(item['修正建议']||'')+'</div>';
      html += '<div style="padding:0 0 2px 12px;font-size:0.76em;color:#657786;">↳ '+esc(item['问题类型']||'')+' ('+esc(sev)+') — '+esc((item['问题说明']||'').slice(0,150))+'</div>';
    });
    html += '</div></div>';
  }
  renderHunter('logic_problem_hunter_1','🔍 逻辑猎手1 — DeepSeek 深度审查');
  renderHunter('logic_problem_hunter_2','🔍 逻辑猎手2 — 豆包大模型');
  document.getElementById('results').innerHTML = html;
  bindCards();
}

// ===================== Tab 2: 规则解剖 =====================
document.getElementById('dissectBtn').addEventListener('click', async () => {
  const text = document.getElementById('dissectInput').value.trim();
  if(!text) return;
  const mode = document.querySelector('input[name="dissectMode"]:checked').value;
  const btn = document.getElementById('dissectBtn');
  const status = document.getElementById('dissectStatus');
  btn.disabled = true; status.textContent = '解剖分析中...';
  document.getElementById('results').innerHTML = '';
  try {
    const res = await fetch('/dissect', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text, mode})});
    if(!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    renderDissectResult(data);
    status.textContent = '解剖完成';
  } catch(e) {
    document.getElementById('results').innerHTML = '<div class="error">请求失败: '+esc(e.message)+'</div>';
    status.textContent = '失败';
  }
  btn.disabled = false;
});

document.getElementById('dissectDeepBtn').addEventListener('click', async () => {
  const text = document.getElementById('dissectInput').value.trim();
  if(!text) return;
  const mode = document.querySelector('input[name="dissectMode"]:checked').value;
  const btn = document.getElementById('dissectDeepBtn');
  const status = document.getElementById('dissectStatus');
  btn.disabled = true; status.textContent = '阶段1: 解剖分析...';
  document.getElementById('results').innerHTML = '';
  try {
    const res1 = await fetch('/dissect', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text, mode})});
    if(!res1.ok) throw new Error('HTTP '+res1.status);
    const d = await res1.json();
    status.textContent = '阶段2: 深度辩论...';
    const res2 = await fetch('/debate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text, dissection_result: d})});
    if(!res2.ok) throw new Error('HTTP '+res2.status);
    const debate = await res2.json();
    renderDeepResult(d, debate);
    status.textContent = '全流程完成';
  } catch(e) {
    document.getElementById('results').innerHTML = '<div class="error">请求失败: '+esc(e.message)+'</div>';
    status.textContent = '失败';
  }
  btn.disabled = false;
});

function renderDissectResult(data) {
  let html = '';
  const mj = data['模式判定']||{};
  if(Object.keys(mj).length) {
    html += '<div class="score" style="padding:16px"><div style="font-size:1.1em;font-weight:600">'+esc(mj['模式']||'未知')+'</div><div class="score-label">'+esc(mj['依据']||'')+' (置信度: '+esc(mj['置信度']||'?')+')</div></div>';
  }
  const gm = data['博弈地图']||{};
  if(Object.keys(gm).length) {
    html += '<div class="card open"><div class="card-header"><span>🗺️ 博弈地图</span><span class="arrow">▼</span></div><div class="card-body">';
    Object.entries(gm).forEach(([k,v]) => {
      if(k.startsWith('_')) return;
      if(Array.isArray(v)) v.forEach(x => html += '<div class="line">'+esc(k)+': '+esc(typeof x==='string'?x:JSON.stringify(x))+'</div>');
      else html += '<div class="line">'+esc(k)+': '+esc(String(v))+'</div>';
    });
    html += '</div></div>';
  }
  const risks = data['风险计算']||{};
  if(Object.keys(risks).length) {
    html += '<div class="card open"><div class="card-header"><span>⚠️ 风险扫描</span><span class="arrow">▼</span></div><div class="card-body">';
    Object.entries(risks).forEach(([k,v]) => {if(!k.startsWith('_')) html += '<div class="line">'+esc(k)+': '+esc(String(v))+'</div>';});
    html += '</div></div>';
  }
  const conflicts = data['公理冲突检查']||{};
  if(Object.keys(conflicts).length) {
    html += '<div class="card open"><div class="card-header"><span>⚡ 公理冲突裁决</span><span class="arrow">▼</span></div><div class="card-body">';
    html += '<div class="line">活跃公理: '+esc((conflicts['活跃公理列表']||[]).join('、'))+'</div>';
    (conflicts['冲突列表']||[]).forEach(c => {
      if(typeof c==='object') html += '<div class="line warn">'+esc(c['公理A']||'')+' vs '+esc(c['公理B']||'')+' → '+esc(c['裁决']||'')+'</div>';
    });
    html += '</div></div>';
  }
  const actions = data['行动指令']||[];
  if(actions.length) {
    html += '<div class="section"><div class="section-title">🎯 行动指令</div><div class="items">';
    actions.forEach(a => html += '<div class="item suggestion">'+esc(a)+'</div>');
    html += '</div></div>';
  }
  const preds = data['预测']||[];
  if(preds.length) {
    html += '<div class="section"><div class="section-title">📈 预测</div><div class="items">';
    preds.forEach(p => html += '<div class="item neutral">['+esc(p['置信度']||'?')+'] '+esc((p['text']||'').slice(0,200))+'</div>');
    html += '</div></div>';
  }
  document.getElementById('results').innerHTML = html || '<div class="error">无结构化结果，请查看原始输出</div>';
  bindCards();
}

// ===================== Tab 3: 深度辩论 =====================
document.getElementById('debateBtn').addEventListener('click', async () => {
  const text = document.getElementById('debateInput').value.trim();
  if(!text) return;
  const btn = document.getElementById('debateBtn');
  const status = document.getElementById('debateStatus');
  btn.disabled = true; status.textContent = '5位专家辩论中...';
  document.getElementById('results').innerHTML = '';
  try {
    const res = await fetch('/debate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    if(!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    renderDebateResult(data);
    status.textContent = '辩论完成';
  } catch(e) {
    document.getElementById('results').innerHTML = '<div class="error">请求失败: '+esc(e.message)+'</div>';
    status.textContent = '失败';
  }
  btn.disabled = false;
});

function renderDebateResult(data) {
  let html = '';
  const experts = data['专家分析']||{};
  if(Object.keys(experts).length) {
    Object.entries(experts).forEach(([name, content]) => {
      html += '<div class="card"><div class="card-header"><span>👤 '+esc(name)+'</span><span class="arrow">▼</span></div><div class="card-body"><pre>'+esc(typeof content==='string'?content:JSON.stringify(content,null,2))+'</pre></div></div>';
    });
  }
  const synthesis = data['综合裁决']||data['辩论总结']||'';
  if(synthesis) {
    html += '<div class="card open"><div class="card-header"><span>🏛️ 综合裁决</span><span class="arrow">▼</span></div><div class="card-body"><pre>'+esc(typeof synthesis==='string'?synthesis:JSON.stringify(synthesis,null,2))+'</pre></div></div>';
  }
  const phases = data['辩论阶段']||{};
  if(Object.keys(phases).length) {
    Object.entries(phases).forEach(([phase, content]) => {
      html += '<div class="card"><div class="card-header"><span>📝 '+esc(phase)+'</span><span class="arrow">▼</span></div><div class="card-body"><pre>'+esc(typeof content==='string'?content:JSON.stringify(content,null,2))+'</pre></div></div>';
    });
  }
  document.getElementById('results').innerHTML = html || '<div class="error">无辩论结果</div>';
  bindCards();
}

// ===================== Deep result (dissect + debate) =====================
function renderDeepResult(dissectData, debateData) {
  let html = '<div class="section"><div class="section-title" style="font-size:1em;color:#9b59b6">🔪 阶段1: 规则解剖</div></div>';
  document.getElementById('results').innerHTML = html;
  renderDissectResult(dissectData);
  html = document.getElementById('results').innerHTML;
  html += '<div class="section" style="margin-top:24px"><div class="section-title" style="font-size:1em;color:#f39c12">⚔️ 阶段2: 深度辩论</div></div>';
  document.getElementById('results').innerHTML = html;
  const debateEl = document.createElement('div');
  const oldResults = document.getElementById('results');
  // Render debate into a temp area then append
  renderDebateResult(debateData);
}

// ===================== History =====================
function openHistory() {
  document.getElementById('historyPanel').classList.add('open');
  fetchHistory();
}
document.getElementById('historyBtn').addEventListener('click', openHistory);
document.getElementById('historyBtn2').addEventListener('click', openHistory);
document.getElementById('historyBtn3').addEventListener('click', openHistory);
document.getElementById('closeHistoryBtn').addEventListener('click', () => {
  document.getElementById('historyPanel').classList.remove('open');
});

async function fetchHistory() {
  const list = document.getElementById('historyList');
  const empty = document.getElementById('historyEmpty');
  const count = document.getElementById('historyCount');
  list.innerHTML = '<div style="text-align:center;padding:12px;color:#657786">加载中...</div>';
  empty.style.display = 'none';
  try {
    const res = await fetch('/history?limit=30');
    if(!res.ok) throw new Error('HTTP '+res.status);
    const rows = await res.json();
    if(!rows.length) { list.innerHTML=''; empty.style.display='block'; count.textContent=''; return; }
    count.textContent = '共 '+rows.length+' 条';
    list.innerHTML = rows.map(r => {
      const typeLabel = {'analyze':'评分','dissect':'解剖','debate':'辩论'}[r.analysis_type]||'评分';
      const typeCls = r.analysis_type||'analyze';
      const scoreHtml = r.score ? '<span class="h-score" style="color:'+(r.score>=70?'#27ae60':r.score>=40?'#f39c12':'#e74c3c')+'">'+r.score+'</span>' : '';
      var txt = r.text||''; if(txt.length>120) txt=txt.substring(0,120)+'...';
      return '<div class="history-item" data-id="'+r.id+'"><div class="h-row"><span class="h-type '+typeCls+'">'+typeLabel+'</span>'+scoreHtml+'<span class="h-time">'+esc(r.created_at||'')+'</span><span style="flex:1"></span><button class="btn-sm btn-secondary view-btn" data-id="'+r.id+'">查看</button><button class="btn-sm btn-danger del-btn" data-id="'+r.id+'">删</button></div><div class="h-text">'+esc(txt)+'</div></div>';
    }).join('');
    list.querySelectorAll('.view-btn').forEach(btn => btn.addEventListener('click', async e => {
      e.stopPropagation();
      const id = e.target.dataset.id;
      document.getElementById('historyPanel').classList.remove('open');
      const res = await fetch('/history/'+id);
      const data = await res.json();
      const result = data.result||data;
      const atype = data.analysis_type||'analyze';
      if(atype==='dissect') renderDissectResult(result);
      else if(atype==='debate') renderDebateResult(result);
      else renderAnalyzeResult(result);
    }));
    list.querySelectorAll('.del-btn').forEach(btn => btn.addEventListener('click', async e => {
      e.stopPropagation();
      if(!confirm('确定删除？')) return;
      await fetch('/history/'+e.target.dataset.id, {method:'DELETE'});
      fetchHistory();
    }));
  } catch(e) {
    list.innerHTML = '<div style="text-align:center;padding:12px;color:#e74c3c">加载失败: '+esc(e.message)+'</div>';
  }
}

document.getElementById('clearHistoryBtn').addEventListener('click', async () => {
  if(!confirm('确定清空全部历史记录？此操作不可撤销。')) return;
  await fetch('/history', {method:'DELETE'});
  fetchHistory();
});

// ===================== Helpers =====================
function esc(s) { const d = document.createElement('div'); d.textContent = String(s); return d.innerHTML; }
function bindCards() {
  document.querySelectorAll('#results .card-header').forEach(h => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });
}
</script>
</body>
</html>"""

from ljmodel import LogicJudgeModel
from ljmodel.model import ALL_MODULES
from ljmodel.database import list_analyses, get_analysis, delete_analysis, search_analyses, clear_history as db_clear, save_analysis, _get_conn
from ljmodel.knowledge_base import KNOWLEDGE_BASE, reload_books

app = FastAPI(
    title="终极逻辑判断模型 API",
    version="3.0.0",
    description="三合一智能分析系统 — 逻辑评分 · 规则解剖 · 深度辩论",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB Migration: add analysis_type column ---
def _migrate_db():
    """Add analysis_type column if missing (for older DBs)"""
    try:
        with _get_conn() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(analyses)").fetchall()]
            if "analysis_type" not in cols:
                conn.execute("ALTER TABLE analyses ADD COLUMN analysis_type TEXT DEFAULT 'analyze'")
    except Exception:
        pass

_migrate_db()

# --- Pydantic Schemas ---
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="待分析文本")
    modules: Optional[list[str]] = Field(None, description="可选，要运行的模块列表")
    html: bool = Field(False, description="是否在响应中包含HTML报告")

class BatchRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, description="待分析文本列表")
    modules: Optional[list[str]] = Field(None, description="可选，要运行的模块列表")

class DissectRequest(BaseModel):
    text: str = Field(..., min_length=1, description="待解剖的决策问题")
    mode: str = Field("auto", description="解剖模式: auto / a / b")

class DebateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="待辩论的问题")
    dissection_result: Optional[dict] = Field(None, description="可选，解剖分析结果（用于全流程）")

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "3.0.0"

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
        "zhihu_expert": "知乎集体智慧 — 从高赞回答中提炼的真实世界经验",
        "llm_primary": "LLM综合分析 — 使用大模型进行多框架综合评估",
    }
    return [ModuleInfo(name=n, description=descriptions.get(n, "")) for n in ALL_MODULES]

# ---- 系统一：逻辑评分 ----
@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    judge = get_judge()
    try:
        result = await asyncio.to_thread(judge.analyze, req.text, False, None, req.modules)
        if req.html and result["modules"].get("llm_primary"):
            from ljmodel.report_html import generate_html_report
            result["html_report"] = generate_html_report(result)
        # Save to history
        score_str = (result.get("synthesis", {}).get("逻辑质量评分", "") or "")
        try:
            score = int(score_str.split("/")[0])
        except Exception:
            score = 0
        save_analysis(req.text, score, req.modules or list(ALL_MODULES.keys()), result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/batch")
async def analyze_batch(req: BatchRequest):
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

# ---- 系统二：规则解剖 ----
@app.post("/dissect")
async def dissect(req: DissectRequest):
    judge = get_judge()
    try:
        result = await asyncio.to_thread(judge.dissect, req.text, req.mode, False)
        # Save with analysis_type
        with _get_conn() as conn:
            import json
            conn.execute(
                "INSERT INTO analyses (text, score, modules, result, analysis_type) VALUES (?, ?, ?, ?, ?)",
                (req.text, 0, json.dumps([], ensure_ascii=False),
                 json.dumps(result, ensure_ascii=False), "dissect")
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- 系统三：深度辩论 ----
@app.post("/debate")
async def debate(req: DebateRequest):
    judge = get_judge()
    try:
        result = await asyncio.to_thread(
            judge.debate, req.text, False,
            req.dissection_result, None
        )
        # Save with analysis_type
        with _get_conn() as conn:
            import json
            conn.execute(
                "INSERT INTO analyses (text, score, modules, result, analysis_type) VALUES (?, ?, ?, ?, ?)",
                (req.text, 0, json.dumps([], ensure_ascii=False),
                 json.dumps(result, ensure_ascii=False), "debate")
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- History Endpoints ----
@app.get("/history")
async def history_list(limit: int = 30, q: str = ""):
    if q:
        return search_analyses(q, limit)
    return list_analyses(limit)

@app.get("/history/{hid}")
async def history_detail(hid: int):
    row = get_analysis(hid)
    if row is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return row

@app.delete("/history/{hid}")
async def history_delete(hid: int):
    ok = delete_analysis(hid)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"status": "deleted", "id": hid}

@app.delete("/history")
async def history_clear():
    count = db_clear()
    return {"status": "cleared", "deleted": count}

# ---- Book Endpoints ----
@app.get("/books")
async def books_list():
    return [{"name": k, "source": v.get("source", ""), "description": v.get("description", "")}
            for k, v in KNOWLEDGE_BASE.items()]

@app.get("/books/{book_name}")
async def book_detail(book_name: str):
    book = KNOWLEDGE_BASE.get(book_name)
    if book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return book

@app.post("/books/reload")
async def books_reload():
    loaded = reload_books()
    return {"status": "reloaded", "books": loaded}

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    import uvicorn
    print(f"  终极逻辑判断模型 API v3.0 启动于 http://{host}:{port}")
    print(f"  三系统: 逻辑评分 · 规则解剖 · 深度辩论")
    print(f"  API文档: http://localhost:{port}/docs")
    if reload:
        print(f"  自动重载已开启")
    kwargs = dict(host=host, port=port)
    if reload:
        kwargs["reload"] = True
        kwargs["reload_includes"] = ["*.py", "*.yaml"]
        kwargs["app"] = "api_server:app"
    else:
        kwargs["app"] = app
    uvicorn.run(**kwargs)
