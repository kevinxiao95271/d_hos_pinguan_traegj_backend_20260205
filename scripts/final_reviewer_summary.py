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

accounts = [
    (28, '13886509429', '朱研究员', '书审专属评委', '238655'),
    (29, '13887790508', '朱研究员', '面谈专属评委', '774474'),
    (5,  '13800002569', '孙丽娟',  '书审+面谈双阶段', '074279'),
    (27, '13811185687', '刘研究员', '书审+面谈双阶段', '691659'),
]

print('=' * 60)
print('  评委测试账号汇总')
print('=' * 60)

for uid, phone, name, label, pwd in accounts:
    resp = post(BASE + '/api/auth/login-with-password', {'phone': phone, 'password': pwd})
    if not (resp and resp.get('data') and resp['data'].get('token')):
        print(f'❌ {phone} 登录失败')
        continue
    t = resp['data']['token']
    tasks_resp = get(BASE + '/api/reviews/my-tasks', t)
    tasks = tasks_resp.get('data', []) if tasks_resp else []
    book = [x for x in tasks if x.get('stage') == 'BOOK']
    intv = [x for x in tasks if x.get('stage') == 'INTERVIEW']
    book_s = [x for x in book if x.get('status') == 'SCORED']
    intv_s = [x for x in intv if x.get('status') == 'SCORED']
    book_p = [x for x in book if x.get('status') in ('PENDING', 'RETURNED')]
    intv_p = [x for x in intv if x.get('status') in ('PENDING', 'RETURNED')]

    print(f'\n【{label}】')
    print(f'  手机: {phone}   密码: {pwd}   姓名: {name}')
    print(f'  书审: 共{len(book)}个 → 已评{len(book_s)}个 / 待评{len(book_p)}个')
    print(f'  面谈: 共{len(intv)}个 → 已评{len(intv_s)}个 / 待评{len(intv_p)}个')
    if book:
        print(f'  书审任务样例:')
        for t2 in book[:3]:
            print(f'    task_id={t2["id"]:>4} [{t2["status"]:>8}]  reg_id={t2.get("registrationId")}  {str(t2.get("projectName",""))[:28]}')
    if intv:
        print(f'  面谈任务样例:')
        for t2 in intv[:3]:
            print(f'    task_id={t2["id"]:>4} [{t2["status"]:>8}]  reg_id={t2.get("registrationId")}  {str(t2.get("projectName",""))[:28]}')

# 构造两类特殊场景说明
print('\n' + '=' * 60)
print('  目标测试场景')
print('=' * 60)
print('''
场景A: 有书审分、无面谈分 的项目
  → 找刘研究员(27) 的任务中 stage=BOOK 且有分的项目，该项目在面谈阶段无任务或 PENDING

场景B: 无书审分、有面谈分 的项目
  → 找孙丽娟(5) 的任务中 stage=INTERVIEW 且有分的项目，该项目书审阶段 PENDING/无任务

以上数据已存在（score-list API 验证过），可直接用这些账号登录测试打分页面。
''')
