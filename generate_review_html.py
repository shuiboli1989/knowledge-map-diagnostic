"""为试题 JSON 生成直观的 HTML 审阅页面"""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = Path(__file__).parent / "data"

# 读取知识图谱获取节点名称
with open(DATA_DIR / "graph_course_china_finance.json", 'r', encoding='utf-8') as f:
    graph = json.load(f)
node_map = {n['id']: n['name'] for n in graph['nodes']}

level_map = {
    'memory': ('记忆', '#6366F1'),
    'understanding': ('理解', '#10B981'),
    'application': ('应用', '#F59E0B'),
    'analysis': ('分析', '#EF4444'),
}


def generate_html(questions, title, subtitle, output_path):
    rows = []
    current_node = None
    for i, q in enumerate(questions):
        node_id = q['node_id']
        node_name = node_map.get(node_id, node_id)
        level = q.get('level', '')
        level_cn, level_color = level_map.get(level, (level, '#666'))

        # 知识点分组标题
        if node_id != current_node:
            current_node = node_id
            rows.append(f'''
            <tr class="node-header">
                <td colspan="5">
                    <span class="node-id">{node_id}</span>
                    <span class="node-name">{node_name}</span>
                </td>
            </tr>''')

        # 选项 HTML
        options_html = '<br>'.join(
            f'<span class="{"correct-option" if opt.startswith(q["answer"] + ".") else ""}">{opt}</span>'
            for opt in q.get('options', [])
        )

        explanation = q.get('explanation', '')

        rows.append(f'''
            <tr>
                <td class="col-id">{q["id"]}</td>
                <td class="col-level"><span class="level-tag" style="background:{level_color};">{level_cn}</span></td>
                <td class="col-question">{q["question"]}</td>
                <td class="col-options">{options_html}</td>
                <td class="col-explain">
                    <span class="answer-badge">{q["answer"]}</span>
                    <details open><summary>解析</summary><p>{explanation}</p></details>
                </td>
            </tr>''')

    # 统计
    total = len(questions)
    dist = {}
    for q in questions:
        dist[q['answer']] = dist.get(q['answer'], 0) + 1
    dist_str = '  '.join(f'{k}: {v}' for k, v in sorted(dist.items()))
    level_dist = {}
    for q in questions:
        l = level_map.get(q.get('level', ''), (q.get('level', ''),))[0]
        level_dist[l] = level_dist.get(l, 0) + 1
    level_str = '  '.join(f'{k}: {v}' for k, v in level_dist.items())
    node_count = len(set(q['node_id'] for q in questions))

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #F5F5F7; color: #1A1A1A; padding: 24px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    .header {{ background: #fff; border-radius: 12px; padding: 32px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .header h1 {{ font-size: 24px; margin-bottom: 8px; color: #1A1A1A; }}
    .header .subtitle {{ font-size: 14px; color: #888; margin-bottom: 16px; }}
    .stats {{ display: flex; gap: 24px; flex-wrap: wrap; }}
    .stat-item {{ background: #F8F9FA; border-radius: 8px; padding: 12px 20px; }}
    .stat-item .label {{ font-size: 12px; color: #888; }}
    .stat-item .value {{ font-size: 18px; font-weight: 600; color: #333; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    th {{ background: #F8F9FA; padding: 14px 12px; text-align: left; font-size: 13px; color: #666; font-weight: 600; border-bottom: 2px solid #E5E7EB; }}
    td {{ padding: 12px; border-bottom: 1px solid #F0F0F0; vertical-align: top; font-size: 13px; line-height: 1.7; }}
    tr:hover td {{ background: #FAFBFC; }}
    .node-header td {{ background: #EEF2FF !important; padding: 10px 16px; font-weight: 600; border-bottom: 2px solid #C7D2FE; }}
    .node-id {{ font-size: 11px; color: #6366F1; background: #E0E7FF; padding: 2px 8px; border-radius: 4px; margin-right: 8px; }}
    .node-name {{ font-size: 14px; color: #3730A3; }}
    .col-id {{ width: 100px; color: #888; font-family: monospace; font-size: 12px; }}
    .col-level {{ width: 60px; text-align: center; }}
    .col-question {{ width: 35%; }}
    .col-options {{ width: 30%; }}
    .col-explain {{ width: 20%; }}
    .level-tag {{ color: #fff; padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: 500; }}
    .correct-option {{ color: #15803D; font-weight: 600; }}
    .answer-badge {{ display: inline-block; background: #DCFCE7; color: #15803D; font-weight: 700; padding: 2px 10px; border-radius: 6px; font-size: 13px; margin-bottom: 6px; }}
    details {{ margin-top: 6px; }}
    details summary {{ cursor: pointer; color: #6366F1; font-size: 12px; }}
    details p {{ margin-top: 6px; color: #555; font-size: 12px; line-height: 1.6; }}
    .footer {{ text-align: center; padding: 24px; color: #aaa; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
        <div class="stats">
            <div class="stat-item"><div class="label">总题数</div><div class="value">{total}</div></div>
            <div class="stat-item"><div class="label">知识点数</div><div class="value">{node_count}</div></div>
            <div class="stat-item"><div class="label">题型分布</div><div class="value">{level_str}</div></div>
            <div class="stat-item"><div class="label">答案分布</div><div class="value">{dist_str}</div></div>
        </div>
    </div>
    <table>
        <thead>
            <tr>
                <th>题号</th>
                <th>层级</th>
                <th>题目</th>
                <th>选项</th>
                <th>答案 / 解析</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    <div class="footer">中国金融学 · 系统性金融风险防控 · 试题审阅</div>
</div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"已生成：{output_path}")


# 生成两份 HTML
with open(DATA_DIR / "questions_course_china_finance.json", 'r', encoding='utf-8') as f:
    q1 = json.load(f)

with open(DATA_DIR / "questions_course_china_finance_llm.json", 'r', encoding='utf-8') as f:
    q2 = json.load(f)

generate_html(
    q1,
    "中国金融学试题审阅 — Claude 生成版",
    "由 Claude 根据知识图谱直接生成，共 22 个知识点 × 3 层级",
    DATA_DIR / "review_questions_claude.html"
)

generate_html(
    q2,
    "中国金融学试题审阅 — OpenTrek-72B 生成版",
    "由 OpenTrek-72B（modelCode: 12003）通过 API 调用生成，共 22 个知识点 × 3 层级",
    DATA_DIR / "review_questions_llm.html"
)
