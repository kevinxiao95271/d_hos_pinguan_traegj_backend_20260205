import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 先看表结构
cur.execute("DESCRIBE registrations")
cols = [r[0] for r in cur.fetchall()]
print("registrations columns:", cols)

# 根据实际列名查报名
cur.execute("SELECT * FROM registrations WHERE id = 20260209")
row = cur.fetchone()
if row:
    d = dict(zip(cols, row))
    print(f"\n报名ID: {d['id']}")
    print(f"项目名: {d.get('project_name','')}")
    print(f"报名状态: {d.get('status','')}")
    uid_col = next((c for c in cols if 'user' in c.lower()), None)
    inst_col = next((c for c in cols if 'institution' in c.lower()), None)
    print(f"user字段: {uid_col}={d.get(uid_col)}")
    print(f"institution字段: {inst_col}={d.get(inst_col)}")

    uid = d.get(uid_col)
    inst_id = d.get(inst_col)

    if uid:
        cur.execute("SELECT id, name, phone FROM user_accounts WHERE id=%s", (uid,))
        u = cur.fetchone()
        if u: print(f"账户: id={u[0]} name={u[1]} phone={u[2]}")

    if inst_id:
        cur.execute("SELECT id, name, uscc FROM institutions WHERE id=%s", (inst_id,))
        i = cur.fetchone()
        if i: print(f"当前机构: id={i[0]} {i[1]} uscc={i[2]}")
else:
    print("未找到 id=20260209")

# 查温州市中医院
cur.execute("SELECT id, name, uscc FROM institutions WHERE name LIKE '%温州%中医%'")
print("\n=== 温州市中医院候选 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

conn.close()
