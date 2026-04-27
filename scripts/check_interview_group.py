import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# INTERVIEW 阶段任务的报名分组情况
cur.execute("""
    SELECT r.group_type, r.group_code, COUNT(DISTINCT rt.registration_id) AS reg_count,
           COUNT(rt.id) AS task_count
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    WHERE rt.stage = 'INTERVIEW'
    GROUP BY r.group_type, r.group_code
    ORDER BY r.group_type, r.group_code
""")
print("=== INTERVIEW 任务按分组统计 ===")
for row in cur.fetchall():
    print(f"  group_type={row[0]}  group_code={row[1]}  registrations={row[2]}  tasks={row[3]}")

# 非进阶组的 INTERVIEW 任务详情
cur.execute("""
    SELECT rt.id AS task_id, rt.registration_id, rt.status,
           r.project_name, r.group_type, r.group_code
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    WHERE rt.stage = 'INTERVIEW'
      AND r.group_type != 'ADVANCED'
    ORDER BY r.group_type, rt.registration_id
""")
rows = cur.fetchall()
print(f"\n=== 非进阶组 INTERVIEW 任务（共 {len(rows)} 条）===")
for row in rows:
    print(f"  task_id={row[0]} reg={row[1]} status={row[2]} group={row[4]}/{row[5]} 项目={row[3][:30]}")

conn.close()
