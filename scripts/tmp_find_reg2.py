import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB); cur = conn.cursor()

cur.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM registrations WHERE id BETWEEN 1 AND 999999")
print("非测试数据id范围:", cur.fetchone())

cur.execute("""
  SELECT r.id, r.project_name, i.name
  FROM registrations r
  JOIN institutions i ON i.id=r.institution_id
  WHERE i.name LIKE '%淳安%'
    AND r.id BETWEEN 1 AND 999999
""")
rows = cur.fetchall()
print("淳安县项目（正式数据）:")
for row in rows:
    print(f"  id={row[0]}  {row[2]}  {row[1]}")

cur.close(); conn.close()
