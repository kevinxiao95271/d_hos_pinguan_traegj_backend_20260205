import pymysql, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT id, name, code, uscc, region, city, level, is_ext
    FROM institutions
    WHERE uscc = '123305004711716660'
""")
r = cur.fetchone()
if r:
    print(f"id       = {r[0]}")
    print(f"name     = {r[1]}")
    print(f"code     = {r[2]}")
    print(f"uscc     = {r[3]}")
    print(f"region   = {r[4]}")
    print(f"city     = {r[5]}")
    print(f"level    = {r[6]}")
    print(f"is_ext   = {r[7]}")
conn.close()
