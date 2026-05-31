import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import bcrypt

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

# 取所有参与了 FINAL 任务的评委
cur.execute("""
    SELECT DISTINCT ua.id, ua.name, ua.phone
    FROM user_accounts ua
    JOIN review_tasks rt ON rt.reviewer_id = ua.id
    WHERE rt.stage = 'FINAL'
    ORDER BY ua.phone
""")
reviewers = cur.fetchall()

# 生成 user123 的 BCrypt hash
pwd_hash = bcrypt.hashpw(b'user123', bcrypt.gensalt(rounds=10)).decode('utf-8')
# 替换 $2b$ 为 $2a$ 保持兼容
pwd_hash = pwd_hash.replace('$2b$', '$2a$')

# 批量更新
ids = [r[0] for r in reviewers]
cur.execute(f"UPDATE user_accounts SET password=%s WHERE id IN ({','.join(['%s']*len(ids))})",
            [pwd_hash] + ids)
conn.commit()

print(f"已重置 {len(reviewers)} 个评委密码为 user123\n")
print("手机号列表：")
for _, name, phone in reviewers:
    print(f"{phone}  {name}")

conn.close()
