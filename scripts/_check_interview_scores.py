import sys, io, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    # 已提交的面谈评分总数
    cur.execute("SELECT COUNT(*) FROM interview_scores WHERE submitted_at IS NOT NULL")
    submitted_total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM interview_scores WHERE submitted_at IS NULL")
    draft_total = cur.fetchone()[0]

    print(f'面谈评分 - 已提交(submitted_at IS NOT NULL): {submitted_total} 条')
    print(f'面谈评分 - 草稿(submitted_at IS NULL):       {draft_total} 条')

    # 看看是哪些评委提交的
    cur.execute("""
        SELECT ua.name, ua.phone, ua.interview_group_code, COUNT(*) as cnt,
               MIN(is_.submitted_at) as first_submit, MAX(is_.submitted_at) as last_submit
        FROM interview_scores is_
        JOIN review_tasks rt ON rt.id = is_.review_task_id
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        WHERE is_.submitted_at IS NOT NULL
        GROUP BY ua.id, ua.name, ua.phone, ua.interview_group_code
        ORDER BY cnt DESC
    """)
    rows = cur.fetchall()
    print(f'\n已提交面谈评分的评委（共 {len(rows)} 人）:')
    for r in rows:
        print(f'  {r[0]}  {r[1]}  interview_group={r[2]}  已提交:{r[3]}条  时间:{r[4]} ~ {r[5]}')
conn.close()
