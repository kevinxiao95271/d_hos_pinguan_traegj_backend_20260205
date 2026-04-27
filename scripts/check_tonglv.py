import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, name, uscc, region, city, level FROM institutions
    WHERE name LIKE '%桐庐%第一%'
""")
print("=== institutions ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}  region={r[3]}")

cur.execute("""
    SELECT id, name, uscc FROM const_init_institutions
    WHERE name LIKE '%桐庐%第一%'
""")
print("\n=== const_init_institutions ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

# 有多少用户绑定了这家机构
cur.execute("""
    SELECT COUNT(*) FROM user_accounts ua
    JOIN institutions i ON ua.institution_id = i.id
    WHERE i.name LIKE '%桐庐%第一%'
""")
print(f"\n绑定该机构的用户数: {cur.fetchone()[0]}")

# 有多少报名项目
cur.execute("""
    SELECT COUNT(*) FROM registrations r
    JOIN institutions i ON r.institution_id = i.id
    WHERE i.name LIKE '%桐庐%第一%'
""")
print(f"关联的报名项目数: {cur.fetchone()[0]}")

conn.close()
