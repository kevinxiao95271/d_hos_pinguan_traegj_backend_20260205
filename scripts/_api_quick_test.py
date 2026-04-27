import sys, io, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = 'http://localhost:6031'

accounts = [
    ('书审专属（单书审，无面谈组）', '13886509429', 'JV30av9G'),
    ('面谈专属（单面谈）',           '13887790508', 'GYu4DdMr'),
    ('书审+面谈重叠评委',            '13800002569', 'qz7WF5N4'),
]

for label, phone, pwd in accounts:
    print(f'\n=== [{label}] ===')
    try:
        r = requests.post(f'{API}/api/auth/login-with-password',
            json={'phone': phone, 'password': pwd}, timeout=30)
        print(f'  HTTP {r.status_code}')
        body = r.json()
        print(f'  完整响应: {json.dumps(body, ensure_ascii=False, indent=2)[:800]}')
    except Exception as e:
        print(f'  ERROR: {e}')
