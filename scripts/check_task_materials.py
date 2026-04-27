import pymysql
from collections import defaultdict

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
    SELECT
        rt.stage,
        rv.name  AS reviewer_name,
        rv.phone AS reviewer_phone,
        r.id     AS reg_id,
        r.project_name,
        r.group_type,
        COUNT(mf.id)                                   AS material_count,
        MAX(CASE WHEN mf.id IS NOT NULL THEN 1 ELSE 0 END) AS has_material
    FROM review_tasks rt
    JOIN user_accounts rv ON rt.reviewer_id = rv.id
    JOIN registrations  r  ON rt.registration_id = r.id
    LEFT JOIN material_files mf ON mf.registration_id = r.id
    WHERE rv.phone IN ('13886509429','13887790508','13800002569')
      AND rt.stage IN ('BOOK','INTERVIEW')
    GROUP BY rt.id, rt.stage, rv.name, rv.phone, r.id, r.project_name, r.group_type
    ORDER BY rv.phone, rt.stage, r.id
""")
rows = cur.fetchall()

summary = defaultdict(lambda: {'BOOK': [], 'INTERVIEW': []})
for row in rows:
    k = f"{row['reviewer_name']}({row['reviewer_phone']})"
    summary[k][row['stage']].append(row)

total_no_mat = 0
for reviewer, data in summary.items():
    print(f'\n== {reviewer} ==')
    for stage_label, stage_key in [('书审', 'BOOK'), ('面谈', 'INTERVIEW')]:
        tasks = data[stage_key]
        if not tasks:
            continue
        print(f'  [{stage_label}] {len(tasks)} 条:')
        for t in tasks:
            mark = '[有材料]' if t['has_material'] else '[无材料]'
            print(f"    reg_id={t['reg_id']} {mark}({t['material_count']}个) {t['project_name'][:25]}")
            if not t['has_material']:
                total_no_mat += 1

print(f'\n无材料项目总计: {total_no_mat} 条')
cur.close()
conn.close()
