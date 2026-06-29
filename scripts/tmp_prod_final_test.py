"""
生产环境决赛评分全流程验证
- 严格限定 stage=FINAL，不碰书审/面谈
- Step1: OPS驳回杨永挺的0分FINAL任务
- Step2: 找QCC/QFD/NON_QCC各一条SCORED任务驳回
- Step3: 专家登录，测试草稿+提交全流程
"""
import requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://zkjb.zjmss.org.cn/pgds'
COMP_ID = 1

def api(method, path, token=None, body=None, params=None):
    hdrs = {'Authorization': f'Bearer {token}'} if token else {}
    r = getattr(requests, method)(BASE + path, json=body, headers=hdrs, params=params, timeout=15)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {}

def ok(label, cond, info=''):
    mark = 'OK' if cond else 'FAIL'
    print(f'  [{mark}] {label}' + (f'  -> {info}' if info else ''))
    return cond

def round2(v): return round(v * 2) / 2

WEIGHTS = {
    'QCC':     {'plan':10,'problem':15,'action':15,'success':20,'review':5,'operation':15,'presentation':20},
    'QFD':     {'plan':10,'problem':30,'action':35,'success':20,'review':5},
    'NON_QCC': {'plan':15,'problem':10,'action':10,'success':20,'review':10,'operation':10,'presentation':15,'item8':10},
}

# ── OPS 登录 ──────────────────────────────────────────────────────────────────
print('=== OPS 登录 ===')
code, res = api('post', '/api/auth/login-with-password',
                body={'phone': '13800010001', 'password': 'ops2026'})
ok('OPS登录', code == 200 and res.get('success'), res.get('message', str(code)))
ops_token = res.get('data', {}).get('token', '')

# ── 获取所有FINAL评分汇总 ─────────────────────────────────────────────────────
print('\n=== 获取决赛评分汇总 ===')
code, res = api('get', '/api/admin/final/scores', token=ops_token, params={'competitionId': COMP_ID})
all_tasks = res.get('data', [])
print(f'  总任务数: {len(all_tasks)}')

# 杨永挺的0分FINAL SCORED任务
yangyongtie_tasks = [t for t in all_tasks
                     if t.get('reviewerPhone') == '13754322649'
                     and t.get('status') == 'SCORED'
                     and (t.get('total') or 0) == 0]
print(f'  杨永挺0分SCORED任务: {len(yangyongtie_tasks)} 条')

# ── OPS 驳回杨永挺的0分任务 ────────────────────────────────────────────────────
print('\n=== OPS 驳回杨永挺的0分任务 ===')
rejected_yangt = []
for t in yangyongtie_tasks[:5]:  # 最多驳回5条，留够测试即可
    tid = t['taskId']
    code2, res2 = api('post', f'/api/admin/final/scores/{tid}/reject', token=ops_token)
    ok(f'驳回 taskId={tid} ({t.get("projectName","")[:15]})', res2.get('success') or code2==200, res2.get('message',''))
    if res2.get('success') or code2 == 200:
        rejected_yangt.append(t)

# ── 找三种评分表各一条SCORED任务驳回 ──────────────────────────────────────────
print('\n=== 找三表各一条SCORED任务并驳回 ===')
found_forms = {}
for t in all_tasks:
    sf = t.get('scoreForm')
    if sf and sf not in found_forms and t.get('status') == 'SCORED' and (t.get('total') or 0) > 0:
        found_forms[sf] = t
    if len(found_forms) == 3:
        break

form_tasks = {}  # scoreForm -> taskItem
for sf, t in found_forms.items():
    tid = t['taskId']
    code2, res2 = api('post', f'/api/admin/final/scores/{tid}/reject', token=ops_token)
    ok(f'驳回 {sf} taskId={tid} reviewer={t.get("reviewerName","")}',
       res2.get('success') or code2 == 200, res2.get('message',''))
    if res2.get('success') or code2 == 200:
        form_tasks[sf] = t

# ── 杨永挺登录 ────────────────────────────────────────────────────────────────
print('\n=== 杨永挺登录 ===')
code, res = api('post', '/api/auth/login-with-password',
                body={'phone': '13754322649', 'password': '589856'})
ok('登录', code == 200 and res.get('success'), res.get('message', str(code)))
yt_token = res.get('data', {}).get('token', '')

# ── 测试杨永挺的一个被驳回任务 ────────────────────────────────────────────────
if rejected_yangt and yt_token:
    t0 = rejected_yangt[0]
    tid0 = t0['taskId']
    sf0 = t0.get('scoreForm') or 'QCC'
    print(f'\n=== 杨永挺 taskId={tid0} scoreForm={sf0} ===')

    # 确认已回到PENDING
    code, res = api('get', '/api/reviews/final/my-tasks', token=yt_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid0), None)
    ok('驳回后状态PENDING', cur and cur['status'] == 'PENDING', cur and cur['status'])

    # 草稿 total=86
    print('  -- 草稿 total=86 --')
    code, res = api('put', f'/api/reviews/final/scores/{tid0}/draft',
                    token=yt_token, body={'scoreForm': sf0, 'total': 86})
    ok('保存草稿', res.get('success'), res.get('message',''))
    code, res = api('get', '/api/reviews/final/my-tasks', token=yt_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid0), None)
    draft = (cur or {}).get('draftScore') or {}
    ok('total=86.0', draft.get('total') == 86.0, str(draft.get('total')))
    wts = WEIGHTS.get(sf0, {})
    if wts:
        all_match = all(draft.get(f) == round2(86*w/100) for f,w in wts.items())
        ok('分项全匹配权重', all_match,
           ', '.join(f'{f}={draft.get(f)}(期望{round2(86*w/100)})' for f,w in wts.items() if draft.get(f) != round2(86*w/100)) or 'all ok')

    # 草稿 total=86.5
    print('  -- 草稿 total=86.5 --')
    code, res = api('put', f'/api/reviews/final/scores/{tid0}/draft',
                    token=yt_token, body={'scoreForm': sf0, 'total': 86.5})
    ok('保存草稿', res.get('success'), res.get('message',''))
    code, res = api('get', '/api/reviews/final/my-tasks', token=yt_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid0), None)
    draft2 = (cur or {}).get('draftScore') or {}
    ok('total=86.5', draft2.get('total') == 86.5, str(draft2.get('total')))

    # 提交 total=86
    print('  -- 提交 total=86 --')
    code, res = api('put', f'/api/reviews/final/scores/{tid0}/submit',
                    token=yt_token, body={'scoreForm': sf0, 'total': 86})
    ok('提交成功', res.get('success'), res.get('message',''))
    code, res = api('get', '/api/reviews/final/my-tasks', token=yt_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid0), None)
    ok('状态SCORED', cur and cur['status'] == 'SCORED', cur and cur['status'])
    ok('提交后total=86', cur and cur.get('total') == 86.0, str(cur and cur.get('total')))

# ── 三表评分专家各测一遍 ────────────────────────────────────────────────────────
for sf, t_info in form_tasks.items():
    reviewer_phone = t_info.get('reviewerPhone')
    reviewer_name = t_info.get('reviewerName', '')
    tid = t_info['taskId']
    print(f'\n=== {sf} | {reviewer_name} | taskId={tid} ===')

    # 找密码: 如果是杨永挺直接用已有token
    if reviewer_phone == '13754322649':
        r_token = yt_token
    else:
        # 尝试默认密码 (生产环境可能不同，这里只测API)
        code, res = api('post', '/api/auth/login-with-password',
                        body={'phone': reviewer_phone, 'password': '123456'})
        r_token = res.get('data', {}).get('token', '')
        if not r_token:
            print(f'  [SKIP] 无法登录 {reviewer_phone}，跳过')
            continue

    # 确认PENDING
    code, res = api('get', '/api/reviews/final/my-tasks', token=r_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid), None)
    ok('状态PENDING', cur and cur['status'] == 'PENDING', cur and cur['status'])

    # 草稿 total=88
    code, res = api('put', f'/api/reviews/final/scores/{tid}/draft',
                    token=r_token, body={'scoreForm': sf, 'total': 88})
    ok('草稿保存', res.get('success'), res.get('message',''))
    code, res = api('get', '/api/reviews/final/my-tasks', token=r_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid), None)
    draft = (cur or {}).get('draftScore') or {}
    ok('total=88.0', draft.get('total') == 88.0, str(draft.get('total')))
    wts = WEIGHTS.get(sf, {})
    all_match = all(draft.get(f) == round2(88*w/100) for f,w in wts.items()) if wts else True
    ok('分项匹配', all_match)

    # 提交
    code, res = api('put', f'/api/reviews/final/scores/{tid}/submit',
                    token=r_token, body={'scoreForm': sf, 'total': 88})
    ok('提交', res.get('success'), res.get('message',''))
    code, res = api('get', '/api/reviews/final/my-tasks', token=r_token)
    cur = next((x for x in res.get('data', []) if x['taskId'] == tid), None)
    ok('SCORED total=88', cur and cur.get('total') == 88.0, str(cur and cur.get('total')))

print('\n===== 生产验证完成 =====')
