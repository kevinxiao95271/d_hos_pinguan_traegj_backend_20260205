import pymysql, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 看 interview_scores 表结构和数据量
cur.execute("DESCRIBE interview_scores")
print("=== interview_scores 表结构 ===")
for c in cur.fetchall():
    print(f"  {c[0]:30s} {c[1]}")

cur.execute("SELECT COUNT(*) FROM interview_scores")
print(f"\n  总记录数: {cur.fetchone()[0]}")

# 看几条样本
cur.execute("""
    SELECT is2.id, is2.review_task_id, is2.topic, is2.process, is2.interview_operation,
           is2.result, is2.total, is2.submitted_at,
           rt.registration_id, rt.reviewer_id, rt.stage
    FROM interview_scores is2
    JOIN review_tasks rt ON is2.review_task_id = rt.id
    LIMIT 3
""")
print("\n=== 样本数据 ===")
for r in cur.fetchall():
    print(f"  id={r[0]} task={r[1]} topic={r[2]} process={r[3]} op={r[4]} result={r[5]} total={r[6]} stage={r[10]}")
    print(f"  reg={r[8]} reviewer={r[9]} submitted={r[7]}")

# review-details 的底层查询逻辑：scoreSummaryByRegistration
# 看一个有数据的报名
cur.execute("""
    SELECT DISTINCT rt.registration_id
    FROM interview_scores is2
    JOIN review_tasks rt ON is2.review_task_id = rt.id
    LIMIT 1
""")
row = cur.fetchone()
if row:
    rid = row[0]
    print(f"\n=== 报名 {rid} 的面谈得分汇总 ===")
    cur.execute("""
        SELECT ua.name AS reviewer, is2.topic, is2.process, is2.interview_operation,
               is2.result, is2.total, rt.status, is2.submitted_at
        FROM review_tasks rt
        JOIN interview_scores is2 ON is2.review_task_id = rt.id
        JOIN user_accounts ua ON rt.reviewer_id = ua.id
        WHERE rt.registration_id = %s
    """, (rid,))
    for r in cur.fetchall():
        print(f"  {r[0]}: topic={r[1]} process={r[2]} op={r[3]} result={r[4]} total={r[5]} status={r[6]}")

conn.close()
