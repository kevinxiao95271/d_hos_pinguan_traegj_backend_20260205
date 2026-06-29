"""
决赛评分完整流程测试：
1. 专家登录 → 获取任务
2. 保存草稿（只传total）→ 验证分项被正确拆分
3. 提交评分 → 验证SCORED
4. OPS驳回 → 验证回到PENDING/DRAFT
5. 专家重新提交 → 验证SCORED
"""
import requests, json, pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://81.71.44.180:6039'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

def ok(label, cond, info=''):
    mark = 'OK' if cond else 'FAIL'
    print(f'  [{mark}] {label}' + (f'  ({info})' if info else ''))
    return cond

def api(method, path, token=None, body=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    r = getattr(requests, method)(BASE + path, json=body, headers=headers, timeout=10)
    return r.status_code, r.json()

# ── 找一个有FINAL任务的测试专家 ────────────────────────────────────────────
conn = pymysql.connect(**DB); cur = conn.cursor()
cur.execute('''
    SELECT ua.id, ua.name, ua.phone, rt.id as task_id, r.final_session_code
    FROM review_tasks rt
    JOIN user_accounts ua ON ua.id = rt.reviewer_id
    JOIN registrations r ON r.id = rt.registration_id
    WHERE rt.stage = %s AND rt.status = %s
    LIMIT 1
''', ('FINAL', 'PENDING'))
row = cur.fetchone()
if not row:
    print('测试库无PENDING的FINAL任务，先重置一条')
    cur.execute('SELECT id FROM review_tasks WHERE stage=%s LIMIT 1', ('FINAL',))
    tid = cur.fetchone()[0]
    cur.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('PENDING', tid))
    conn.commit()
    cur.execute('''
        SELECT ua.id, ua.name, ua.phone, rt.id, r.final_session_code
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        JOIN registrations r ON r.id = rt.registration_id
        WHERE rt.id = %s
    ''', (tid,))
    row = cur.fetchone()

reviewer_id, reviewer_name, reviewer_phone, task_id, session_code = row
print(f'测试专家: {reviewer_name}({reviewer_phone})  taskId={task_id}  专场={session_code}')

# 重置密码为 test123 的bcrypt hash（$2a$）
import bcrypt
pwd = 'test123'
h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
h2a = h[:2] + 'a' + h[3:]
cur.execute('UPDATE user_accounts SET password=%s WHERE id=%s', (h2a, reviewer_id))
# 确保任务PENDING
cur.execute('DELETE FROM review_scores WHERE review_task_id=%s', (task_id,))
cur.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('PENDING', task_id))
conn.commit()
cur.close(); conn.close()
print(f'密码重置为: {pwd}\n')

# ── Step 1: 专家登录 ──────────────────────────────────────────────────────
print('=== Step 1: 专家登录 ===')
code, res = api('post', '/api/auth/login-with-password',
                body={'phone': reviewer_phone, 'password': pwd})
ok('登录成功', code == 200 and res.get('success'), res.get('message',''))
token = res.get('data', {}).get('token')

# ── Step 2: 获取任务，确认PENDING ────────────────────────────────────────
print('\n=== Step 2: 获取任务 ===')
code, res = api('get', '/api/reviews/final/my-tasks', token=token)
tasks = res.get('data', [])
t = next((x for x in tasks if x['taskId'] == task_id), None)
ok('任务存在', t is not None)
ok('初始状态PENDING', t and t['status'] == 'PENDING', t and t['status'])
score_form = (t or {}).get('scoreForm') or 'QCC'
print(f'  scoreForm={score_form}')

# ── Step 3: 保存草稿（只传total） ─────────────────────────────────────────
print('\n=== Step 3: 保存草稿 (total=86) ===')
code, res = api('put', f'/api/reviews/final/scores/{task_id}/draft',
                token=token, body={'scoreForm': score_form, 'total': 86})
ok('草稿保存成功', res.get('success'), res.get('message',''))

# 重新拉取验证分项
code, res = api('get', '/api/reviews/final/my-tasks', token=token)
t2 = next((x for x in res.get('data', []) if x['taskId'] == task_id), None)
draft = (t2 or {}).get('draftScore') or {}
ok('状态变DRAFT', t2 and t2['status'] == 'DRAFT', t2 and t2['status'])
ok('total=86存储正确', draft.get('total') == 86.0, str(draft.get('total')))
ok('plan分项已拆分(非null)', draft.get('plan') is not None, str(draft.get('plan')))
print(f'  分项: plan={draft.get("plan")} problem={draft.get("problem")} action={draft.get("action")}')
print(f'        success={draft.get("success")} review={draft.get("review")} operation={draft.get("operation")} presentation={draft.get("presentation")}')

# ── Step 4: 提交评分 ─────────────────────────────────────────────────────
print('\n=== Step 4: 提交评分 ===')
code, res = api('put', f'/api/reviews/final/scores/{task_id}/submit',
                token=token, body={'scoreForm': score_form, 'total': 86})
ok('提交成功', res.get('success'), res.get('message',''))

code, res = api('get', '/api/reviews/final/my-tasks', token=token)
t3 = next((x for x in res.get('data', []) if x['taskId'] == task_id), None)
ok('状态变SCORED', t3 and t3['status'] == 'SCORED', t3 and t3['status'])
ok('total=86', t3 and t3.get('total') == 86.0, str(t3 and t3.get('total')))

# ── Step 5: OPS驳回 ──────────────────────────────────────────────────────
print('\n=== Step 5: OPS驳回（直接改DB模拟）===')
conn2 = pymysql.connect(**DB); cur2 = conn2.cursor()
cur2.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('RETURNED', task_id))
conn2.commit(); cur2.close(); conn2.close()

code, res = api('get', '/api/reviews/final/my-tasks', token=token)
t4 = next((x for x in res.get('data', []) if x['taskId'] == task_id), None)
ok('驳回后状态RETURNED', t4 and t4['status'] == 'RETURNED', t4 and t4['status'])

# ── Step 6: 重新提交 ─────────────────────────────────────────────────────
print('\n=== Step 6: 重新提交 ===')
code, res = api('put', f'/api/reviews/final/scores/{task_id}/submit',
                token=token, body={'scoreForm': score_form, 'total': 90})
ok('重新提交成功', res.get('success'), res.get('message',''))

code, res = api('get', '/api/reviews/final/my-tasks', token=token)
t5 = next((x for x in res.get('data', []) if x['taskId'] == task_id), None)
ok('状态重回SCORED', t5 and t5['status'] == 'SCORED', t5 and t5['status'])
ok('total更新为90', t5 and t5.get('total') == 90.0, str(t5 and t5.get('total')))

print('\n=== 全流程测试完成 ===')
