"""测试大模型平台 API 连通性"""
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "https://ai-chat.hep.com.cn/llm/chat/completions"
SYSTEM_TOKEN = "$1$jn7hHZvm$YFRCbYMuJMuNyJ939ylo.1"

headers = {
    "system-token": SYSTEM_TOKEN,
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "modelCode": 12003,
    "stream": False
}

resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
result = resp.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
