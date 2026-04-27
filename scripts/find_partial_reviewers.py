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

# ops 登录
login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
ops_token = login['data']['token']

# 拉评委列表
reviewers_resp = get(BASE + '/api/admin/reviewers', ops_token)
reviewers = reviewers_resp.get('data', []) if reviewers_resp else []
print(f'共 {len(reviewers)} 个评委\n')

# 找有 PENDING/RETURNED 任务的评委（通过 score-list 反推）
# 先拿书审和面谈的 summary（含所有状态任务）
book_sum = get(BASE + '/api/admin/reviews/summary?competitionId=1&stage=BOOK', ops_token)
int_sum  = get(BASE + '/api/admin/reviews/summary?competitionId=1&stage=INTERVIEW', ops_token)

# summary 只有 SCORED，改用 score-list 来分析已评的
# 直接对评委挨个查 my-tasks，找有待评任务的
candidates = []
for rv in reviewers:
    uid = rv['id']
    phone = rv.get('phone', '')
    name = rv.get('name', '')
    if not phone:
        continue

    # 用 ops 重置密码
    reset = post(BASE + f'/api/admin/users/{uid}/reset-password', {}, ops_token)
    if not (reset and reset.get('data') and reset['data'].get('newPassword')):
        continue
    pwd = reset['data']['newPassword']

    # 登录
    login2 = post(BASE + '/api/auth/login-with-password', {'phone': phone, 'password': pwd})
    if not (login2 and login2.get('data') and login2['data'].get('token')):
        continue
    rv_token = login2['data']['token']

    tasks_resp = get(BASE + '/api/reviews/my-tasks', rv_token)
    tasks = tasks_resp.get('data', []) if tasks_resp else []
    if not tasks:
        continue

    book = [t for t in tasks if t.get('stage') == 'BOOK']
    intv = [t for t in tasks if t.get('stage') == 'INTERVIEW']
    book_s = [t for t in book if t.get('status') == 'SCORED']
    intv_s = [t for t in intv if t.get('status') == 'SCORED']
    book_p = [t for t in book if t.get('status') in ('PENDING', 'RETURNED')]
    intv_p = [t for t in intv if t.get('status') in ('PENDING', 'RETURNED')]

    has_pending = len(book_p) > 0 or len(intv_p) > 0
    if has_pending:
        candidates.append({
            'uid': uid, 'phone': phone, 'name': name, 'password': pwd,
            'book_total': len(book), 'book_scored': len(book_s), 'book_pending': len(book_p),
            'intv_total': len(intv), 'intv_scored': len(intv_s), 'intv_pending': len(intv_p),
            'book_pending_tasks': book_p[:2],
            'intv_pending_tasks': intv_p[:2],
        })
        print(f'  找到: id={uid} {name} {phone}  书审待评{len(book_p)} 面谈待评{len(intv_p)}')

    if len(candidates) >= 5:
        break

print(f'\n共找到 {len(candidates)} 个有待评任务的评委\n')
print('=' * 60)
for c in candidates:
    print(f"\n【{c['name']}】  手机: {c['phone']}  密码: {c['password']}")
    print(f"  书审: 共{c['book_total']}个 → 已评{c['book_scored']} / 待评{c['book_pending']}")
    print(f"  面谈: 共{c['intv_total']}个 → 已评{c['intv_scored']} / 待评{c['intv_pending']}")
    for t in c['book_pending_tasks']:
        print(f"    书审待评 task_id={t['id']} reg_id={t.get('registrationId')} {str(t.get('projectName',''))[:30]}")
    for t in c['intv_pending_tasks']:
        print(f"    面谈待评 task_id={t['id']} reg_id={t.get('registrationId')} {str(t.get('projectName',''))[:30]}")
