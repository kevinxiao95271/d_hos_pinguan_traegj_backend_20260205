import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://zkjb.zjmss.org.cn'

# 登录
r = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10)
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}
print('登录成功')

# 拉前10条报名
resp = requests.get(f'{BASE}/api/admin/registrations/filter',
    params={'competitionId':1,'page':1,'size':10}, headers=h, timeout=30)
data = resp.json().get('data', {})
items = data.get('items') or data.get('content') or []
print(f'totalPages={data.get("totalPages") or data.get("pages")}  totalElements={data.get("totalElements") or data.get("total")}  本页={len(items)}条')
print()
for item in items:
    print(json.dumps(item, ensure_ascii=False, indent=2, default=str))
    print('---')
