import pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

# 确认表已建
cur.execute("SHOW TABLES LIKE 'staff_session_assignments'")
print("staff_session_assignments 表:", "存在" if cur.fetchone() else "不存在！请检查JPA是否建表")

# 密码哈希
raw = bcrypt.hashpw(b'opt123', bcrypt.gensalt(rounds=10)).decode()
hashed = raw.replace('$2b$', '$2a$', 1)
print(f"密码哈希: {hashed}")

SESSION_MAP = {
    '综合组问题解决型1': '综合组-问题解决型专场1（三楼开元A厅）',
    '综合组问题解决型2': '综合组-问题解决型专场2（三楼开元A厅）',
    '综合组问题解决型3': '综合组-问题解决型专场3（三楼锦兰厅）',
    '综合组问题解决型4': '综合组-问题解决型专场4(三楼开元A厅)',
    '综合组课达QFD1':   '综合组-课题达成及QFD专场2改1（三楼开元B厅）',
    '综合组课达QFD2':   '综合组-课题达成及QFD专场2（三楼开元B厅）',
    '综合组课达QFD3':   '综合组-课题达成及QFD专场3（三楼开元B厅）',
    '进阶组1':          '进阶组1组（三楼萧然厅）',
    '进阶组2':          '进阶组 2组（三楼萧然厅）',
    '进阶组3':          '进阶组3组（三楼萧然厅）',
    '基层组1':          '基层组1组（一楼活动中心）',
    '基层组2':          '基层组2组（锦绣厅）',
    '基层组3':          '基层组3组（一楼活动中心）',
    '基层组4':          '基层组4组（一楼活动中心）',
    '综合组十大安全目标1': '综合组-十大安全目标专场1（三楼锦绣厅）',
    '综合组十大安全目标2': '综合组-十大安全目标专场2（三楼锦绣厅）',
    '综合组综合工具1':  '综合组-综合工具专场1（三楼锦兰厅）',
    '综合组综合工具2':  '综合组-综合工具专场2（三楼锦兰厅）',
    '综合组PDCA1':      '综合组-PDCA专场1（二楼名仕厅）',
    '综合组PDCA2':      '综合组-PDCA专场2（二楼名仕厅）',
    '综合组PDCA3':      '综合组-PDCA专场3（二楼名仕厅）',
}

staff = [
    ('沈佩儿', '13588040680', ['综合组问题解决型1', '综合组问题解决型2', '综合组问题解决型4']),
    ('钱丽华', '15825502873', ['综合组课达QFD1',   '综合组课达QFD2',   '综合组课达QFD3']),
    ('周桉',   '18057127990', ['进阶组1',           '进阶组2',           '进阶组3']),
    ('华佳宁', '18868634981', ['基层组2',           '综合组十大安全目标1', '综合组十大安全目标2']),
    ('汪洋',   '15996257167', ['综合组综合工具1',   '综合组综合工具2',   '综合组问题解决型3']),
    ('江玲',   '18858161236', ['综合组PDCA1',       '综合组PDCA2',       '综合组PDCA3']),
    ('田阳帆', '18258881995', ['基层组1',           '基层组3',           '基层组4']),
]

now = '2026-05-30 00:00:00'
print("\n--- 插入账号 ---")
for name, phone, sessions in staff:
    # 检查是否已存在
    cur.execute("SELECT id FROM user_accounts WHERE phone=%s", (phone,))
    row = cur.fetchone()
    if row:
        uid = row[0]
        cur.execute("UPDATE user_accounts SET role='OPERATOR', password=%s WHERE id=%s", (hashed, uid))
        print(f"  {name} {phone}  已存在id={uid} -> 更新role+密码")
    else:
        cur.execute(
            "INSERT INTO user_accounts (name,phone,password,role,enabled,created_at) VALUES(%s,%s,%s,'OPERATOR',1,%s)",
            (name, phone, hashed, now))
        uid = cur.lastrowid
        print(f"  {name} {phone}  新建 id={uid}")

    # 会场分配（幂等）
    for short in sessions:
        full = SESSION_MAP[short]
        cur.execute("SELECT 1 FROM staff_session_assignments WHERE staff_id=%s AND session_code=%s", (uid, full))
        if not cur.fetchone():
            cur.execute("INSERT INTO staff_session_assignments (staff_id,session_code) VALUES(%s,%s)", (uid, full))
            print(f"    + 分配会场: {full}")
        else:
            print(f"    = 已有会场: {full}")

conn.commit()
print("\n--- 验证 ---")
cur.execute("""
    SELECT ua.name, ua.phone, ua.role, ssa.session_code
    FROM staff_session_assignments ssa
    JOIN user_accounts ua ON ua.id=ssa.staff_id
    ORDER BY ua.name, ssa.session_code
""")
for row in cur.fetchall():
    print(f"  {row[0]:8s} {row[1]}  {row[2]:10s}  {row[3]}")

cur.close()
conn.close()
print("\n完成！")
