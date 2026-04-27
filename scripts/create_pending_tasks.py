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

# 目标评委: 刘研究员 id=27, 孙丽娟 id=5
target_reviewer_id = 27
target_reviewer_name = '刘研究员'
target_phone = '13811185687'
target_pwd = '691659'

# 查目前所有已分配书审任务的 reg_id
book_score_list = get(BASE + '/api/admin/reviews/score-list?competitionId=1&stage=BOOK', ops_token)
scored_reg_ids = set()
if book_score_list and book_score_list.get('data'):
    for item in book_score_list['data']:
        scored_reg_ids.add(item['registrationId'])
print(f'书审已有任务的项目: {len(scored_reg_ids)} 个')

# 查全部已提交报名（SUBMITTED/APPROVED）
regs_resp = get(BASE + '/api/admin/registrations?competitionId=1&status=SUBMITTED&size=200', ops_token)
all_regs = []
if regs_resp and regs_resp.get('data'):
    d = regs_resp['data']
    all_regs = d.get('content', d) if isinstance(d, dict) else d
print(f'已提交报名: {len(all_regs)} 个')

# 找没有书审任务的报名
no_task_regs = [r for r in all_regs if r['id'] not in scored_reg_ids]
print(f'无书审任务的报名: {len(no_task_regs)} 个')

if not no_task_regs:
    print('\n没有空余报名，改为查找只有1个评委的项目...')
    # 找只有1个评委打分的项目，给第二个位置分配
    for item in (book_score_list.get('data') or [])[:10]:
        rv_scores = item.get('reviewerScores', [])
        if len(rv_scores) == 1:
            print(f'  reg_id={item["registrationId"]} 只有1个评委 {rv_scores[0].get("reviewerName")}')

# 找到后手动分配3个给目标评委
to_assign = no_task_regs[:3]
if not to_assign:
    print('\n⚠️  无可分配的报名，请先检查是否有 APPROVED 状态报名')
else:
    print(f'\n准备将 {len(to_assign)} 个报名分配给 {target_reviewer_name}(id={target_reviewer_id})')
    for reg in to_assign:
        reg_id = reg['id']
        # 创建书审任务
        assign_resp = post(BASE + '/api/admin/reviews/assign', {
            'registrationId': reg_id,
            'reviewerId': target_reviewer_id,
            'stage': 'BOOK',
            'competitionId': 1
        }, ops_token)
        if assign_resp and assign_resp.get('code') == 200:
            task_id = assign_resp.get('data', {}).get('id') if isinstance(assign_resp.get('data'), dict) else assign_resp.get('data')
            print(f'  ✅ reg_id={reg_id} [{reg.get("projectName","?")[:25]}] -> task_id={task_id}')
        else:
            print(f'  ❌ reg_id={reg_id} 分配失败: {assign_resp}')

# 验证评委现在的任务
print(f'\n验证 {target_reviewer_name} 当前任务:')
login2 = post(BASE + '/api/auth/login-with-password', {'phone': target_phone, 'password': target_pwd})
if login2 and login2.get('data') and login2['data'].get('token'):
    rv_token = login2['data']['token']
    tasks = get(BASE + '/api/reviews/my-tasks', rv_token)
    tasks_list = tasks.get('data', []) if tasks else []
    book = [t for t in tasks_list if t.get('stage') == 'BOOK']
    pending = [t for t in book if t.get('status') in ('PENDING', 'RETURNED')]
    scored = [t for t in book if t.get('status') == 'SCORED']
    print(f'  书审: 共{len(book)}个 → 已评{len(scored)} / 待评{len(pending)}')
    for t in pending[:5]:
        print(f'    待评 task_id={t["id"]}  {str(t.get("projectName",""))[:30]}')
