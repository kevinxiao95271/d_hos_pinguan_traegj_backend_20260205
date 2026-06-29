import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB); cur = conn.cursor()

# 查 20260321 是否存在
cur.execute("SELECT id, project_name FROM registrations WHERE id=20260321")
print("id=20260321:", cur.fetchone())

# 淳安县中医院所有正式报名（id 在 20260000-20270000 区间）
cur.execute("""
  SELECT r.id, r.project_name, i.name
  FROM registrations r
  JOIN institutions i ON i.id=r.institution_id
  WHERE i.name LIKE '%淳安%'
    AND r.id BETWEEN 20260000 AND 20270000
""")
rows = cur.fetchall()
print("淳安县正式报名数据:")
for row in rows:
    print(f"  id={row[0]}  {row[2]}")
    print(f"    项目名: {row[1]}")

# 全库有多少正式报名
cur.execute("SELECT COUNT(*) FROM registrations WHERE id BETWEEN 20260000 AND 20270000")
print("正式报名总数:", cur.fetchone()[0])

cur.close(); conn.close()
