"""HTML报告生成器 — 从分析结果生成美观的HTML报告"""

import json
import os
import datetime


def generate_html_report(result: dict, output_path: str = None) -> str:
    """从分析结果生成自包含HTML报告

    Args:
        result: analyze() 返回的完整结果字典
        output_path: 可选的输出文件路径，不传则只返回HTML字符串

    Returns:
        str: HTML内容
    """
    modules = result["modules"]
    synthesis = result["synthesis"]
    input_text = result.get("input", "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 提取关键数据
    score_text = synthesis.get("逻辑质量评分", "待评估")
    score_value = _extract_score(synthesis)
    findings = synthesis.get("主要发现", [])
    warnings = synthesis.get("警告", [])
    suggestions = synthesis.get("行动建议", [])

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>逻辑判断分析报告</title>
<style>
  :root {{
    --bg: #f5f7fa;
    --card: #ffffff;
    --text: #2c3e50;
    --accent: #3498db;
    --warn: #e74c3c;
    --ok: #27ae60;
    --border: #e8ecf1;
    --muted: #95a5a6;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, 'Segoe UI', 'Noto Sans SC', sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }}
  .header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color:#fff; padding:40px 30px; text-align:center; }}
  .header h1 {{ font-size:1.6em; margin-bottom:8px; }}
  .header .sub {{ opacity:0.85; font-size:0.9em; }}
  .header .time {{ opacity:0.6; font-size:0.8em; margin-top:12px; }}
  .container {{ max-width:960px; margin:0 auto; padding:20px; }}

  /* Score */
  .score-card {{ background:var(--card); border-radius:12px; padding:30px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.06); text-align:center; }}
  .score-badge {{ display:inline-block; width:100px; height:100px; line-height:100px; border-radius:50%; font-size:2em; font-weight:700; color:#fff; }}
  .score-badge.high {{ background:var(--ok); }}
  .score-badge.mid {{ background:#f39c12; }}
  .score-badge.low {{ background:var(--warn); }}
  .score-label {{ margin-top:12px; font-size:1.1em; color:var(--muted); }}

  /* Cards */
  .card {{ background:var(--card); border-radius:10px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,0.05); overflow:hidden; }}
  .card-header {{ padding:14px 20px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; user-select:none; transition:background 0.15s; }}
  .card-header:hover {{ background:#f8f9fb; }}
  .card-header h2 {{ font-size:1em; }}
  .card-header .arrow {{ transition:transform 0.2s; font-size:0.8em; color:var(--muted); }}
  .card-body {{ padding:0 20px 20px; display:none; }}
  .card.open .card-body {{ display:block; }}
  .card.open .arrow {{ transform:rotate(180deg); }}

  /* Items */
  .item {{ padding:6px 0; font-size:0.93em; }}
  .item::before {{ content:"•"; color:var(--accent); margin-right:8px; }}
  .item.warn::before {{ content:"⚠"; color:var(--warn); }}
  .item.ok::before {{ content:"✓"; color:var(--ok); }}
  .item.warn {{ color:#c0392b; }}
  .item.indent {{ padding-left:20px; font-size:0.88em; color:var(--muted); }}
  .prob {{ background:#fef0f0; border-left:3px solid var(--warn); padding:6px 12px; margin:4px 0; font-size:0.88em; border-radius:0 4px 4px 0; }}

  /* Input box */
  .input-box {{ background:#f0f4f8; border-radius:8px; padding:14px 18px; font-size:0.9em; word-break:break-word; border:1px solid var(--border); margin-bottom:20px; }}

  /* Warnings */
  .warning-list {{ padding:0; }}
  .warning-item {{ background:#fff5f5; border:1px solid #fed7d7; border-radius:6px; padding:8px 14px; margin:4px 0; font-size:0.9em; color:#c53030; list-style:none; }}
  .finding-item {{ background:#f0fff4; border:1px solid #c6f6d5; border-radius:6px; padding:8px 14px; margin:4px 0; font-size:0.9em; color:#276749; list-style:none; }}
  .suggestion-item {{ background:#ebf8ff; border:1px solid #bee3f8; border-radius:6px; padding:8px 14px; margin:4px 0; font-size:0.9em; color:#2b6cb0; list-style:none; }}

  /* LLM section */
  .llm-dim {{ background:#f8fafc; border-radius:6px; padding:10px 14px; margin:6px 0; border:1px solid var(--border); }}
  .llm-dim h4 {{ font-size:0.9em; color:var(--accent); margin-bottom:4px; }}

  @media (max-width:640px) {{
    .header {{ padding:24px 16px; }}
    .header h1 {{ font-size:1.2em; }}
    .container {{ padding:12px; }}
    .score-badge {{ width:80px; height:80px; line-height:80px; font-size:1.6em; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>终极逻辑判断模型</h1>
  <div class="sub">九维思维矩阵 · 综合分析报告</div>
  <div class="time">{timestamp}</div>
</div>
<div class="container">

  <div class="input-box"><strong>分析文本：</strong>{_escape_html(input_text[:200])}{'…' if len(input_text) > 200 else ''}</div>

  <div class="score-card">
    {_score_html(score_value)}
    <div class="score-label">{_escape_html(score_text)}</div>
  </div>
"""

    # 警告
    if warnings and not (len(warnings) == 1 and warnings[0] == "未检测到严重的逻辑问题"):
        html += """  <div class="card open"><div class="card-header"><h2>⚠ 警告</h2><span class="arrow">▼</span></div><div class="card-body"><ul class="warning-list">"""
        for w in warnings:
            html += f'<li class="warning-item">{_escape_html(w)}</li>'
        html += "</ul></div></div>"

    # 主要发现
    if findings:
        html += """  <div class="card open"><div class="card-header"><h2>📌 主要发现</h2><span class="arrow">▼</span></div><div class="card-body"><ul class="warning-list">"""
        for f in findings:
            html += f'<li class="finding-item">{_escape_html(f)}</li>'
        html += "</ul></div></div>"

    # 行动建议
    if suggestions:
        html += """  <div class="card open"><div class="card-header"><h2>💡 行动建议</h2><span class="arrow">▼</span></div><div class="card-body"><ul class="warning-list">"""
        for s in suggestions:
            html += f'<li class="suggestion-item">{_escape_html(s)}</li>'
        html += "</ul></div></div>"

    # 各模块详细结果
    module_configs = [
        ("formal_logic", "模块1 · 形式逻辑分析", "逻辑学十五讲"),
        ("critical_inquiry", "模块2 · 批判性质询", "学会提问"),
        ("bias_detection", "模块3 · 认知偏见检测", "思考,快与慢"),
        ("argumentation", "模块4 · 论证规则评估", "论证是一门学问"),
        ("elements_of_thought", "模块5 · 思维元素分析", "批判性思维工具"),
        ("structured_analysis", "模块6 · 结构化分析", "麦肯锡逻辑思维"),
        ("dialectical", "模块7 · 辩证系统分析", "世界的逻辑"),
        ("source_thinking", "模块8 · 源思维深度分析", "源思维"),
        ("simple_logic", "模块10 · 简单逻辑深度分析", "简单的逻辑学"),
    ]

    for module_key, module_title, module_book in module_configs:
        data = modules.get(module_key, {})
        if not data:
            continue
        html += f"""  <div class="card"><div class="card-header"><h2>{module_title} <span style="font-weight:400;color:var(--muted);font-size:0.85em">— {module_book}</span></h2><span class="arrow">▼</span></div><div class="card-body">"""
        for section_key, section_items in data.items():
            if not section_items:
                continue
            if isinstance(section_items, list):
                for item in section_items:
                    if isinstance(item, dict):
                        if "keyword" in item and "description" in item:
                            cls = "warn" if "谬误" in section_key else ""
                            html += f'<div class="item {cls}"><strong>{_escape_html(item["keyword"])}</strong>: {_escape_html(item.get("description", ""))}</div>'
                        elif "bias" in item and "trigger" in item:
                            html += f'<div class="item warn"><strong>{_escape_html(item["bias"])}</strong> (触发: {_escape_html(item["trigger"])})</div>'
                        else:
                            html += f'<div class="item">{_escape_html(str(item))}</div>'
                    elif isinstance(item, str):
                        cls = ""
                        if "!" in item or "谬误" in item:
                            cls = "warn"
                        elif "OK" in item or "有效" in item:
                            cls = "ok"
                        html += f'<div class="item{(" " + cls) if cls else ""}">{_escape_html(item)}</div>'
                html += ""
            elif isinstance(section_items, dict):
                html += f"<h4 style='font-size:0.9em;color:var(--muted);margin:8px 0 4px;'>{_escape_html(section_key)}</h4>"
                for k, v in section_items.items():
                    html += f'<div class="item"><strong>{_escape_html(str(k))}</strong>: {_escape_html(str(v)[:200])}</div>'
        html += "</div></div>"

    # LLM综合分析
    llm = modules.get("llm_primary", {})
    if llm and "error" not in llm:
        dims = llm.get("维度分析", {})
        html += f"""  <div class="card"><div class="card-header"><h2>模块9 · LLM综合分析 <span style="font-weight:400;color:var(--muted);font-size:0.85em">— DeepSeek 9本书框架</span></h2><span class="arrow">▼</span></div><div class="card-body">"""
        dim_labels = {
            "形式逻辑": "逻辑学十五讲", "批判性质询": "学会提问",
            "认知偏见": "思考,快与慢", "论证规则": "论证是一门学问",
            "思维元素": "批判性思维工具", "结构化": "麦肯锡逻辑思维",
            "辩证系统": "世界的逻辑", "源思维": "源思维"
        }
        for dim_key, dim_label in dim_labels.items():
            dim_data = dims.get(dim_key, {})
            if not dim_data:
                continue
            analysis_text = dim_data.get("分析", "")
            problems = dim_data.get("问题", [])
            if not analysis_text and not problems:
                continue
            html += f"""<div class="llm-dim"><h4>{_escape_html(dim_key)} ({_escape_html(dim_label)})</h4>"""
            if analysis_text:
                html += f'<div class="item">{_escape_html(analysis_text[:500])}</div>'
            for p in problems:
                html += f'<div class="prob">⚠ {_escape_html(p)}</div>'
            html += "</div>"

        llm_suggestions = llm.get("行动建议", [])
        if llm_suggestions:
            html += "<h4 style='margin-top:12px;'>LLM 行动建议</h4>"
            for s in llm_suggestions:
                html += f'<div class="suggestion-item">{_escape_html(s)}</div>'
        html += "</div></div>"

    # Footer
    html += f"""
  <div style="text-align:center;padding:30px 0;color:var(--muted);font-size:0.85em;">
    终极逻辑判断模型 · 九维思维矩阵 v2.0<br>
    生成时间: {timestamp}
  </div>
</div>

<script>
document.querySelectorAll('.card-header').forEach(h => {{
  h.addEventListener('click', () => {{
    h.parentElement.classList.toggle('open');
  }});
}});
</script>
</body>
</html>"""

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html


def _extract_score(synthesis: dict) -> int:
    """从评分文本中提取数字分数"""
    score_text = synthesis.get("逻辑质量评分", "")
    import re
    match = re.search(r'(\d+)/100', score_text)
    if match:
        return int(match.group(1))
    return 0


def _score_html(score: int) -> str:
    """生成分数圆环HTML"""
    if score >= 70:
        cls = "high"
    elif score >= 40:
        cls = "mid"
    else:
        cls = "low"
    return f'<div class="score-badge {cls}">{score}</div>'


def _escape_html(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
