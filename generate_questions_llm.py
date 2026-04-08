"""调用 OpenTrek-72B 为中国金融学知识图谱生成试题"""
import requests
import json
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "https://ai-chat.hep.com.cn/llm/chat/completions"
SYSTEM_TOKEN = "$1$jn7hHZvm$YFRCbYMuJMuNyJ939ylo.1"
MODEL_CODE = 12003

# 读取知识图谱
graph_path = Path(__file__).parent / "data" / "graph_course_china_finance.json"
with open(graph_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

nodes = graph['nodes']


def call_llm(prompt, max_retries=3):
    """调用大模型 API"""
    headers = {
        "system-token": SYSTEM_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "你是一位金融学教育专家，擅长根据知识点出题。请严格按照要求的JSON格式输出，不要输出任何多余内容。"},
            {"role": "user", "content": prompt}
        ],
        "modelCode": MODEL_CODE,
        "stream": False,
        "advanced_config": {
            "summary_config": {
                "max_tokens": 4096,
                "tempernature": 0.7,
                "top_p": 0.8
            }
        }
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
            result = resp.json()
            if isinstance(result, list):
                result = result[0]
            content = result.get('choices', [{}])[0].get('content', '')
            if not content:
                content = result.get('message', {}).get('content', '')
            return content
        except Exception as e:
            print(f"  请求失败 (尝试 {attempt+1}/{max_retries}): {e}")
            time.sleep(3)
    return None


def build_prompt(node):
    """为单个知识点构建出题 prompt"""
    desc = node['description']
    testable = desc.get('testable_angles', {})
    confusable = desc.get('confusable_points', '')

    prompt = f"""请根据以下知识点信息，生成3道单选题（每题4个选项，只有1个正确答案）。

知识点名称：{node['name']}
核心概念：{desc['core_concept']}
考察角度：
- 记忆层：{testable.get('memory', '')}
- 理解层：{testable.get('understanding', '')}
- 应用层：{testable.get('application', '')}
易混淆点：{confusable}

要求：
1. 第1题为记忆层（memory），考察基本概念和定义的识记
2. 第2题为理解层（understanding），考察对概念关系和机制的理解
3. 第3题为应用层（application），考察运用知识分析实际案例的能力
4. 每题的4个选项要有区分度，干扰项要合理
5. 正确答案在A/B/C/D中均匀分布，不要都选同一个
6. 解析要详细说明为什么正确答案对、其他选项错

请严格按以下JSON数组格式输出，不要输出任何其他内容（不要输出```json标记）：
[
  {{
    "level": "memory",
    "question": "题目内容",
    "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
    "answer": "A",
    "explanation": "解析内容"
  }},
  {{
    "level": "understanding",
    "question": "题目内容",
    "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
    "answer": "B",
    "explanation": "解析内容"
  }},
  {{
    "level": "application",
    "question": "题目内容",
    "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
    "answer": "C",
    "explanation": "解析内容"
  }}
]"""
    return prompt


def parse_questions(raw_text):
    """从 LLM 返回的文本中解析 JSON"""
    if not raw_text:
        return None
    # 去掉可能的 markdown 代码块标记
    text = raw_text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    if text.endswith('```'):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试找到 JSON 数组
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                return None
    return None


# 生成试题
all_questions = []
question_counter = 1

print(f"共 {len(nodes)} 个知识点，开始生成试题...\n")

for i, node in enumerate(nodes):
    node_id = node['id']
    node_name = node['name']
    print(f"[{i+1}/{len(nodes)}] 正在为 \"{node_name}\" 生成试题...")

    prompt = build_prompt(node)
    raw_response = call_llm(prompt)

    if raw_response:
        questions = parse_questions(raw_response)
        if questions and isinstance(questions, list):
            for q in questions:
                q['id'] = f"q_fin_llm_{question_counter:03d}"
                q['node_id'] = node_id
                all_questions.append(q)
                question_counter += 1
            print(f"  成功生成 {len(questions)} 道题")
        else:
            print(f"  解析失败，原始返回：{raw_response[:200]}")
    else:
        print(f"  API 调用失败")

    # 避免请求过快
    time.sleep(1)

# 保存结果
output_path = Path(__file__).parent / "data" / "questions_course_china_finance_llm.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

# 统计
answer_dist = {}
for q in all_questions:
    ans = q.get('answer', '?')
    answer_dist[ans] = answer_dist.get(ans, 0) + 1

print(f"\n生成完成！共 {len(all_questions)} 道题")
print(f"答案分布：{answer_dist}")
print(f"保存到：{output_path}")
