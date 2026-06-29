import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4'
)
cur = conn.cursor()

# 先看现在的值
cur.execute("SELECT id, staff_id, session_code FROM staff_session_assignments ORDER BY staff_id, session_code")
rows = cur.fetchall()
print(f"当前 staff_session_assignments ({len(rows)} 行):")
for r in rows:
    print(f"  id={r[0]} staff={r[1]} code={r[2]}")

# 映射：旧短格式 → 新2026格式
mapping = {
    '基层组1组':               '2026基层组1组',
    '基层组2组':               '2026基层组2组',
    '基层组3组':               '2026基层组3组',
    '基层组4组':               '2026基层组4组',
    '进阶组1组':               '2026进阶组1组',
    '进阶组 2组':              '2026进阶组2组',
    '进阶组2组':               '2026进阶组2组',
    '进阶组3组':               '2026进阶组3组',
    '综合组-PDCA专场1':        '2026综合组PDCA专场1',
    '综合组-PDCA专场2':        '2026综合组PDCA专场2',
    '综合组-PDCA专场3':        '2026综合组PDCA专场3',
    '综合组-综合工具专场1':    '2026综合组综合工具专场1',
    '综合组-综合工具专场2':    '2026综合组综合工具专场2',
    '综合组-十大安全目标专场1':'2026综合组十大安全目标专场1',
    '综合组-十大安全目标专场2':'2026综合组十大安全目标专场2',
    '综合组-问题解决型专场1':  '2026综合组问题解决型专场1',
    '综合组-问题解决型专场2':  '2026综合组问题解决型专场2',
    '综合组-问题解决型专场3':  '2026综合组问题解决型专场3',
    '综合组-问题解决型专场4':  '2026综合组问题解决型专场4',
    '综合组-课题达成及QFD专场2改1': '2026综合组QFD、课题达成型专场1',
    '综合组-课题达成及QFD专场1改2': '2026综合组QFD、课题达成型专场2',
    '综合组-课题达成及QFD专场2':    '2026综合组QFD、课题达成型专场2',
    '综合组-课题达成及QFD专场3':    '2026综合组QFD、课题达成型专场3',
}

print("\n更新 staff_session_assignments:")
total = 0
for old, new in mapping.items():
    cur.execute(
        "UPDATE staff_session_assignments SET session_code = %s WHERE session_code = %s",
        (new, old)
    )
    if cur.rowcount:
        print(f"  {old} -> {new}  ({cur.rowcount}行)")
        total += cur.rowcount
conn.commit()
print(f"合计更新 {total} 行")

# 验证
cur.execute("""
    SELECT ua.phone, ua.name, ssa.session_code
    FROM staff_session_assignments ssa
    JOIN user_accounts ua ON ua.id = ssa.staff_id
    ORDER BY ua.phone, ssa.session_code
""")
rows = cur.fetchall()
print(f"\n验证 ({len(rows)} 条):")
for r in rows:
    print(f"  {r[0]} {r[1]}  {r[2]}")

conn.close()
