import pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Python bcrypt 生成 $2b$，替换为 $2a$（算法完全相同，Spring Security 接受 $2a$）
raw = bcrypt.hashpw(b'user123', bcrypt.gensalt(rounds=10)).decode()
HASH_USER123 = raw.replace('$2b$', '$2a$', 1)

# 验证可解码
ok = bcrypt.checkpw(b'user123', HASH_USER123.replace('$2a$', '$2b$', 1).encode())
print(f"生成哈希: {HASH_USER123[:20]}...")
print(f"bcrypt 校验: {'通过' if ok else '失败'}")

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("UPDATE user_accounts SET password=%s WHERE role='REVIEWER' AND enabled=1", (HASH_USER123,))
print(f"更新 {cur.rowcount} 条评委密码 -> $2a$ user123")
conn.commit()

cur.execute("SELECT phone, LEFT(password,7) FROM user_accounts WHERE role='REVIEWER' LIMIT 3")
for r in cur.fetchall(): print(f"  {r[0]} -> {r[1]}")
conn.close()
