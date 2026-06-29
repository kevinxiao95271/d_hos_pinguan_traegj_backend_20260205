import pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
                       password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 进决赛的参赛者（有 final_session_code）
cur.execute('''
    SELECT ua.id, ua.name, ua.phone, r.final_session_code, r.group_code
    FROM user_accounts ua
    JOIN registrations r ON r.applicant_id = ua.id
    WHERE r.final_session_code IS NOT NULL AND r.final_session_code != ""
    AND ua.role = "CONTESTANT"
    LIMIT 5
''')
print('进决赛的参赛者:')
finals = cur.fetchall()
for row in finals: print(row)

# 未进决赛的参赛者
cur.execute('''
    SELECT ua.id, ua.name, ua.phone, r.group_code
    FROM user_accounts ua
    JOIN registrations r ON r.applicant_id = ua.id
    WHERE (r.final_session_code IS NULL OR r.final_session_code = "")
    AND ua.role = "CONTESTANT"
    LIMIT 5
''')
print('\n未进决赛的参赛者:')
non_finals = cur.fetchall()
for row in non_finals: print(row)

# 重置密码
pwd = 'user123'
h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
h2a = h[:2] + 'a' + h[3:]

all_ids = [r[0] for r in finals] + [r[0] for r in non_finals]
if all_ids:
    placeholders = ','.join(['%s'] * len(all_ids))
    cur.execute(f'UPDATE user_accounts SET password=%s WHERE id IN ({placeholders})', [h2a] + all_ids)
    conn.commit()
    print(f'\n已将 {len(all_ids)} 个账号密码重置为: {pwd}')

cur.close(); conn.close()
