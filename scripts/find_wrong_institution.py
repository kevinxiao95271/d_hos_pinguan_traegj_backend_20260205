import pymysql
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    db='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 当前报名中，机构USCC在const_init一拖N范围内的所有用户+机构
cur.execute("""
SELECT DISTINCT
    ua.id           AS user_id,
    ua.phone,
    ua.name         AS user_name,
    i.id            AS institution_id,
    i.name          AS current_institution_name,
    i.uscc
FROM registrations r
JOIN institutions i  ON r.institution_id = i.id
JOIN user_accounts ua ON r.applicant_id  = ua.id
WHERE i.uscc COLLATE utf8mb4_general_ci IN (
    SELECT uscc FROM const_init_institutions
    WHERE uscc IS NOT NULL
    GROUP BY uscc
    HAVING COUNT(DISTINCT name) > 1
)
""")
current_users = cur.fetchall()

confirmed = []   # 历史与当前机构一致 → 可排除
mismatch  = []   # 历史与当前机构不一致 → 需核查
no_his    = []   # 无历史记录 → 无法比对

for row in current_users:
    user_id, phone, user_name, inst_id, curr_inst, uscc = row

    cur.execute("""
        SELECT institution_name, year
        FROM pinguan_his_data
        WHERE hospital_contact_phone COLLATE utf8mb4_general_ci = %s
           OR project_leader_phone   COLLATE utf8mb4_general_ci = %s
        ORDER BY year DESC
        LIMIT 10
    """, (phone, phone))
    his_rows = cur.fetchall()

    if not his_rows:
        no_his.append((user_id, phone, user_name, curr_inst))
        continue

    matched = False
    for his in his_rows:
        his_inst = (his[0] or '').strip()
        his_year = his[1]
        if his_inst == curr_inst.strip():
            confirmed.append((user_id, phone, user_name, curr_inst, his_year))
            matched = True
            break

    if not matched:
        # 取最近一条历史机构名
        his_inst_latest = (his_rows[0][0] or '').strip()
        his_year_latest = his_rows[0][1]
        mismatch.append((user_id, phone, user_name, curr_inst, his_inst_latest, his_year_latest, inst_id, uscc))

print(f"=== ✅ 历史一致、可排除 共 {len(confirmed)} 人 ===\n")
print(f"{'user_id':>8}  {'phone':>13}  {'user_name':^8}  {'institution':^40}  {'his_year':>6}")
print("-" * 90)
for r in confirmed:
    print(f"{r[0]:>8}  {r[1]:>13}  {r[2]:^8}  {r[3]:^40}  {r[4]:>6}")

print()
print(f"=== ⚠️  历史不一致、需核查 共 {len(mismatch)} 人 ===\n")
print(f"{'user_id':>8}  {'phone':>13}  {'name':^8}  {'current':^35}  {'historical':^35}  {'year':>6}")
print("-" * 115)
for r in mismatch:
    print(f"{r[0]:>8}  {r[1]:>13}  {r[2]:^8}  {r[3]:^35}  {r[4]:^35}  {r[5]:>6}")

print()
print(f"=== ❓ 无历史记录 共 {len(no_his)} 人（均为测试/新账号）===\n")
for u in no_his:
    print(f"  user_id={u[0]}  phone={u[1]}  name={u[2]}  curr_inst={u[3]}")

conn.close()
