import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor()

print('=== ADMIN / OPS ===')
cur.execute("SELECT name, phone, role FROM user_accounts WHERE role IN ('ADMIN','OPS','COMMITTEE_ADMIN') ORDER BY role, name")
for r in cur.fetchall():
    print(f'  {r[2]:20s}  {r[1]}  {r[0]}')

print()
print('=== OPERATOR（工作人员）密码 opt123 ===')
cur.execute("""
  SELECT ua.name, ua.phone,
         GROUP_CONCAT(ssa.session_code ORDER BY ssa.session_code SEPARATOR ' | ') as sessions
  FROM user_accounts ua
  LEFT JOIN staff_session_assignments ssa ON ssa.staff_id=ua.id
  WHERE ua.role='OPERATOR'
  GROUP BY ua.id, ua.name, ua.phone
  ORDER BY ua.name
""")
for r in cur.fetchall():
    print(f'  {r[1]}  {r[0]:8s}  {r[2]}')

print()
print('=== REVIEWER（有FINAL任务，按任务数前10）密码 user123 ===')
cur.execute("""
  SELECT ua.name, ua.phone,
         SUM(CASE WHEN rt.stage='FINAL' THEN 1 ELSE 0 END) as final_tasks,
         SUM(CASE WHEN rt.stage='FINAL' AND rt.status='SCORED' THEN 1 ELSE 0 END) as scored,
         SUM(CASE WHEN rt.stage='FINAL' AND rt.status='DRAFT' THEN 1 ELSE 0 END) as draft,
         SUM(CASE WHEN rt.stage='FINAL' AND rt.status='PENDING' THEN 1 ELSE 0 END) as pending
  FROM user_accounts ua
  JOIN review_tasks rt ON rt.reviewer_id=ua.id
  WHERE ua.role='REVIEWER'
  GROUP BY ua.id, ua.name, ua.phone
  HAVING final_tasks > 0
  ORDER BY final_tasks DESC
  LIMIT 10
""")
for r in cur.fetchall():
    print(f'  {r[1]}  {r[0]:10s}  FINAL共:{r[2]}  已评:{r[3]}  草稿:{r[4]}  待评:{r[5]}')

cur.close()
conn.close()
