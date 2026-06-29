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

steps = [
    # Step 1: 加列
    ("加列 final_session_code_desc",
     "ALTER TABLE registrations ADD COLUMN final_session_code_desc VARCHAR(128) DEFAULT NULL COMMENT '现场场次原始描述（含场地名）' AFTER final_session_code"),

    # Step 2: 备份原值
    ("备份原值",
     "UPDATE registrations SET final_session_code_desc = final_session_code WHERE final_session_code IS NOT NULL"),

    # Step 3: 更新 21 个场次（测试库短格式 → 标准格式）
    ("基层组1组", "UPDATE registrations SET final_session_code = '2026基层组1组' WHERE final_session_code = '基层组1组'"),
    ("基层组2组", "UPDATE registrations SET final_session_code = '2026基层组2组' WHERE final_session_code = '基层组2组'"),
    ("基层组3组", "UPDATE registrations SET final_session_code = '2026基层组3组' WHERE final_session_code = '基层组3组'"),
    ("基层组4组", "UPDATE registrations SET final_session_code = '2026基层组4组' WHERE final_session_code = '基层组4组'"),
    ("进阶组1组", "UPDATE registrations SET final_session_code = '2026进阶组1组' WHERE final_session_code = '进阶组1组'"),
    ("进阶组2组", "UPDATE registrations SET final_session_code = '2026进阶组2组' WHERE final_session_code = '进阶组 2组'"),
    ("进阶组3组", "UPDATE registrations SET final_session_code = '2026进阶组3组' WHERE final_session_code = '进阶组3组'"),
    ("PDCA专场1", "UPDATE registrations SET final_session_code = '2026综合组PDCA专场1' WHERE final_session_code = '综合组-PDCA专场1'"),
    ("PDCA专场2", "UPDATE registrations SET final_session_code = '2026综合组PDCA专场2' WHERE final_session_code = '综合组-PDCA专场2'"),
    ("PDCA专场3", "UPDATE registrations SET final_session_code = '2026综合组PDCA专场3' WHERE final_session_code = '综合组-PDCA专场3'"),
    ("综合工具专场1", "UPDATE registrations SET final_session_code = '2026综合组综合工具专场1' WHERE final_session_code = '综合组-综合工具专场1'"),
    ("综合工具专场2", "UPDATE registrations SET final_session_code = '2026综合组综合工具专场2' WHERE final_session_code = '综合组-综合工具专场2'"),
    ("十大安全专场1", "UPDATE registrations SET final_session_code = '2026综合组十大安全目标专场1' WHERE final_session_code = '综合组-十大安全目标专场1'"),
    ("十大安全专场2", "UPDATE registrations SET final_session_code = '2026综合组十大安全目标专场2' WHERE final_session_code = '综合组-十大安全目标专场2'"),
    ("问题解决型专场1", "UPDATE registrations SET final_session_code = '2026综合组问题解决型专场1' WHERE final_session_code = '综合组-问题解决型专场1'"),
    ("问题解决型专场2", "UPDATE registrations SET final_session_code = '2026综合组问题解决型专场2' WHERE final_session_code = '综合组-问题解决型专场2'"),
    ("问题解决型专场3", "UPDATE registrations SET final_session_code = '2026综合组问题解决型专场3' WHERE final_session_code = '综合组-问题解决型专场3'"),
    ("问题解决型专场4", "UPDATE registrations SET final_session_code = '2026综合组问题解决型专场4' WHERE final_session_code = '综合组-问题解决型专场4'"),
    ("QFD课题达成专场1", "UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场1' WHERE final_session_code = '综合组-课题达成及QFD专场2改1'"),
    ("QFD课题达成专场2", "UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场2' WHERE final_session_code = '综合组-课题达成及QFD专场1改2'"),
    ("QFD课题达成专场3", "UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场3' WHERE final_session_code = '综合组-课题达成及QFD专场3'"),
]

for label, sql in steps:
    try:
        cur.execute(sql)
        conn.commit()
        print(f"OK  [{label}]  affected={cur.rowcount}")
    except Exception as e:
        print(f"ERR [{label}]  {e}")
        conn.rollback()

# 验证
cur.execute("SELECT DISTINCT final_session_code, COUNT(*) cnt FROM registrations WHERE final_session_code IS NOT NULL GROUP BY final_session_code ORDER BY final_session_code")
rows = cur.fetchall()
print(f"\n验证 - 共 {len(rows)} 个场次:")
for r in rows:
    print(f"  {r[0]}  ({r[1]}项)")

conn.close()
