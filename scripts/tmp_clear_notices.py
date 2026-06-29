import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606, user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 查当前数量
cur.execute("SELECT COUNT(*) FROM reviewer_integrity_notices")
print(f"reviewer_integrity_notices 当前: {cur.fetchone()[0]} 条")

cur.execute("SELECT COUNT(*) FROM user_accounts WHERE notice_confirmed_at IS NOT NULL AND role='REVIEWER'")
print(f"notice_confirmed_at 非空 REVIEWER: {cur.fetchone()[0]} 条")

# 清理
cur.execute("DELETE FROM reviewer_integrity_notices")
print(f"reviewer_integrity_notices 已删除: {cur.rowcount} 条")

cur.execute("UPDATE user_accounts SET notice_confirmed_at = NULL WHERE role = 'REVIEWER'")
print(f"notice_confirmed_at 已清空: {cur.rowcount} 条")

conn.commit()
conn.close()
print("完成")
