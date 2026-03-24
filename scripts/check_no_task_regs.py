import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
                       user='root', password='Yiguo9527_',
                       db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 报名了但完全没有 BOOK 阶段任务的项目
cur.execute("""
    SELECT r.group_type, COUNT(*)
    FROM registrations r
    WHERE r.competition_id = 1
      AND r.group_type IN ('BASIC','COMPREHENSIVE')
      AND NOT EXISTS (
          SELECT 1 FROM review_tasks rt
          WHERE rt.registration_id = r.id AND rt.stage = 'BOOK'
      )
    GROUP BY r.group_type
""")
print('有报名但无 BOOK 任务的项目（按组别）:')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} 个')

# 有任务但全部非 SCORED 的
cur.execute("""
    SELECT r.group_type, COUNT(DISTINCT r.id)
    FROM registrations r
    JOIN review_tasks rt ON rt.registration_id = r.id
    WHERE r.competition_id = 1
      AND r.group_type IN ('BASIC','COMPREHENSIVE')
      AND rt.stage = 'BOOK'
      AND r.id NOT IN (
          SELECT DISTINCT registration_id FROM review_tasks
          WHERE stage='BOOK' AND status='SCORED'
      )
    GROUP BY r.group_type
""")
print('\n有任务但无 SCORED 记录的项目（按组别）:')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} 个')

conn.close()
