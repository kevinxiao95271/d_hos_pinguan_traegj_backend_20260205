"""三表草稿测试 - 本地 6031"""
import requests, pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
          password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

WEIGHTS = {
    'QCC':     {'plan':10,'problem':15,'action':15,'success':20,'review':5,'operation':15,'presentation':20},
    'QFD':     {'plan':10,'problem':30,'action':35,'success':20,'review':5},
    'NON_QCC': {'plan':15,'problem':10,'action':10,'success':20,'review':10,'operation':10,'presentation':15,'item8':10},
}
def round2(v): return round(v * 2) / 2
def ok(label, cond, info=''):
    print(f'    [{"OK" if cond else "FAIL"}] {label}' + (f'  ({info})' if info else ''))

conn = pymysql.connect(**DB)
seen = set()
for form in ['QCC', 'QFD', 'NON_QCC']:
    print(f'\n===== {form} =====')
    cur = conn.cursor()
    cur.execute('''
        SELECT ua.id, ua.phone, rt.id
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        JOIN registrations r ON r.id = rt.registration_id
        WHERE rt.stage='FINAL' AND r.final_score_form=%s AND ua.id NOT IN %s
        LIMIT 1
    ''', (form, tuple(seen) if seen else (0,)))
    row = cur.fetchone()
    if not row:
        print('  无任务跳过'); cur.close(); continue
    uid, phone, tid = row
    seen.add(uid)
    cur.execute('DELETE FROM review_scores WHERE review_task_id=%s', (tid,))
    cur.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('PENDING', tid))
    pwd = 'Local1234'
    h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
    cur.execute('UPDATE user_accounts SET password=%s WHERE id=%s', (h[:2]+'a'+h[3:], uid))
    conn.commit(); cur.close()

    token = requests.post(BASE+'/api/auth/login-with-password',
                          json={'phone': phone, 'password': pwd}, timeout=10).json().get('data',{}).get('token')
    ok('登录', bool(token))
    if not token: continue
    hdrs = {'Authorization': 'Bearer '+token}

    # 案例1：只传total=86
    print('  -- 案例1: 只传 total=86 --')
    r = requests.put(BASE+f'/api/reviews/final/scores/{tid}/draft',
                     headers=hdrs, json={'scoreForm':form,'total':86}, timeout=10)
    ok('草稿保存', r.json().get('success'))
    t = next((x for x in requests.get(BASE+'/api/reviews/final/my-tasks',headers=hdrs,timeout=10).json().get('data',[]) if x['taskId']==tid), None)
    draft = (t or {}).get('draftScore') or {}
    ok('total=86.0', draft.get('total')==86.0, str(draft.get('total')))
    wts = WEIGHTS[form]
    all_ok = all(draft.get(f)==round2(86*w/100) for f,w in wts.items())
    if all_ok:
        print(f'    [OK] 分项全部匹配 ({", ".join(f"{f}={round2(86*w/100)}" for f,w in wts.items())})')
    else:
        for f,w in wts.items():
            ok(f'{f}={round2(86*w/100)}', draft.get(f)==round2(86*w/100), str(draft.get(f)))

    # 案例2：传全部分项
    print('  -- 案例2: 传所有分项 --')
    items = {f: round2(86*w/100) for f,w in wts.items()}
    r2 = requests.put(BASE+f'/api/reviews/final/scores/{tid}/draft',
                      headers=hdrs, json={'scoreForm':form,**items}, timeout=10)
    ok('草稿保存', r2.json().get('success'))
    t2 = next((x for x in requests.get(BASE+'/api/reviews/final/my-tasks',headers=hdrs,timeout=10).json().get('data',[]) if x['taskId']==tid), None)
    exp_sum = sum(items.values())
    ok(f'total={exp_sum}', (t2 or {}).get('draftScore',{}).get('total')==exp_sum, str((t2 or {}).get('draftScore',{}).get('total')))

    # 案例3：提交
    print('  -- 案例3: 提交 total=90 --')
    r3 = requests.put(BASE+f'/api/reviews/final/scores/{tid}/submit',
                      headers=hdrs, json={'scoreForm':form,'total':90}, timeout=10)
    ok('提交成功', r3.json().get('success'), r3.json().get('message',''))
    t3 = next((x for x in requests.get(BASE+'/api/reviews/final/my-tasks',headers=hdrs,timeout=10).json().get('data',[]) if x['taskId']==tid), None)
    ok('状态SCORED', t3 and t3['status']=='SCORED', t3 and t3['status'])
    ok('total=90', t3 and t3.get('total')==90.0, str(t3 and t3.get('total')))

conn.close()
print('\n===== 本地测试完成 =====')
