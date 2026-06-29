import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB); cur = conn.cursor()

# 按 session + order 查这8条
cur.execute("""
  SELECT r.id, r.final_session_order, r.project_name, r.final_score_form, i.name
  FROM registrations r
  JOIN institutions i ON i.id=r.institution_id
  WHERE r.final_session_code='综合组-十大安全目标专场1'
  ORDER BY r.final_session_order
""")
for row in cur.fetchall():
    print(f"  id={row[0]}  order={row[1]}  form={row[3]}")
    print(f"    机构: {row[4]}")
    print(f"    项目: {row[2]}")

cur.close(); conn.close()
