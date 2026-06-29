import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB); cur = conn.cursor()

cur.execute("SELECT id, project_name FROM registrations WHERE id=20260321")
print("id=20260321:", cur.fetchone())

cur.execute("SELECT id, project_name FROM registrations WHERE project_name LIKE '%胸痛%' OR project_name LIKE '%转诊延迟%'")
print("关键词搜索:", cur.fetchall())

cur.execute("""
  SELECT r.id, r.project_name, i.name
  FROM registrations r
  JOIN institutions i ON i.id=r.institution_id
  WHERE i.name LIKE '%淳安%中医%'
""")
print("淳安县中医院的项目:")
for row in cur.fetchall():
    print(f"  id={row[0]}  {row[2]}  {row[1]}")

cur.close(); conn.close()
