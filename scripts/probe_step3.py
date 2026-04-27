import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://zkjb.zjmss.org.cn'
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 看 reg=20260004 的详情结构
detail = requests.get(f'{BASE}/api/registrations/20260004', headers=h, timeout=15).json()
print(json.dumps(detail, ensure_ascii=False, indent=2, default=str))
