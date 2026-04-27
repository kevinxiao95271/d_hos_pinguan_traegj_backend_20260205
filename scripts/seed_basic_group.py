"""
为基层组构造测试数据：
- 取 6 个基层组项目，分成 2 小组（J1/J2，各 3 个）
- 每个项目分配 2 位评委打分（已打分状态）
- 触发 compute-ranking
- 查看入围结果
"""
import pymysql, requests, sys, random
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'
COMPETITION_ID = 1

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# ── 登录 ──────────────────────────────────────────────────────
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
print('[OK] 登录成功')

# ── 取基层组已提交项目 ──────────────────────────────────────
cur.execute("""
    SELECT id, project_name FROM registrations
    WHERE competition_id=%s AND group_type='BASIC' AND status='SUBMITTED'
    ORDER BY id LIMIT 6
""", (COMPETITION_ID,))
projects = cur.fetchall()
print(f'\n[INFO] 基层组项目数: {len(projects)}')
if len(projects) < 2:
    print('[ERR] 基层组项目不足，退出'); conn.close(); sys.exit(1)
for p in projects:
    print(f'  id={p[0]} {p[1][:30]}')

# 分三小组 A1/A2/A3，每组 2 个项目
groups = {'A1': [p[0] for p in projects[0:2]],
          'A2': [p[0] for p in projects[2:4]],
          'A3': [p[0] for p in projects[4:6]]}
for gc, pids in groups.items():
    for pid in pids:
        cur.execute("UPDATE registrations SET group_code=%s WHERE id=%s", (gc, pid))
conn.commit()
print(f'\n[OK] 分组完成: ' + '  '.join(f'{gc}={pids}' for gc, pids in groups.items()))

# ── 取 2 位评委 ───────────────────────────────────────────────
cur.execute("SELECT id, name FROM user_accounts WHERE role='REVIEWER' LIMIT 2")
reviewers = cur.fetchall()
r1, r2 = reviewers[0][0], reviewers[1][0]
print(f'[INFO] 评委: {reviewers[0][1]}(id={r1})  {reviewers[1][1]}(id={r2})')

# ── 清理旧 BOOK 任务 ──────────────────────────────────────────
all_ids = tuple(p[0] for p in projects)
cur.execute(f"""
    DELETE rs FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id=rt.id
    WHERE rt.stage='BOOK' AND rt.registration_id IN {all_ids}
""")
cur.execute(f"DELETE FROM review_tasks WHERE stage='BOOK' AND registration_id IN {all_ids}")
conn.commit()

# ── 构造打分：J1 评委打分偏低(76-84)，J2 偏高(85-92)，模拟专家差异 ──
random.seed(42)
# A1 偏低(75-82)，A2 中等(80-87)，A3 偏高(85-92)，模拟不同专家评分差异
ranges = {'A1': (75, 82), 'A2': (80, 87), 'A3': (85, 92)}
score_plan = []
for gc, pids in groups.items():
    lo, hi = ranges[gc]
    for pid in pids:
        score_plan.append((pid, r1, random.randint(lo, hi)))
        score_plan.append((pid, r2, random.randint(lo, hi)))

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
print(f'[OK] 写入 {len(score_plan)} 条基层组评分')
print('     分布: A1 约 75-82 分，A2 约 80-87 分，A3 约 85-92 分（模拟专家评分差异）')

# ── 触发 compute-ranking（不传 groupType，同时算基层+综合） ──
resp = requests.post(f'{BASE}/api/admin/reviews/compute-ranking',
    json={'competitionId': COMPETITION_ID, 'stage': 'BOOK'},
    headers=headers)
print(f'\n[API] compute-ranking → {resp.status_code} 写入快照数={resp.json().get("data")}')

# ── 查入围结果（PER_GROUP 模式，基层前3+综合前3）─────────────
# 先设置配置
requests.put(f'{BASE}/api/admin/shortlist/config',
    json={'groupType':'BASIC','mode':'COUNT','value':3}, headers=headers)
requests.put(f'{BASE}/api/admin/shortlist/config',
    json={'groupType':'COMPREHENSIVE','mode':'COUNT','value':3}, headers=headers)
requests.put(f'{BASE}/api/admin/shortlist/book-scope',
    json={'scope':'PER_GROUP'}, headers=headers)

resp2 = requests.get(f'{BASE}/api/admin/shortlist',
    params={'competitionId': COMPETITION_ID, 'stage': 'BOOK'},
    headers=headers)
items = resp2.json().get('data', [])
shortlisted = [x for x in items if x['shortlisted']]
print(f'\n[RESULT] 书审入围名单（PER_GROUP，各取前3）:')
print(f'  总返回 {len(items)} 条，入围 {len(shortlisted)} 条')
for gt in ['BASIC','COMPREHENSIVE']:
    grp = [x for x in items if x['groupType']==gt]
    win = [x for x in grp if x['shortlisted']]
    print(f'\n  [{gt}] 共{len(grp)}条，入围{len(win)}条:')
    for x in grp[:6]:
        mark = '★入围' if x['shortlisted'] else '  落选'
        print(f'    {mark} irank={x["irank"]} adj={x["adjustedScore"]:.2f} '
              f'groupCode={x["groupCode"]} proj={str(x["projectName"])[:20]}')

# ── 也测 UNIFIED 模式 ─────────────────────────────────────────
requests.put(f'{BASE}/api/admin/shortlist/book-scope',
    json={'scope':'UNIFIED','unifiedMode':'RATIO','unifiedValue':0.5}, headers=headers)
resp3 = requests.get(f'{BASE}/api/admin/shortlist',
    params={'competitionId': COMPETITION_ID, 'stage': 'BOOK'},
    headers=headers)
items3 = resp3.json().get('data', [])
win3 = [x for x in items3 if x['shortlisted']]
print(f'\n[RESULT] 书审入围名单（UNIFIED，合并前50%）:')
print(f'  总返回 {len(items3)} 条，入围 {len(win3)} 条（基层+综合合并排名）')
for x in items3[:8]:
    mark = '★入围' if x['shortlisted'] else '  落选'
    print(f'  {mark} adj={x["adjustedScore"]:.2f} groupType={x["groupType"]} '
          f'groupCode={x["groupCode"]} proj={str(x["projectName"])[:20]}')

# 恢复 PER_GROUP
requests.put(f'{BASE}/api/admin/shortlist/book-scope', json={'scope':'PER_GROUP'}, headers=headers)
conn.close()
print('\n[DONE] 完成，已恢复为 PER_GROUP 模式')
