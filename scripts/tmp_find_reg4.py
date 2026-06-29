import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB); cur = conn.cursor()

# 精确查
cur.execute("SELECT id, project_name, final_session_code FROM registrations WHERE id=20260321")
row = cur.fetchone()
print("精确查id=20260321:", row)

# 范围查（排查编码问题）
cur.execute("SELECT id, project_name FROM registrations WHERE id BETWEEN 20260320 AND 20260322")
rows = cur.fetchall()
print("范围查20260320-20260322:", rows)

# 淳安县中医院所有记录（不限id范围）
cur.execute("""
  SELECT r.id, r.project_name, r.final_session_code, i.name
  FROM registrations r
  JOIN institutions i ON i.id=r.institution_id
  WHERE i.name LIKE '%淳安%中医%'
""")
rows2 = cur.fetchall()
print("淳安县中医院全部记录:")
for row in rows2:
    print(f"  id={row[0]}  session={row[2]}  {row[3]}")
    print(f"    {row[1]}")

cur.close(); conn.close()
