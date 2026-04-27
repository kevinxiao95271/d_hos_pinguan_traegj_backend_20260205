import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://zkjb.zjmss.org.cn'
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 把第一条的所有字段名都打出来，看看有没有手机号
resp = requests.get(f'{BASE}/api/admin/registrations/filter',
    params={'competitionId':1,'page':1,'size':5}, headers=h, timeout=30).json()
item = resp['data']['content'][0]
print('列表接口第一条所有字段:')
print(json.dumps(item, ensure_ascii=False, indent=2, default=str))
