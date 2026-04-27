import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

print('=== scoring_snapshots 快照分布 ===')
cur.execute("""
    SELECT stage, group_type, COUNT(*) total, MIN(calculated_at) calc_at
    FROM scoring_snapshots
    GROUP BY stage, group_type
    ORDER BY stage, group_type
""")
for r in cur.fetchall():
    print(f'  stage={r[0]:<12} group_type={r[1]:<15} count={r[2]}  calculated_at={r[3]}')

print('\n=== 入围配置（system_settings） ===')
cur.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE 'shortlist%'")
for r in cur.fetchall():
    print(f'  {r[0]:<45} = {r[1]}')

print('\n=== BOOK 阶段快照按 group_type 明细（前20） ===')
cur.execute("""
    SELECT ss.group_type, ss.group_code, ss.registration_id, ss.irank,
           ss.adjusted_score, r.project_name
    FROM scoring_snapshots ss
    JOIN registrations r ON ss.registration_id = r.id
    WHERE ss.stage='BOOK'
    ORDER BY ss.group_type, ss.irank
    LIMIT 20
""")
cur_group = None
for row in cur.fetchall():
    if row[0] != cur_group:
        cur_group = row[0]
        print(f'\n  [{cur_group}]')
    adj = f'{row[4]:.3f}' if row[4] else 'N/A'
    print(f'    irank={row[3]}  reg_id={row[2]}  adj={adj}  {str(row[5])[:30] if row[5] else ""}')

conn.close()
