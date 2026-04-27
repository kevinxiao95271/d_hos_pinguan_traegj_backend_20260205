import sys, io, bcrypt, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

phone = '13800000005'
new_pwd = 'ops2026'
hashed = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt(8)).decode().replace('$2b$', '$2a$')
print(f'hash: {hashed}')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("UPDATE user_accounts SET password=%s WHERE phone=%s", (hashed, phone))
    conn.commit()
    print(f'已更新 {cur.rowcount} 条，phone={phone} 密码重置为: {new_pwd}')
conn.close()
