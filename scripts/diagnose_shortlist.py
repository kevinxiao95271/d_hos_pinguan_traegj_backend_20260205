import pymysql, requests, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'
COMPETITION_ID = 1

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

print('=== 当前入围配置 ===')
cfg = requests.get(f'{BASE}/api/admin/shortlist/config', headers=h).json()['data']
for c in cfg:
    print(f'  {c["groupType"]:<15} mode={c["mode"]}  value={c["value"]}')
scope = requests.get(f'{BASE}/api/admin/shortlist/book-scope', headers=h).json()['data']
print(f'  book-scope={scope["scope"]}')

print('\n=== 快照分布 ===')
cur.execute("""
    SELECT group_type, COUNT(*) total
    FROM scoring_snapshots WHERE competition_id=%s AND stage='BOOK'
    GROUP BY group_type
""", (COMPETITION_ID,))
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} 条')

print('\n=== shortlist_override 有值的项目 ===')
cur.execute("""
    SELECT r.id, r.project_name, r.group_type, r.shortlist_override, r.shortlist_note
    FROM registrations r
    WHERE r.shortlist_override IS NOT NULL AND r.competition_id=%s
""", (COMPETITION_ID,))
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f'  id={r[0]} override={r[3]} note={r[4]}  {str(r[1])[:25]}')
else:
    print('  （无人工干预）')

print('\n=== API 返回的入围清单（BOOK）===')
items = requests.get(f'{BASE}/api/admin/shortlist',
    params={'competitionId':COMPETITION_ID,'stage':'BOOK'}, headers=h).json().get('data',[])
print(f'  总返回 {len(items)} 条')
by_gt = {}
for x in items:
    by_gt.setdefault(x['groupType'],[]).append(x)
for gt, lst in by_gt.items():
    win = [x for x in lst if x['shortlisted']]
    print(f'\n  [{gt}] 共{len(lst)}条，shortlisted={len(win)}')
    for x in lst:
        mark = '★' if x['shortlisted'] else ' '
        ov = x.get('shortlistOverride') or ''
        print(f'    {mark} irank={x["irank"]} adj={x["adjustedScore"]:.2f} '
              f'withinLine={x["withinLine"]} override={ov or "-"} {str(x["projectName"])[:22]}')

conn.close()
