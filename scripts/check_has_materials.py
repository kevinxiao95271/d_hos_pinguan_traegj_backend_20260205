import pymysql
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('''
    SELECT r.id, r.project_name, r.group_type, r.group_code, r.status,
           COUNT(mf.id) AS mat_cnt
    FROM registrations r
    JOIN material_files mf ON mf.registration_id = r.id
    WHERE r.competition_id = 1
    GROUP BY r.id
    ORDER BY mat_cnt DESC
    LIMIT 15
''')
rows = cur.fetchall()
print(f'有材料的项目: {len(rows)} 条')
for r in rows:
    print(f"  id={r['id']} mat={r['mat_cnt']} status={r['status']} "
          f"groupType={r['group_type']} groupCode={r['group_code']} "
          f"{r['project_name'][:30]}")

if not rows:
    # 查 material_files 表总量
    cur.execute('SELECT COUNT(*) AS cnt FROM material_files')
    total = cur.fetchone()['cnt']
    print(f'material_files 表共 {total} 条记录')

cur.close()
conn.close()
