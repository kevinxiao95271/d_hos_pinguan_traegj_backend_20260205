import pymysql, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

for form in ['NON_QCC', 'QFD']:
    print(f"\n===== {form} 示例（各取3个）=====")
    cur.execute("""
        SELECT ua.phone, ua.name, rt.id as task_id,
               r.id as reg_id, r.project_name, r.final_session_code, rt.status
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        JOIN registrations r ON r.id = rt.registration_id
        WHERE rt.stage = 'FINAL'
          AND r.final_score_form = %s
          AND rt.status = 'SCORED'
        LIMIT 3
    """, (form,))
    rows = cur.fetchall()
    for phone, name, task_id, reg_id, proj, sess, status in rows:
        print(f"  专家: {phone} {name}")
        print(f"  项目: {reg_id} {proj}")
        print(f"  场次: {sess}  taskId:{task_id}  状态:{status}")
        print()

conn.close()
