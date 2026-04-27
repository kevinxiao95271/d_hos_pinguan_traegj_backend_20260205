import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 确认用户当前绑定
cur.execute("""
    SELECT ua.id, ua.name, ua.phone, i.id, i.name, i.uscc
    FROM user_accounts ua
    LEFT JOIN institutions i ON ua.institution_id = i.id
    WHERE ua.phone = '13857683505'
""")
print("=== 当前用户绑定 ===")
for r in cur.fetchall():
    print(f"  uid={r[0]}  {r[1]}  phone={r[2]}  inst_id={r[3]}  inst={r[4]}  uscc={r[5]}")

# 确认恩泽医院在 const_init 的信息
cur.execute("""
    SELECT id, name, uscc, region, city, level
    FROM const_init_institutions
    WHERE name = '台州恩泽医疗中心（集团）恩泽医院'
""")
print("\n=== const_init 恩泽医院 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  region={r[3]}  city={r[4]}  level={r[5]}")

# 确认恩泽是否已在 institutions 表
cur.execute("""
    SELECT id, name, uscc FROM institutions
    WHERE name = '台州恩泽医疗中心（集团）恩泽医院'
""")
print("\n=== institutions 恩泽医院 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

conn.close()
