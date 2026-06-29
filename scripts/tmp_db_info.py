import pymysql
conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com", port=63606,
    user="root", password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, connect_timeout=10
)
with conn.cursor() as c:
    c.execute("SELECT id,phone,role FROM user_accounts WHERE role IN ('ADMIN','OPS') LIMIT 5")
    print("USERS:", c.fetchall())
    c.execute("SELECT id,name,stage FROM competitions ORDER BY id DESC LIMIT 3")
    print("COMPETITIONS:", c.fetchall())
    c.execute("SELECT group_type, COUNT(*) cnt FROM registrations WHERE status='SUBMITTED' GROUP BY group_type")
    print("REG GROUPS:", c.fetchall())
    c.execute("SELECT final_score_form, COUNT(*) cnt FROM registrations WHERE status='SUBMITTED' AND final_score_form IS NOT NULL GROUP BY final_score_form")
    print("SCORE FORMS:", c.fetchall())
    c.execute("SELECT COUNT(*) cnt FROM final_ranking_snapshots")
    print("SNAP COUNT:", c.fetchall())
conn.close()
