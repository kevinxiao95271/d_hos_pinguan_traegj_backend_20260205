import pymysql, json

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as c:
    # find a contestant account that we can register with (one with bcrypt password)
    c.execute("""
        SELECT u.id, u.phone, u.name, u.institution_id, i.name as inst_name,
               LEFT(u.password,10) as pwd_prefix,
               COUNT(r.id) as reg_count
        FROM user_accounts u
        JOIN institutions i ON i.id = u.institution_id
        LEFT JOIN registrations r ON r.applicant_id = u.id AND r.competition_id = 1
        WHERE u.role = 'CONTESTANT' AND u.enabled = 1
          AND u.password IS NOT NULL
        GROUP BY u.id, u.phone, u.name, u.institution_id, i.name, u.password
        ORDER BY reg_count ASC
        LIMIT 10
    """)
    rows = c.fetchall()
conn.close()
print(json.dumps(rows, ensure_ascii=False, indent=2))
