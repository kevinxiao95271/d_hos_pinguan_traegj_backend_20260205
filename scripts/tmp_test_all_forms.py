"""
测试三种表单(QCC/QFD/NON_QCC)草稿存取：
  - 只传 total，验证 total 与各分项读回一致
  - 再传全部分项，验证 total = sum(分项)
"""
import requests, pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://81.71.44.180:6039'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
          password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

# 权重配置（与后端 distributeIfItemsMissing 对齐）
WEIGHTS = {
    'QCC':     {'plan':10,'problem':15,'action':15,'success':20,'review':5,'operation':15,'presentation':20},
    'QFD':     {'plan':10,'problem':30,'action':35,'success':20,'review':5},
    'NON_QCC': {'plan':15,'problem':10,'action':10,'success':20,'review':10,'operation':10,'presentation':15,'item8':10},
}

def round2(v): return round(v * 2) / 2

def ok(label, cond, info=''):
    mark = 'OK' if cond else 'FAIL'
    print(f'    [{mark}] {label}' + (f'  ({info})' if info else ''))
    return cond

conn = pymysql.connect(**DB)

for form in ['QCC', 'QFD', 'NON_QCC']:
    print(f'\n===== {form} =====')
    cur = conn.cursor()
    cur.execute('''
        SELECT rt.id, ua.id, ua.phone
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        JOIN registrations r ON r.id = rt.registration_id
        WHERE rt.stage = %s AND r.final_score_form = %s
        LIMIT 1
    ''', ('FINAL', form))
    row = cur.fetchone()
    if not row:
        print(f'  无 {form} 任务，跳过')
        cur.close()
        continue
    task_id, uid, phone = row

    # 重置
    cur.execute('DELETE FROM review_scores WHERE review_task_id=%s', (task_id,))
    cur.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('PENDING', task_id))
    pwd = 'pass1234'
    h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
    h2a = h[:2] + 'a' + h[3:]
    cur.execute('UPDATE user_accounts SET password=%s WHERE id=%s', (h2a, uid))
    conn.commit(); cur.close()

    print(f'  task_id={task_id}  uid={uid}  phone={phone}')

    # 登录
    token = requests.post(BASE+'/api/auth/login-with-password',
                          json={'phone': phone, 'password': pwd}, timeout=10).json().get('data', {}).get('token')
    ok('登录', bool(token))
    if not token:
        continue
    hdrs = {'Authorization': 'Bearer ' + token}

    # ── 案例1：只传 total=86 ──────────────────────────────────────────────
    print(f'  -- 案例1: 只传 total=86 --')
    r = requests.put(BASE+f'/api/reviews/final/scores/{task_id}/draft',
                     headers=hdrs, json={'scoreForm': form, 'total': 86}, timeout=10)
    ok('草稿保存', r.json().get('success'), r.json().get('message',''))

    tasks = requests.get(BASE+'/api/reviews/final/my-tasks', headers=hdrs, timeout=10).json().get('data', [])
    t = next((x for x in tasks if x['taskId'] == task_id), None)
    draft = (t or {}).get('draftScore') or {}
    total_back = draft.get('total')
    ok('total=86.0', total_back == 86.0, str(total_back))

    # 验证分项 = round(86 * weight/100)
    wts = WEIGHTS[form]
    all_ok = True
    for field, w in wts.items():
        expected = round2(86 * w / 100)
        actual = draft.get(field)
        if actual != expected:
            ok(f'{field}={expected}', False, f'got {actual}')
            all_ok = False
    if all_ok:
        print(f'    [OK] 所有分项匹配权重 ({", ".join(f"{f}={round2(86*w/100)}" for f,w in wts.items())})')

    # ── 案例2：传全部分项（不传total，验证后端自己求和）─────────────────────
    print(f'  -- 案例2: 传所有分项（各取整数，验证total=sum）--')
    item_vals = {f: round2(86 * w / 100) for f, w in wts.items()}
    payload = {'scoreForm': form, **item_vals}
    r2 = requests.put(BASE+f'/api/reviews/final/scores/{task_id}/draft',
                      headers=hdrs, json=payload, timeout=10)
    ok('草稿保存', r2.json().get('success'), r2.json().get('message',''))

    tasks2 = requests.get(BASE+'/api/reviews/final/my-tasks', headers=hdrs, timeout=10).json().get('data', [])
    t2 = next((x for x in tasks2 if x['taskId'] == task_id), None)
    draft2 = (t2 or {}).get('draftScore') or {}
    expected_sum = sum(item_vals.values())
    total_back2 = draft2.get('total')
    ok(f'total={expected_sum}', total_back2 == expected_sum, str(total_back2))

    # ── 案例3：提交打分（只传total=90）──────────────────────────────────────
    print(f'  -- 案例3: 提交 total=90 --')
    r3 = requests.put(BASE+f'/api/reviews/final/scores/{task_id}/submit',
                      headers=hdrs, json={'scoreForm': form, 'total': 90}, timeout=10)
    ok('提交成功', r3.json().get('success'), r3.json().get('message',''))
    tasks3 = requests.get(BASE+'/api/reviews/final/my-tasks', headers=hdrs, timeout=10).json().get('data', [])
    t3 = next((x for x in tasks3 if x['taskId'] == task_id), None)
    ok('状态SCORED', t3 and t3['status'] == 'SCORED', t3 and t3['status'])
    ok('total=90', t3 and t3.get('total') == 90.0, str(t3 and t3.get('total')))

conn.close()
print('\n===== 全部测试完成 =====')
