import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 找这个项目的快照
cur.execute("""
    SELECT ss.irank, ss.group_code, ss.group_type,
           ss.raw_avg, ss.group_avg, ss.overall_avg, ss.coefficient, ss.adjusted_score,
           r.project_name
    FROM scoring_snapshots ss
    JOIN registrations r ON ss.registration_id = r.id
    WHERE r.project_name LIKE '%失效模式%小学卫生站%'
      AND ss.stage = 'BOOK'
""")
row = cur.fetchone()
if not row:
    print('未找到该项目快照'); exit()

irank, gc, gt, raw, ga, oa, cn, adj, name = row
print('='*60)
print(f'项目: {name}')
print(f'排名: 第 {irank} 名   组别: {gt}   小组: {gc}')
print()
print(f'  原始均分(rawAvg)     = {raw:.2f}   ← 两位评委打分的平均')
print(f'  小组均分An           = {ga:.2f}   ← 该小组({gc})所有评委打分的均值')
print(f'  大组均分B            = {oa:.2f}   ← {gt} 组全部评委打分的均值')
print(f'  系数 Cn = An/B       = {cn:.4f}')
print(f'  调整分 D = raw/Cn    = {raw:.2f} / {cn:.4f} = {adj:.2f}')
print()

# 同大组所有项目快照，对比排名
cur.execute("""
    SELECT ss.irank, ss.group_code, ss.raw_avg, ss.coefficient, ss.adjusted_score,
           r.project_name
    FROM scoring_snapshots ss
    JOIN registrations r ON ss.registration_id = r.id
    WHERE ss.stage='BOOK' AND ss.group_type=%s
      AND ss.competition_id=1
    ORDER BY ss.irank
    LIMIT 10
""", (gt,))
rows = cur.fetchall()
print(f'{gt} 组排名（前10）:')
print(f'  {"rank":>4}  {"gc":>5}  {"rawAvg":>7}  {"Cn":>7}  {"adjScore":>9}  项目名')
for r in rows:
    marker = ' ←★' if r[0] == irank else ''
    print(f'  {r[0]:>4}  {r[1]:>5}  {r[2]:>7.2f}  {r[3]:>7.4f}  {r[4]:>9.2f}  {str(r[5])[:28]}{marker}')

# 查一下 gc 组的所有打分，解释 An 为啥低
cur.execute("""
    SELECT rs.total, r.project_name
    FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    JOIN registrations r ON rt.registration_id = r.id
    WHERE rt.stage='BOOK' AND r.group_code=%s AND r.competition_id=1
""", (gc,))
scores = cur.fetchall()
vals = [s[0] for s in scores if 65 <= s[0] <= 95]
an = sum(vals)/len(vals) if vals else 0
print(f'\n小组 {gc} 的所有打分（共{len(scores)}个，去极值后{len(vals)}个）:')
print(f'  分值: {sorted([s[0] for s in scores])}')
print(f'  An = {an:.4f}（去极值后均值）')
print(f'  B  = {oa:.4f}（大组均值）')
print(f'  Cn = An/B = {an:.4f}/{oa:.4f} = {an/oa:.4f}  → Cn<1，专家评分偏严，项目分被拉高')

conn.close()
