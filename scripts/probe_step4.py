import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://zkjb.zjmss.org.cn'
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 试几个可能包含报名人手机号的接口
for url in [
    '/api/admin/users?size=3',
    '/api/admin/users/search?keyword=赵梅玲',
    '/api/admin/registrations/20260004',
    '/api/ops/registrations/20260004',
]:
    r = requests.get(BASE + url, headers=h, timeout=10)
    print(f'GET {url}  => {r.status_code}')
    if r.status_code == 200:
        d = r.json()
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str)[:600])
    print()
