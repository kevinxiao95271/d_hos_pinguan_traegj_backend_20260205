import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests

API = 'http://localhost:6031'

accounts = [
    {'label': '书审专属评委（单书审）', 'phone': '13886509429', 'password': 'JV30av9G'},
    {'label': '面谈专属评委（单面谈）', 'phone': '13887790508', 'password': 'GYu4DdMr'},
    {'label': '书审+面谈重叠评委',      'phone': '13800002569', 'password': 'qz7WF5N4'},
]

for acc in accounts:
    print(f"\n=== [{acc['label']}] phone={acc['phone']} ===")
    r = requests.post(f"{API}/api/auth/login-with-password", json={
        'phone': acc['phone'],
        'password': acc['password']
    }, timeout=10)
    body = r.json()
    if body.get('code') != 200 and body.get('success') is not True:
        # try data field
        pass
    data = body.get('data') or {}
    print(f"  HTTP {r.status_code}")
    print(f"  noticeConfirmed          : {data.get('noticeConfirmed')}")
    print(f"  pendingIntegrityNoticeKeys: {data.get('pendingIntegrityNoticeKeys')}")
    print(f"  role                     : {data.get('role')}")
    print(f"  name                     : {data.get('name')}")
    if not data:
        print(f"  完整响应: {json.dumps(body, ensure_ascii=False)}")
