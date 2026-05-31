import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

sql = """
    SELECT ua.name, ua.phone, rt.status, COUNT(rt.id) as cnt
    FROM review_tasks rt
    JOIN user_accounts ua ON ua.id = rt.reviewer_id
    JOIN registrations reg ON reg.id = rt.registration_id
    WHERE rt.stage = 'FINAL' AND reg.final_score_form = %s
    GROUP BY ua.id, ua.name, ua.phone, rt.status
    ORDER BY ua.phone, rt.status
"""

for sf in ['QCC', 'QFD', 'NON_QCC']:
    cur.execute(sql, (sf,))
    rows = cur.fetchall()
    print(f'\n=== {sf} ===')
    # 按账号聚合
    from collections import defaultdict
    by_phone = defaultdict(lambda: {'name':'','statuses':{}})
    for name, phone, status, cnt in rows:
        by_phone[phone]['name'] = name
        by_phone[phone]['statuses'][status] = cnt
    for phone, d in list(by_phone.items())[:4]:
        statuses = ', '.join(f"{k}:{v}" for k,v in d['statuses'].items())
        print(f"  {d['name']}  手机:{phone}  ({statuses})")

conn.close()
