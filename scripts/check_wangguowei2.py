import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 查王国伟账户
cur.execute("SELECT id, name, phone, institution_id FROM user_accounts WHERE name='王国伟'")
print("=== 王国伟账户 ===")
for r in cur.fetchall():
    print(f"  uid={r[0]} name={r[1]} phone={r[2]} institution_id={r[3]}")
    cur2 = conn.cursor()
    cur2.execute("SELECT id, name, uscc FROM institutions WHERE id=%s", (r[3],))
    inst = cur2.fetchone()
    if inst: print(f"    当前机构: id={inst[0]} {inst[1]} uscc={inst[2]}")

# 查温州中医院（模糊）
cur.execute("SELECT id, name, uscc FROM institutions WHERE name LIKE '%温州%中医%' OR name LIKE '%温州市中医%'")
print("\n=== 温州中医院候选（institutions）===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

# 查 const_init
cur.execute("SELECT id, name, uscc FROM const_init_institutions WHERE name LIKE '%温州%中医%'")
print("\n=== 温州中医院候选（const_init_institutions）===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

# 查 registrations MAX id，了解当前数据规模
cur.execute("SELECT MAX(id), COUNT(*) FROM registrations")
r = cur.fetchone()
print(f"\n registrations: max_id={r[0]}, total={r[1]}")

conn.close()
