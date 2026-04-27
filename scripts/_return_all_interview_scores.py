import sys, io, requests, bcrypt, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = 'http://localhost:6031'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

OPS_PHONE = '13800000005'
OPS_PWD   = 'OpsTest123'

# 查出所有 SCORED 状态的 INTERVIEW 任务
conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("""
        SELECT rt.id, ua.name
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        WHERE rt.stage = 'INTERVIEW' AND rt.status = 'SCORED'
        ORDER BY rt.id
    """)
    scored_tasks = cur.fetchall()
conn.close()
print(f'SCORED 面谈任务: {len(scored_tasks)} 条')

# OPS 登录
r = requests.post(f'{API}/api/auth/login-with-password',
    json={'phone': OPS_PHONE, 'password': OPS_PWD}, timeout=15)
token = r.json()['data']['token']
print(f'OPS 登录成功')

# 批量驳回
headers = {'Authorization': f'Bearer {token}'}
ok, fail = 0, 0
for task_id, name in scored_tasks:
    resp = requests.post(f'{API}/api/admin/reviews/interview-scores/return',
        params={'reviewTaskId': task_id}, headers=headers, timeout=15).json()
    if resp.get('success'):
        print(f'  ✅ task_id={task_id} ({name})')
        ok += 1
    else:
        print(f'  ❌ task_id={task_id} ({name}): {resp.get("message")}')
        fail += 1

print(f'\n=== 成功 {ok} 条，失败 {fail} 条 ===')
