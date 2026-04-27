import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = login['data']['token']

# 试不同的用户查询路径
for url in [
    '/api/admin/users?size=3',
    '/api/ops/users?size=3',
    '/api/admin/reviewers?size=3',
]:
    resp = get(BASE + url, token)
    if resp:
        print(f'{url} -> code={resp.get("code")} data_type={type(resp.get("data")).__name__}')
        d = resp.get('data')
        if isinstance(d, dict):
            print(f'  keys: {list(d.keys())}')
            items = d.get('content', [])
            for item in items[:2]:
                print(f'  -> id={item.get("id")} phone={item.get("phone")} name={item.get("name")}')
        elif isinstance(d, list):
            for item in d[:2]:
                print(f'  -> id={item.get("id")} phone={item.get("phone")} name={item.get("name")}')
    else:
        print(f'{url} -> 无响应/404')

# 直接用 ID reset password (id=5 孙丽娟)
print('\n尝试直接用ID重置密码 (id=5):')
resp = post(BASE + '/api/admin/users/5/reset-password', {'newPassword': 'Review2026'}, token)
print(f'  结果: {resp}')

resp2 = post(BASE + '/api/ops/users/5/reset-password', {'newPassword': 'Review2026'}, token)
print(f'  ops路径: {resp2}')
