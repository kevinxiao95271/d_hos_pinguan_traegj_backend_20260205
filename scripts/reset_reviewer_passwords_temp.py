import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'
NEW_PWD = 'Review2026'

targets = [
    {'phone': '13886509429', 'name': '朱研究员（书审专属）'},
    {'phone': '13887790508', 'name': '朱研究员（面谈专属）'},
    {'phone': '13800002569', 'name': '孙丽娟（书审+面谈）'},
    {'phone': '13811185687', 'name': '刘研究员（书审+面谈）'},
]

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

# 用 ops 账号登录
login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = login['data']['token']
print(f'OPS登录成功\n')

# 查用户列表找 ID
for acc in targets:
    # 用手机号搜索用户
    resp = get(BASE + f'/api/admin/users?phone={acc["phone"]}&size=5', token)
    users = []
    if resp and resp.get('data'):
        d = resp['data']
        users = d.get('content', d) if isinstance(d, dict) else d

    uid = None
    for u in users:
        if u.get('phone') == acc['phone']:
            uid = u['id']
            break

    if not uid:
        print(f"  ❓ {acc['phone']} {acc['name']}  未找到用户ID")
        continue

    # 重置密码
    reset_resp = post(BASE + f'/api/admin/users/{uid}/reset-password',
                      {'newPassword': NEW_PWD}, token)
    if reset_resp and reset_resp.get('code') == 200:
        print(f"  ✅ {acc['phone']}  {acc['name']}  密码已重置为: {NEW_PWD}")
    else:
        print(f"  ❌ {acc['phone']}  {acc['name']}  重置失败: {reset_resp}")

print('\n--- 验证登录 ---')
for acc in targets:
    resp = post(BASE + '/api/auth/login-with-password', {'phone': acc['phone'], 'password': NEW_PWD})
    if resp and resp.get('data') and resp['data'].get('token'):
        t = resp['data']['token']
        tasks_resp = get(BASE + '/api/reviews/tasks', t)
        tasks = tasks_resp.get('data', []) if tasks_resp else []
        book = [x for x in tasks if x.get('stage') == 'BOOK']
        intv = [x for x in tasks if x.get('stage') == 'INTERVIEW']
        book_s = [x for x in book if x.get('status') == 'SCORED']
        intv_s = [x for x in intv if x.get('status') == 'SCORED']
        print(f"  ✅ {acc['phone']}  {acc['name']}  书审{len(book)}个(已评{len(book_s)})  面谈{len(intv)}个(已评{len(intv_s)})")
        for t2 in book[:2]:
            print(f"       书审 task={t2['id']} [{t2['status']}] {t2.get('projectName','')[:25]}")
        for t2 in intv[:2]:
            print(f"       面谈 task={t2['id']} [{t2['status']}] {t2.get('projectName','')[:25]}")
    else:
        print(f"  ❌ {acc['phone']}  登录仍失败")
