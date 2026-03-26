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

login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
ops_token = login['data']['token']
print('OPS登录成功')

# 目标评委: 朱研究员 id=28（书审专属，当前书审只有3条）
# 给他追加 书审 PENDING 任务
# 只有1个评委的reg_ids: [1,4,10,11,12,14,15,17,18,19,...]
# 这些项目目前只有1个评委，给朱研究员(id=28)加第二个

# 同时也给孙丽娟(id=5)加一些面谈 PENDING 任务
# 先看哪些项目面谈只有1个评委

book_score_list = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=BOOK', ops_token)
int_score_list  = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', ops_token)

# 书审：只有1个评委，且那个评委不是朱研究员(28)
book_single = []
for item in (book_score_list.get('data') or []):
    rvs = item.get('reviewerScores', [])
    if len(rvs) == 1 and rvs[0].get('reviewerId') != 28:
        book_single.append(item['registrationId'])

# 面谈：只有1个评委，且那个评委不是朱研究员(28)
int_single = []
for item in (int_score_list.get('data') or []):
    rvs = item.get('reviewerScores', [])
    if len(rvs) == 1 and rvs[0].get('reviewerId') != 28:
        int_single.append(item['registrationId'])

print(f'书审只有1个评委的项目: {len(book_single)} 个')
print(f'面谈只有1个评委的项目: {len(int_single)} 个')

# 给朱研究员(id=28)分配4个书审 PENDING 任务
print('\n=== 给朱研究员(id=28) 分配书审任务 ===')
assigned_book = []
for reg_id in book_single[:4]:
    resp = post(BASE + '/api/admin/reviews/tasks', {
        'registrationId': reg_id,
        'reviewerId': 28,
        'stage': 'BOOK'
    }, ops_token)
    if resp and resp.get('data'):
        task_id = resp['data'].get('id') if isinstance(resp['data'], dict) else resp['data']
        print(f'  ✅ reg_id={reg_id} -> task_id={task_id}')
        assigned_book.append(task_id)
    else:
        print(f'  ❌ reg_id={reg_id} 失败: {resp}')

# 给朱研究员(id=28)分配2个面谈 PENDING 任务
print('\n=== 给朱研究员(id=28) 分配面谈任务 ===')
assigned_int = []
for reg_id in int_single[:2]:
    resp = post(BASE + '/api/admin/reviews/tasks', {
        'registrationId': reg_id,
        'reviewerId': 28,
        'stage': 'INTERVIEW'
    }, ops_token)
    if resp and resp.get('data'):
        task_id = resp['data'].get('id') if isinstance(resp['data'], dict) else resp['data']
        print(f'  ✅ reg_id={reg_id} -> task_id={task_id}')
        assigned_int.append(task_id)
    else:
        print(f'  ❌ reg_id={reg_id} 失败: {resp}')

# 验证朱研究员的任务列表
print('\n=== 验证 朱研究员(13886509429) 当前任务 ===')
login2 = post(BASE + '/api/auth/login-with-password', {'phone': '13886509429', 'password': '238655'})
if login2 and login2.get('data') and login2['data'].get('token'):
    rv_token = login2['data']['token']
    tasks = get(BASE + '/api/reviews/my-tasks', rv_token)
    tasks_list = tasks.get('data', []) if tasks else []
    book = [t for t in tasks_list if t.get('stage') == 'BOOK']
    intv = [t for t in tasks_list if t.get('stage') == 'INTERVIEW']
    book_p = [t for t in book if t.get('status') in ('PENDING','RETURNED')]
    book_s = [t for t in book if t.get('status') == 'SCORED']
    intv_p = [t for t in intv if t.get('status') in ('PENDING','RETURNED')]
    intv_s = [t for t in intv if t.get('status') == 'SCORED']
    print(f'  书审: 共{len(book)}个 → 已评{len(book_s)} / 待评{len(book_p)}')
    print(f'  面谈: 共{len(intv)}个 → 已评{len(intv_s)} / 待评{len(intv_p)}')
    print('\n  待评任务:')
    for t in book_p:
        print(f'    [书审待评] task_id={t["id"]}  {str(t.get("projectName",""))[:35]}')
    for t in intv_p:
        print(f'    [面谈待评] task_id={t["id"]}  {str(t.get("projectName",""))[:35]}')
    print('\n  已评任务(部分):')
    for t in (book_s + intv_s)[:4]:
        print(f'    [{t["stage"]}已评] task_id={t["id"]}  {str(t.get("projectName",""))[:35]}')
