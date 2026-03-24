import json
from pathlib import Path

# 验证线性代数题目文件
file_path = Path(__file__).parent / "data" / "questions_course_linear_algebra.json"

print(f"验证文件: {file_path}")
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"JSON 格式正确，包含 {len(data)} 个题目")
except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")

# 验证线性代数知识图谱文件
file_path = Path(__file__).parent / "data" / "graph_course_linear_algebra.json"

print(f"\n验证文件: {file_path}")
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"JSON 格式正确，包含 {len(data.get('nodes', []))} 个节点")
except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
