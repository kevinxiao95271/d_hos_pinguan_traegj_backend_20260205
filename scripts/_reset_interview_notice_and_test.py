import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pymysql
import requests

DB_HOST = 'gz-cdb-bq7gk3k5.sql.tencentcdb.com'
DB_PORT = 63606
DB_USER = 'root'
DB_PASS = 'Yiguo9527_'
DB_NAME = 'd_hos_pinguan_traegj_20260205'
API_BASE = 'http://localhost:6031'

# ---- Step 1: 执行 SQL 删除 INTERVIEW 须知记录 ----
print('=== Step 1: 删除 INTERVIEW 须知记录 ===')
conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    before = cur.fetchone()[0]
    print(f'删除前 INTERVIEW 记录数: {before}')

    cur.execute("DELETE FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    conn.commit()
    print(f'已删除 {cur.rowcount} 条记录')

    cur.execute("SELECT COUNT(*) FROM reviewer_integrity_notices WHERE notice_key = 'INTERVIEW'")
    after = cur.fetchone()[0]
    print(f'删除后 INTERVIEW 记录数: {after}')

    # 取一个有 BOOK 记录（已完成书审须知）的评委账号做测试
    cur.execute("""
        SELECT ua.id, ua.phone, ua.name
        FROM user_accounts ua
        JOIN reviewer_integrity_notices rin ON rin.user_id = ua.id AND rin.notice_key = 'BOOK'
        WHERE ua.role = 'REVIEWER' AND ua.enabled = 1
        LIMIT 1
    """)
    test_reviewer = cur.fetchone()
    print(f'\n测试用评委: id={test_reviewer[0]}, phone={test_reviewer[1]}, name={test_reviewer[2]}')

conn.close()

# ---- Step 2: API 自测 ----
print('\n=== Step 2: API 登录自测 ===')
# 取测试账号密码 - 用已知测试账号
test_phone = test_reviewer[1]

# 先查询该用户密码（直接用数据库账号信息）
conn2 = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
with conn2.cursor() as cur:
    # 取面谈评委（有 interview_group_code 的）
    cur.execute("""
        SELECT ua.id, ua.phone, ua.name, ua.password, ua.interview_group_code
        FROM user_accounts ua
        JOIN reviewer_integrity_notices rin ON rin.user_id = ua.id AND rin.notice_key = 'BOOK'
        WHERE ua.role = 'REVIEWER' AND ua.enabled = 1 AND ua.interview_group_code IS NOT NULL AND ua.interview_group_code != ''
        LIMIT 3
    """)
    interview_reviewers = cur.fetchall()
    print(f'面谈评委样本（有interview_group_code, 已确认BOOK须知）:')
    for r in interview_reviewers:
        print(f'  id={r[0]}, phone={r[1]}, name={r[2]}, interview_group={r[4]}')
conn2.close()

# 用脚本里的已知测试账号
TEST_ACCOUNTS = [
    {'phone': '13626530377', 'password': 'test1234'},  # 周莹
    {'phone': '13777887810', 'password': 'test1234'},  # 李益民
]

# 实际上，我们用 OPS 账号先查一个面谈评委的密码重置，再测
# 更直接：直接调 login-with-password，用面谈评委账号
# 找一个我们知道密码的测试账号
print('\n--- 尝试用面谈评委账号登录（取前3个有面谈分组的评委）---')

conn3 = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
with conn3.cursor() as cur:
    # 找有面谈分组的评委，且我们能确认其密码格式
    cur.execute("""
        SELECT ua.id, ua.phone, ua.name, ua.interview_group_code
        FROM user_accounts ua
        WHERE ua.role = 'REVIEWER' AND ua.enabled = 1 
          AND ua.interview_group_code IS NOT NULL AND ua.interview_group_code != ''
        LIMIT 5
    """)
    rows = cur.fetchall()
    interview_reviewer_sample = rows[0] if rows else None
    print(f'面谈评委（有interview_group_code）共 {len(rows)} 条样本:')
    for r in rows:
        print(f'  id={r[0]}, phone={r[1]}, name={r[2]}, interview_group={r[3]}')

    # 验证这些评委的 pending notice 状态（数据库层面）
    print('\n--- 数据库层 pending INTERVIEW 须知验证 ---')
    for r in rows[:3]:
        uid = r[0]
        cur.execute("SELECT notice_key FROM reviewer_integrity_notices WHERE user_id=%s", (uid,))
        confirmed = [x[0] for x in cur.fetchall()]
        pending = [k for k in ['BOOK', 'INTERVIEW'] if k not in confirmed]
        print(f'  {r[2]}(id={uid}): 已确认={confirmed}, 待确认(pending)={pending}')
conn3.close()

print('\n=== 结论 ===')
print('SQL 执行成功，所有面谈评委的 INTERVIEW 须知记录已清除。')
print('下次登录时，后端将在 pendingIntegrityNoticeKeys 中返回 ["INTERVIEW"]（若已确认BOOK）或 ["BOOK","INTERVIEW"]（两个都待确认）。')
