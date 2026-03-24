import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 快照表总量与分布
cur.execute("""
    SELECT stage, group_type, COUNT(*), MAX(calculated_at)
    FROM scoring_snapshots
    GROUP BY stage, group_type
    ORDER BY stage, group_type
""")
print('scoring_snapshots 分布:')
for r in cur.fetchall():
    print(f'  stage={r[0]} group={r[1]} count={r[2]} latest={r[3]}')

# 当前 BOOK 阶段已打分项目数（SCORED 任务去重）
cur.execute("""
    SELECT r.group_type, COUNT(DISTINCT rt.registration_id)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
      AND rt.stage = 'BOOK'
      AND rt.status = 'SCORED'
    GROUP BY r.group_type
""")
print('\n当前 BOOK SCORED 项目数（按组别）:')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}')

# 快照 vs 实际已打分的差异
cur.execute("""
    SELECT COUNT(DISTINCT rt.registration_id)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
      AND rt.stage = 'BOOK'
      AND rt.status = 'SCORED'
      AND r.group_type IN ('BASIC', 'COMPREHENSIVE')
""")
print(f'\nBOOK SCORED（仅BASIC+COMPREHENSIVE）项目数: {cur.fetchone()[0]}')

cur.execute("""
    SELECT COUNT(*) FROM scoring_snapshots
    WHERE stage='BOOK' AND group_type IN ('BASIC','COMPREHENSIVE')
""")
print(f'快照中 BASIC+COMPREHENSIVE 数量: {cur.fetchone()[0]}')

conn.close()
