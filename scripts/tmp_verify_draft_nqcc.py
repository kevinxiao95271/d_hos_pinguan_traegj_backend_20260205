import requests, pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://81.71.44.180:6039'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
          password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB); cur = conn.cursor()
cur.execute('''
    SELECT rt.id, ua.phone, r.final_score_form
    FROM review_tasks rt
    JOIN user_accounts ua ON ua.id = rt.reviewer_id
    JOIN registrations r ON r.id = rt.registration_id
    WHERE rt.stage = %s AND r.final_score_form = %s
    LIMIT 1
''', ('FINAL', 'NON_QCC'))
row = cur.fetchone()
if not row:
    print('无NON_QCC任务'); sys.exit(1)

task_id, phone, sf = row
cur.execute('DELETE FROM review_scores WHERE review_task_id=%s', (task_id,))
cur.execute('UPDATE review_tasks SET status=%s WHERE id=%s', ('PENDING', task_id))

pwd = 'test456'
h = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
h2a = h[:2] + 'a' + h[3:]
cur.execute('UPDATE user_accounts SET password=%s WHERE phone=%s', (h2a, phone))
conn.commit(); cur.close(); conn.close()

print(f'task_id={task_id}  phone={phone}  scoreForm={sf}')

token = requests.post(BASE+'/api/auth/login-with-password',
                      json={'phone': phone, 'password': pwd}, timeout=10).json().get('data', {}).get('token')
print('登录:', 'OK' if token else 'FAIL')
headers = {'Authorization': 'Bearer ' + token}

# 草稿 - 只传 total=86
r = requests.put(BASE+f'/api/reviews/final/scores/{task_id}/draft',
                 headers=headers, json={'scoreForm': sf, 'total': 86}, timeout=10)
print('草稿保存:', r.status_code, r.json().get('success'))

tasks = requests.get(BASE+'/api/reviews/final/my-tasks', headers=headers, timeout=10).json().get('data', [])
t = next((x for x in tasks if x['taskId'] == task_id), None)
draft = (t or {}).get('draftScore') or {}
print('status:', t.get('status') if t else None)
print('total:', draft.get('total'), ' <- 期望 86.0')
items = [draft.get(k) for k in ['plan','problem','action','success','review','operation','presentation','item8']]
print('分项 sum:', sum(x for x in items if x), ':', items)
