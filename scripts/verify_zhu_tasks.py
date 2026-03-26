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
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

# 重新重置密码确保能登录
ops_login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
ops_token = ops_login['data']['token']
reset = post(BASE + '/api/admin/users/28/reset-password', {}, ops_token)
pwd = reset['data']['newPassword']
print(f'朱研究员(id=28) 新密码: {pwd}')

login2 = post(BASE + '/api/auth/login-with-password', {'phone': '13886509429', 'password': pwd})
if not (login2 and login2.get('data') and login2['data'].get('token')):
    print('登录失败')
    exit(1)

rv_token = login2['data']['token']
tasks_resp = get(BASE + '/api/reviews/my-tasks', rv_token)
tasks = tasks_resp.get('data', []) if tasks_resp else []

book = [t for t in tasks if t.get('stage') == 'BOOK']
intv = [t for t in tasks if t.get('stage') == 'INTERVIEW']
book_p = [t for t in book if t.get('status') in ('PENDING','RETURNED')]
book_s = [t for t in book if t.get('status') == 'SCORED']
intv_p = [t for t in intv if t.get('status') in ('PENDING','RETURNED')]
intv_s = [t for t in intv if t.get('status') == 'SCORED']

print(f'\n【朱研究员 - 书审+部分待评测试账号】')
print(f'  手机: 13886509429   密码: {pwd}')
print(f'  书审: 共{len(book)}个 → 已评{len(book_s)} / 待评{len(book_p)}')
print(f'  面谈: 共{len(intv)}个 → 已评{len(intv_s)} / 待评{len(intv_p)}')

if book_p:
    print('\n  书审待评任务:')
    for t in book_p:
        print(f'    task_id={t["id"]:>4}  {str(t.get("projectName",""))[:40]}')
if intv_p:
    print('\n  面谈待评任务:')
    for t in intv_p:
        print(f'    task_id={t["id"]:>4}  {str(t.get("projectName",""))[:40]}')
if book_s:
    print('\n  书审已评任务(前3):')
    for t in book_s[:3]:
        print(f'    task_id={t["id"]:>4}  {str(t.get("projectName",""))[:40]}')
