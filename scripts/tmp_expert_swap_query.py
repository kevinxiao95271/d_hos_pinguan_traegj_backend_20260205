import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 不限role找张雪霞和汪伟
for name in ['张雪霞', '汪伟']:
    cur.execute("SELECT id, name, phone, role, institution_id FROM user_accounts WHERE name=%s", (name,))
    rows = cur.fetchall()
    print(f"=== {name} (所有role) ===")
    for r in rows: print(r)
    if not rows:
        print("  → 未找到")

# 机构表模糊搜丽水
cur.execute("SELECT id, name FROM institutions WHERE name LIKE '%丽水%' LIMIT 10")
print("\n=== 机构：丽水相关 ===")
for r in cur.fetchall(): print(r)

# 综合工具专场2 真实reviewer数量（排除测试账号）
cur.execute("""
  SELECT ua.name, ua.phone, ua.role, COUNT(*) cnt
  FROM review_tasks rt
  JOIN user_accounts ua ON ua.id = rt.reviewer_id
  JOIN registrations r ON r.id = rt.registration_id
  WHERE r.final_session_code = '2026综合组综合工具专场2' AND rt.stage = 'FINAL'
  GROUP BY ua.id
""")
print("\n=== 综合工具专场2 按评委分组 ===")
for r in cur.fetchall(): print(r)

# QFD专场3 按评委分组
cur.execute("""
  SELECT ua.id, ua.name, ua.phone, ua.role, COUNT(*) cnt
  FROM review_tasks rt
  JOIN user_accounts ua ON ua.id = rt.reviewer_id
  JOIN registrations r ON r.id = rt.registration_id
  WHERE r.final_session_code = '2026综合组QFD、课题达成型专场3' AND rt.stage = 'FINAL'
  GROUP BY ua.id
""")
print("\n=== QFD专场3 按评委分组 ===")
for r in cur.fetchall(): print(r)

# 进阶组3组 按评委分组
cur.execute("""
  SELECT ua.id, ua.name, ua.phone, ua.role, COUNT(*) cnt
  FROM review_tasks rt
  JOIN user_accounts ua ON ua.id = rt.reviewer_id
  JOIN registrations r ON r.id = rt.registration_id
  WHERE r.final_session_code = '2026进阶组3组' AND rt.stage = 'FINAL'
  GROUP BY ua.id
""")
print("\n=== 进阶组3组 按评委分组 ===")
for r in cur.fetchall(): print(r)

conn.close()
