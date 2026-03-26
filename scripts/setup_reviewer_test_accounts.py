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
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

# 目标评委 (id, phone, name, label)
targets = [
    (28, '13886509429', '朱研究员', '书审专属评委'),
    (29, '13887790508', '朱研究员', '面谈专属评委'),
    (5,  '13800002569', '孙丽娟',  '书审+面谈双阶段'),
    (27, '13811185687', '刘研究员', '书审+面谈双阶段'),
]

login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = login['data']['token']
print('OPS登录成功\n')

results = []
for uid, phone, name, label in targets:
    resp = post(BASE + f'/api/admin/users/{uid}/reset-password', {}, token)
    if resp and resp.get('data') and resp['data'].get('newPassword'):
        pwd = resp['data']['newPassword']
        results.append({'uid': uid, 'phone': phone, 'name': name, 'label': label, 'password': pwd})
        print(f'✅ id={uid}  {name}  新密码: {pwd}')
    else:
        print(f'❌ id={uid}  {name}  重置失败: {resp}')

print('\n=== 登录验证 + 任务详情 ===\n')
for acc in results:
    resp = post(BASE + '/api/auth/login-with-password', {'phone': acc['phone'], 'password': acc['password']})
    if not (resp and resp.get('data') and resp['data'].get('token')):
        print(f"❌ {acc['phone']} 登录失败")
        continue
    t = resp['data']['token']
    tasks_resp = get(BASE + '/api/reviews/tasks', t)
    tasks = tasks_resp.get('data', []) if tasks_resp else []
    book = [x for x in tasks if x.get('stage') == 'BOOK']
    intv = [x for x in tasks if x.get('stage') == 'INTERVIEW']
    book_s = [x for x in book if x.get('status') == 'SCORED']
    intv_s = [x for x in intv if x.get('status') == 'SCORED']
    print(f"【{acc['label']}】")
    print(f"  账号: {acc['phone']}  姓名: {acc['name']}  密码: {acc['password']}")
    print(f"  书审任务: {len(book)}个 (已评分{len(book_s)}个)  面谈任务: {len(intv)}个 (已评分{len(intv_s)}个)")
    for t2 in book[:3]:
        print(f"    书审 task_id={t2['id']} [{t2['status']}]  项目: {t2.get('projectName','')[:30]}")
    for t2 in intv[:3]:
        print(f"    面谈 task_id={t2['id']} [{t2['status']}]  项目: {t2.get('projectName','')[:30]}")
    print()
