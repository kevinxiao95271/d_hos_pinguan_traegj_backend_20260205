import sys, io, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM interview_scores WHERE submitted_at IS NOT NULL")
    before = cur.fetchone()[0]
    print(f'执行前 - 已提交: {before} 条')

    cur.execute("UPDATE interview_scores SET submitted_at = NULL WHERE submitted_at IS NOT NULL")
    conn.commit()
    print(f'已驳回: {cur.rowcount} 条')

    cur.execute("SELECT COUNT(*) FROM interview_scores WHERE submitted_at IS NOT NULL")
    after = cur.fetchone()[0]
    print(f'执行后 - 已提交: {after} 条')

    cur.execute("SELECT COUNT(*) FROM interview_scores WHERE submitted_at IS NULL")
    draft = cur.fetchone()[0]
    print(f'执行后 - 草稿:   {draft} 条')
conn.close()
print('\n✅ 完成，所有面谈评分已回退至草稿状态，评委需重新整体提交。')
