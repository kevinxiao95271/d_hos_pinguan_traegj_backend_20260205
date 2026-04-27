import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'

accounts = [
    {'phone': '13886509429', 'password': 'JV30av9G', 'label': '书审专属评委（单书审任务）', 'name': '朱研究员'},
    {'phone': '13887790508', 'password': 'GYu4DdMr', 'label': '面谈专属评委（单面谈任务）', 'name': '朱研究员'},
    {'phone': '13800002569', 'password': 'qz7WF5N4', 'label': '书审+面谈重叠评委（多任务）', 'name': '孙丽娟'},
    {'phone': '13811185687', 'password': None, 'label': '书审+面谈都有得分', 'name': '刘研究员'},
]

def post(url, data):
    req = urllib.request.Request(url, json.dumps(data).encode(), {'Content-Type': 'application/json'})
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

print("=== 评委账号验证 ===\n")
for acc in accounts:
    if not acc['password']:
        print(f"  {acc['phone']}  {acc['name']}  密码未知，跳过")
        continue
    resp = post(BASE + '/api/auth/login-with-password', {'phone': acc['phone'], 'password': acc['password']})
    if resp and resp.get('data') and resp['data'].get('token'):
        token = resp['data']['token']
        # 查该评委的任务
        tasks_resp = get(BASE + '/api/reviews/tasks', token)
        tasks = tasks_resp.get('data', []) if tasks_resp else []
        book_tasks = [t for t in tasks if t.get('stage') == 'BOOK']
        int_tasks = [t for t in tasks if t.get('stage') == 'INTERVIEW']
        book_scored = [t for t in book_tasks if t.get('status') == 'SCORED']
        int_scored = [t for t in int_tasks if t.get('status') == 'SCORED']
        print(f"  ✅ {acc['phone']}  {acc['name']}  [{acc['label']}]")
        print(f"     密码: {acc['password']}")
        print(f"     书审任务: {len(book_tasks)}个 (已评{len(book_scored)})  面谈任务: {len(int_tasks)}个 (已评{len(int_scored)})")
        if book_tasks:
            for t in book_tasks[:3]:
                print(f"       书审 task_id={t['id']}  reg_id={t.get('registrationId')}  状态={t['status']}  项目={t.get('projectName','?')[:20]}")
        if int_tasks:
            for t in int_tasks[:3]:
                print(f"       面谈 task_id={t['id']}  reg_id={t.get('registrationId')}  状态={t['status']}  项目={t.get('projectName','?')[:20]}")
        print()
    else:
        print(f"  ❌ {acc['phone']}  {acc['name']}  登录失败（密码可能已更改）")
        print()
