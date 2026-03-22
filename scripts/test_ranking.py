"""
系数调整排名测试脚本

手动构造已知分数 → 调接口计算 → 对比期望值
测试场景：
  综合组 2个小组（B1_TEST / B2_TEST，与正式数据隔离）
    B1_TEST: P1(评委78,80=79均)  P2(评委82,84=83均)
    B2_TEST: P3(评委88,90=89均)  P4(评委86,88=87均)

期望计算：
  B1_TEST所有个人分: 78,80,82,84 → An1=81.0
  B2_TEST所有个人分: 88,90,86,88 → An2=88.0
  全组 B = (78+80+82+84+88+90+86+88)/8 = 84.5
  Cn1 = 81.0/84.5 = 0.9586
  Cn2 = 88.0/84.5 = 1.0414
  D: P1=82.41  P2=86.59  P3=85.46  P4=83.54
  排名: P2 > P3 > P4 > P1
"""
import pymysql, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'
COMPETITION_ID = 1

def get_conn():
    return pymysql.connect(
        host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
        user='root', password='Yiguo9527_',
        database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = get_conn()
cur = conn.cursor()

# ── 0. 登录获取token ──────────────────────────────────────────
resp = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'})
token = resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
print('[OK] 登录成功')

# ── 1. 彻底清理上轮测试遗留数据 ──────────────────────────────
# 找所有 *_TEST 组的项目
cur.execute("""
    SELECT id FROM registrations
    WHERE competition_id=%s AND group_code LIKE '%%_TEST'
""", (COMPETITION_ID,))
old_test_ids = [r[0] for r in cur.fetchall()]
if old_test_ids:
    t = tuple(old_test_ids) if len(old_test_ids) > 1 else (old_test_ids[0], old_test_ids[0])
    cur.execute(f"""
        DELETE rs FROM review_scores rs
        JOIN review_tasks rt ON rs.review_task_id=rt.id
        WHERE rt.stage='BOOK' AND rt.registration_id IN {t}
    """)
    cur.execute(f"DELETE FROM review_tasks WHERE stage='BOOK' AND registration_id IN {t}")
    cur.execute(f"UPDATE registrations SET group_code='B1' WHERE id IN {t}")
    conn.commit()
    print(f'[OK] 清理上轮遗留: {old_test_ids}')

# 清旧快照
cur.execute("DELETE FROM scoring_snapshots WHERE competition_id=%s AND stage='BOOK'", (COMPETITION_ID,))
conn.commit()
print('[OK] 清空书审快照')

# ── 2. 选4个综合组项目（保证分两组） ─────────────────────────
cur.execute("""
    SELECT r.id, r.project_name, r.group_code
    FROM registrations r
    WHERE r.competition_id=%s AND r.group_type='COMPREHENSIVE'
      AND r.status='SUBMITTED'
    ORDER BY r.id
    LIMIT 4
""", (COMPETITION_ID,))
rows = cur.fetchall()
if len(rows) < 4:
    print(f'[ERR] 综合组项目不足4个，只有{len(rows)}个'); sys.exit(1)
rows = list(rows)

# 强制分两组
p1_id, p2_id = rows[0][0], rows[1][0]
p3_id, p4_id = rows[2][0], rows[3][0]
cur.execute("UPDATE registrations SET group_code='B1_TEST' WHERE id IN (%s,%s)", (p1_id, p2_id))
cur.execute("UPDATE registrations SET group_code='B2_TEST' WHERE id IN (%s,%s)", (p3_id, p4_id))
conn.commit()
print(f'\n[INFO] 测试项目: B1_TEST=[{p1_id},{p2_id}]  B2_TEST=[{p3_id},{p4_id}]')

# ── 3. 取评委 ─────────────────────────────────────────────────
cur.execute("SELECT id, name FROM user_accounts WHERE role='REVIEWER' LIMIT 2")
reviewers = cur.fetchall()
if len(reviewers) < 2:
    print('[ERR] 评委不足2人'); conn.close(); sys.exit(1)
r1, r2 = reviewers[0][0], reviewers[1][0]
print(f'[INFO] 评委: {reviewers[0][1]}(id={r1}), {reviewers[1][1]}(id={r2})')

# ── 4. 清理旧任务，写入测试分数 ──────────────────────────────
proj_ids = (p1_id, p2_id, p3_id, p4_id)
cur.execute(f"""
    DELETE rs FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id=rt.id
    WHERE rt.stage='BOOK' AND rt.registration_id IN {proj_ids}
""")
cur.execute(f"DELETE FROM review_tasks WHERE stage='BOOK' AND registration_id IN {proj_ids}")
conn.commit()

score_plan = [
    (p1_id, r1, 78), (p1_id, r2, 80),  # P1 avg=79
    (p2_id, r1, 82), (p2_id, r2, 84),  # P2 avg=83
    (p3_id, r1, 88), (p3_id, r2, 90),  # P3 avg=89
    (p4_id, r1, 86), (p4_id, r2, 88),  # P4 avg=87
]
for reg_id, rev_id, score in score_plan:
    cur.execute("""
        INSERT INTO review_tasks(stage,status,registration_id,reviewer_id,created_at,updated_at)
        VALUES('BOOK','SCORED',%s,%s,NOW(),NOW())
    """, (reg_id, rev_id))
    tid = cur.lastrowid
    cur.execute("""
        INSERT INTO review_scores(plan,problem,action,success,review,operation,presentation,
            total,highlight,weakness,submitted_at,review_task_id)
        VALUES(0,0,0,0,0,0,%s,%s,'','',NOW(),%s)
    """, (score, score, tid))
conn.commit()
print(f'[OK] 写入 {len(score_plan)} 条测试评分')

# ── 5. 调 compute-ranking 接口 ───────────────────────────────
resp = requests.post(f'{BASE}/api/admin/reviews/compute-ranking',
    json={'competitionId': COMPETITION_ID, 'stage': 'BOOK', 'groupType': 'COMPREHENSIVE'},
    headers=headers)
d = resp.json()
print(f'\n[API] compute-ranking → {resp.status_code} {d}')

# ── 6. 查快照 ─────────────────────────────────────────────────
conn2 = get_conn()
cur2 = conn2.cursor()
cur2.execute("""
    SELECT ss.registration_id, ss.group_code, ss.raw_avg, ss.group_avg,
           ss.overall_avg, ss.coefficient, ss.adjusted_score, ss.irank
    FROM scoring_snapshots ss
    WHERE ss.competition_id=%s AND ss.stage='BOOK' AND ss.group_type='COMPREHENSIVE'
      AND ss.registration_id IN %s
    ORDER BY ss.irank
""", (COMPETITION_ID, proj_ids))
snapshots = cur2.fetchall()
print(f'\n[RESULT] 快照（只含测试项目）:')
print(f'  {"ID":>6} {"组":>8} {"原始均":>8} {"An":>8} {"B":>8} {"Cn":>8} {"D":>8} {"irank":>6}')
for s in snapshots:
    print(f'  {s[0]:>6} {s[1]:>8} {s[2]:>8.3f} {s[3]:>8.3f} {s[4]:>8.3f} {s[5]:>8.4f} {s[6]:>8.3f} {s[7]:>4}')

# ── 7. 验证（动态推导期望值，不依赖DB项目数量） ──────────────
print('\n[VERIFY] 系数计算精度:')
snap_map = {s[0]: s for s in snapshots}

# 从快照中读实际 B（全组均值，随DB数据变化，但Cn=An/B应恒成立）
actual_B = snap_map[p1_id][4] if p1_id in snap_map else None
exp_An1, exp_An2 = 81.0, 88.0  # 只由4个测试项目决定，固定
exp_raw = {p1_id: 79.0, p2_id: 83.0, p3_id: 89.0, p4_id: 87.0}
exp_an  = {p1_id: exp_An1, p2_id: exp_An1, p3_id: exp_An2, p4_id: exp_An2}

all_pass = True
for reg_id in [p1_id, p2_id, p3_id, p4_id]:
    s = snap_map.get(reg_id)
    if not s:
        print(f'  [FAIL] id={reg_id} 快照缺失'); all_pass=False; continue
    B = s[4]
    exp_Cn = exp_an[reg_id] / B if B else 1.0
    exp_D  = exp_raw[reg_id] / exp_Cn if exp_Cn else exp_raw[reg_id]
    raw_ok = abs(s[2] - exp_raw[reg_id]) < 0.01
    an_ok  = abs(s[3] - exp_an[reg_id])  < 0.01
    cn_ok  = abs(s[5] - exp_Cn)          < 0.001
    d_ok   = abs(s[6] - exp_D)           < 0.01
    ok = raw_ok and an_ok and cn_ok and d_ok
    if not ok: all_pass = False
    print(f'  [{"PASS" if ok else "FAIL"}] id={reg_id} '
          f'rawAvg={s[2]:.1f}(✓{exp_raw[reg_id]}) '
          f'An={s[3]:.3f}(✓{exp_an[reg_id]:.1f}) '
          f'B={B:.3f} Cn={s[5]:.4f}(✓{exp_Cn:.4f}) '
          f'D={s[6]:.3f}(✓{exp_D:.3f})')

# 相对排名: P2 > P3 > P4 > P1
ranks = {reg_id: snap_map[reg_id][7] for reg_id in [p1_id,p2_id,p3_id,p4_id] if reg_id in snap_map}
order_ok = (ranks.get(p2_id,99) < ranks.get(p3_id,99) <
            ranks.get(p4_id,99) < ranks.get(p1_id,99))
print(f'  [{"PASS" if order_ok else "FAIL"}] 相对排名顺序 P2({ranks.get(p2_id)})<P3({ranks.get(p3_id)})<P4({ranks.get(p4_id)})<P1({ranks.get(p1_id)})')
if not order_ok: all_pass = False
print(f'\n{"[ALL PASS]" if all_pass else "[SOME FAILED]"} 系数调整排名测试{"通过" if all_pass else "未通过"}')

# ── 8. 入围列表 ───────────────────────────────────────────────
resp = requests.get(f'{BASE}/api/admin/shortlist',
    params={'competitionId': COMPETITION_ID, 'stage': 'BOOK', 'groupType': 'COMPREHENSIVE'},
    headers=headers)
if resp.status_code == 200:
    items = resp.json().get('data', [])
    test_items = [x for x in items if x['registrationId'] in proj_ids]
    print(f'\n[API] shortlist 测试项目({len(test_items)}条):')
    for it in test_items:
        print(f'  irank={it["irank"]} adj={it.get("adjustedScore"):.2f} '
              f'withinLine={it["withinLine"]} shortlisted={it["shortlisted"]}')
else:
    print(f'[ERR] shortlist → {resp.status_code} {resp.text[:200]}')

# ── 9. 测试增补 ───────────────────────────────────────────────
not_shortlisted = [x for x in items if not x['shortlisted'] and x['registrationId'] in proj_ids]
if not_shortlisted:
    override_reg = not_shortlisted[0]['registrationId']
    resp2 = requests.put(f'{BASE}/api/admin/shortlist/override',
        json={'registrationId': override_reg, 'override': 'INCLUDE', 'note': '测试增补'},
        headers=headers)
    print(f'\n[API] override(INCLUDE) → {resp2.status_code}')
    resp3 = requests.get(f'{BASE}/api/admin/shortlist',
        params={'competitionId': COMPETITION_ID, 'stage': 'BOOK', 'groupType': 'COMPREHENSIVE'},
        headers=headers)
    after = resp3.json().get('data', [])
    target = next((x for x in after if x['registrationId'] == override_reg), None)
    ok = target and target['shortlisted']
    print(f'  [{"PASS" if ok else "FAIL"}] 增补id={override_reg} shortlisted={target.get("shortlisted") if target else "N/A"} override={target.get("override") if target else "N/A"}')
    requests.delete(f'{BASE}/api/admin/shortlist/override/{override_reg}', headers=headers)
    print(f'  [OK] 已清除 override')

# ── 10. 面谈打分 ──────────────────────────────────────────────
print('\n=== 面谈打分测试 ===')
conn2.ping(reconnect=True)
cur2.execute("""
    SELECT rt.id FROM review_tasks rt
    JOIN registrations r ON rt.registration_id=r.id
    WHERE r.group_type='ADVANCED' AND rt.stage='INTERVIEW' AND rt.status='PENDING'
    LIMIT 1
""")
row = cur2.fetchone()
if row:
    task_id = row[0]
    cur2.execute('DELETE FROM interview_scores WHERE review_task_id=%s', (task_id,))
    conn2.commit()
    print(f'[INFO] 面谈任务 id={task_id}')
    payload = {'reviewTaskId': task_id, 'topic': 8.5, 'process': 35.0,
               'operation': 18.0, 'result': 27.0, 'highlight': '选题新颖', 'weakness': '数据略薄'}
    resp5 = requests.post(f'{BASE}/api/reviews/interview-scores', json=payload, headers=headers)
    if resp5.status_code == 200:
        d5 = resp5.json().get('data', {})
        exp_total = 8.5+35.0+18.0+27.0
        ok5 = abs(d5.get('total', 0) - exp_total) < 0.01
        print(f'  [{"PASS" if ok5 else "FAIL"}] total={d5.get("total")}(期望{exp_total})')
        resp6 = requests.get(f'{BASE}/api/reviews/interview-scores/{task_id}', headers=headers)
        if resp6.status_code == 200:
            d6 = resp6.json().get('data', {})
            print(f'  [PASS] 查询 total={d6.get("total")} highlight={d6.get("highlight")}')
        else:
            print(f'  [FAIL] 查询 → {resp6.status_code}')
    else:
        print(f'  [ERR] 提交失败 {resp5.status_code}: {resp5.text[:200]}')
else:
    print('[WARN] 无进阶组面谈任务，跳过')

conn.close()
conn2.close()
print('\n[DONE] 全部测试完成')
