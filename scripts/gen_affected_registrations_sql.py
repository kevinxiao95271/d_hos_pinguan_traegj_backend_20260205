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

# 取所有同USCC多名称的USCC列表
cur.execute("""
SELECT uscc
FROM const_init_institutions
WHERE uscc IS NOT NULL
GROUP BY uscc
HAVING COUNT(DISTINCT name) > 1
""")
rows = cur.fetchall()
uscc_list = [row[0] for row in rows]
print(f"-- 共 {len(uscc_list)} 个USCC（同USCC多名称）\n")

# 拼装 IN 列表（分批，每500个一组避免超长）
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

in_clauses = []
for batch in chunks(uscc_list, 500):
    vals = ', '.join(f"'{v}'" for v in batch)
    in_clauses.append(vals)

# 生成查询SQL
print("-- ================================================")
print("-- 查哪些报名项目落在这些机构范围内")
print("-- ================================================")

if len(in_clauses) == 1:
    in_sql = f"({in_clauses[0]})"
else:
    # 多批用 UNION 的方式拼 IN，或者直接用子查询
    in_sql = """(
    SELECT uscc FROM const_init_institutions
    WHERE uscc IS NOT NULL
    GROUP BY uscc
    HAVING COUNT(DISTINCT name) > 1
)"""

sql = f"""SELECT
    r.id            AS registration_id,
    r.project_name,
    r.group_type,
    r.status,
    r.submitted_at,
    i.id            AS institution_id,
    i.name          AS institution_name,
    i.uscc,
    ua.id           AS user_id,
    ua.phone,
    ua.name         AS user_name
FROM registrations r
JOIN institutions i  ON r.institution_id = i.id
JOIN user_accounts ua ON r.applicant_id  = ua.id
WHERE i.uscc IN {in_sql}
ORDER BY i.uscc, r.id;"""

print(sql)

conn.close()
