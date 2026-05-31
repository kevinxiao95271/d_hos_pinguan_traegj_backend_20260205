import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute("""
    SELECT r.final_session_date, r.final_session_code, r.final_session_order,
           r.id, r.project_name, i.name as inst_name, r.final_score_form
    FROM registrations r
    LEFT JOIN institutions i ON i.id = r.institution_id
    WHERE r.final_session_code IS NOT NULL
    ORDER BY r.final_session_date ASC, r.final_session_code ASC, ISNULL(r.final_session_order), r.final_session_order ASC
""")
rows = cur.fetchall()
conn.close()

cur_date = None
cur_sess = None
for date, sess, order, reg_id, proj, inst, form in rows:
    if date != cur_date:
        cur_date = date
        cur_sess = None
        print(f"\n{'='*60}")
        print(f"日期: {date}")
        print(f"{'='*60}")
    if sess != cur_sess:
        cur_sess = sess
        print(f"\n  【{sess}】")
    print(f"    {str(order):>3}.  {reg_id}  {(inst or '')[:18]:18s}  {proj[:35]}")
