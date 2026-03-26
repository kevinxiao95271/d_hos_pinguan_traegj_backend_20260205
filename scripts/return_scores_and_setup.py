import sys, json, time
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
        return {'error': str(e)}

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

# 等服务就绪
for i in range(5):
    resp = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
    if resp and resp.get('data') and resp['data'].get('token'):
        ops_token = resp['data']['token']
        print('OPS登录成功')
        break
    print(f'  第{i+1}次连接失败，重试...')
    time.sleep(3)
else:
    print('服务连接失败')
    sys.exit(1)

# ─── 1. 驳回多个书审得分 ───────────────────────────────────────
score_list = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=BOOK', ops_token)
items = score_list.get('data', []) if score_list else []

to_return_book = []
seen_reviewers = set()
for item in items:
    for rs in item.get('reviewerScores', []):
        rv_id = rs.get('reviewerId')
        task_id = rs.get('reviewTaskId')
        if rv_id and task_id and rv_id not in seen_reviewers and rv_id not in (27, 5, 28):
            to_return_book.append({
                'taskId': task_id, 'reviewerId': rv_id,
                'reviewerName': rs.get('reviewerName','?'),
                'regId': item['registrationId'],
                'project': item.get('projectName','')[:30]
            })
            seen_reviewers.add(rv_id)
        if len(to_return_book) >= 5:
            break
    if len(to_return_book) >= 5:
        break

# 面谈再找2个
int_score_list = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', ops_token)
int_items = int_score_list.get('data', []) if int_score_list else []
to_return_int = []
for item in int_items:
    for rs in item.get('reviewerScores', []):
        rv_id = rs.get('reviewerId')
        task_id = rs.get('reviewTaskId')
        if rv_id and task_id and rv_id not in seen_reviewers:
            to_return_int.append({
                'taskId': task_id, 'reviewerId': rv_id,
                'reviewerName': rs.get('reviewerName','?'),
                'regId': item['registrationId'],
                'project': item.get('projectName','')[:30]
            })
            seen_reviewers.add(rv_id)
        if len(to_return_int) >= 2:
            break
    if len(to_return_int) >= 2:
        break

print('\n' + '=' * 62)
print('  书审驳回  POST /api/admin/reviews/scores/return')
print('=' * 62)
for t in to_return_book:
    body = {'reviewTaskId': t['taskId']}
    resp = post(BASE + '/api/admin/reviews/scores/return', body, ops_token)
    ok = resp and isinstance(resp.get('data'), dict) and resp['data'].get('status') == 'RETURNED'
    status_str = f'✅ 驳回成功 → status={resp["data"]["status"]}' if ok else f'❌ {resp}'
    print(f'\n  POST /api/admin/reviews/scores/return')
    print(f'  Body : {json.dumps(body)}')
    print(f'  任务 : task_id={t["taskId"]}  评委={t["reviewerName"]}(id={t["reviewerId"]})')
    print(f'  项目 : reg_id={t["regId"]}  {t["project"]}')
    print(f'  结果 : {status_str}')

print('\n' + '=' * 62)
print('  面谈驳回  POST /api/admin/reviews/interview-scores/return')
print('=' * 62)
for t in to_return_int:
    url = BASE + f'/api/admin/reviews/interview-scores/return?reviewTaskId={t["taskId"]}'
    resp = post(url, {}, ops_token)
    ok = resp and resp.get('code') == 200
    status_str = '✅ 驳回成功' if ok else f'❌ {resp}'
    print(f'\n  POST /api/admin/reviews/interview-scores/return?reviewTaskId={t["taskId"]}')
    print(f'  任务 : task_id={t["taskId"]}  评委={t["reviewerName"]}(id={t["reviewerId"]})')
    print(f'  项目 : reg_id={t["regId"]}  {t["project"]}')
    print(f'  结果 : {status_str}')

# ─── 2. 给这些评委重置密码、展示账号 ────────────────────────────
print('\n' + '=' * 62)
print('  被驳回评委登录账号')
print('=' * 62)
reviewers_resp = get(BASE + '/api/admin/reviewers', ops_token)
reviewers = reviewers_resp.get('data', []) if reviewers_resp else []
rv_phone_map = {r['id']: r.get('phone','?') for r in reviewers}

all_returned = to_return_book + to_return_int
shown = {}
for t in all_returned:
    rv_id = t['reviewerId']
    if rv_id in shown:
        continue
    reset = post(BASE + f'/api/admin/users/{rv_id}/reset-password', {}, ops_token)
    if not (reset and reset.get('data') and reset['data'].get('newPassword')):
        print(f'  ❌ id={rv_id} 重置密码失败')
        continue
    pwd = reset['data']['newPassword']
    phone = rv_phone_map.get(rv_id, '?')
    shown[rv_id] = True

    login2 = post(BASE + '/api/auth/login-with-password', {'phone': phone, 'password': pwd})
    if not (login2 and login2.get('data') and login2['data'].get('token')):
        print(f'  ❌ {phone} 登录失败')
        continue
    rv_token = login2['data']['token']
    tasks_resp = get(BASE + '/api/reviews/my-tasks', rv_token)
    tasks = tasks_resp.get('data', []) if tasks_resp else []
    book = [x for x in tasks if x.get('stage') == 'BOOK']
    intv = [x for x in tasks if x.get('stage') == 'INTERVIEW']
    bp = [x for x in book if x.get('status') in ('PENDING','RETURNED')]
    bs = [x for x in book if x.get('status') == 'SCORED']
    ip = [x for x in intv if x.get('status') in ('PENDING','RETURNED')]
    is_ = [x for x in intv if x.get('status') == 'SCORED']
    print(f'\n  姓名={t["reviewerName"]}  手机={phone}  密码={pwd}')
    print(f'  书审: 共{len(book)}个 → 已评{len(bs)} / 待评or驳回{len(bp)}')
    print(f'  面谈: 共{len(intv)}个 → 已评{len(is_)} / 待评or驳回{len(ip)}')
    for tk in bp[:3]:
        print(f'    [书审-{tk["status"]}] task_id={tk["id"]}  {str(tk.get("projectName",""))[:35]}')
    for tk in ip[:3]:
        print(f'    [面谈-{tk["status"]}] task_id={tk["id"]}  {str(tk.get("projectName",""))[:35]}')
