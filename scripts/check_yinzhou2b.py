import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# const_init 里 uscc=12330227756286168R 都有哪些名字
cur.execute("""
    SELECT id, name, uscc FROM const_init_institutions
    WHERE uscc = '12330227756286168R'
""")
print("=== const_init: uscc=12330227756286168R ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

# institutions 表里这个 uscc
cur.execute("""
    SELECT id, name, uscc FROM institutions
    WHERE uscc = '12330227756286168R'
""")
print("\n=== institutions: uscc=12330227756286168R ===")
for r in cur.fetchall():
    print(f"  id={r[0]}  {r[1]}  uscc={r[2]}")

# pinguan_his_data 里出现过哪些名字（含"鄞州"）
cur.execute("""
    SELECT DISTINCT institution_name FROM pinguan_his_data
    WHERE institution_name LIKE '%鄞州%' AND institution_name LIKE '%第二%'
    ORDER BY institution_name
""")
print("\n=== pinguan_his_data: 含'鄞州+第二'的机构名 ===")
for r in cur.fetchall():
    print(f"  {r[0]}")

cur.execute("""
    SELECT DISTINCT institution_name FROM pinguan_his_data
    WHERE institution_name LIKE '%中西医结合%' AND institution_name LIKE '%宁波%'
    ORDER BY institution_name
""")
print("\n=== pinguan_his_data: 宁波中西医结合 ===")
for r in cur.fetchall():
    print(f"  {r[0]}")

conn.close()
