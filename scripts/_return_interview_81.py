import sys, io, requests, bcrypt, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = 'http://81.71.44.180:6031'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

OPS_PHONE = '13800000005'
OPS_PWD   = 'ops2026'

# 查出所有 SCORED 状态的 INTERVIEW 任务
conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("""
        SELECT rt.id, ua.name, ua.phone
        FROM review_tasks rt
        JOIN user_accounts ua ON ua.id = rt.reviewer_id
        WHERE rt.stage = 'INTERVIEW' AND rt.status = 'SCORED'
        ORDER BY rt.id
    """)
    scored_tasks = cur.fetchall()
conn.close()
print(f'SCORED 面谈任务: {len(scored_tasks)} 条')
for t in scored_tasks:
    print(f'  task_id={t[0]} 评委={t[1]}({t[2]})')

if not scored_tasks:
    print('\n没有需要驳回的任务。')
    sys.exit(0)

# OPS 登录
print(f'\n--- OPS 登录 ({API}) ---')
r = requests.post(f'{API}/api/auth/login-with-password',
    json={'phone': OPS_PHONE, 'password': OPS_PWD}, timeout=15)
body = r.json()
if not body.get('success'):
    print(f'登录失败: {body}')
    sys.exit(1)
token = body['data']['token']
print(f'登录成功')

# 批量驳回
headers = {'Authorization': f'Bearer {token}'}
print(f'\n--- 批量驳回 {len(scored_tasks)} 条 ---')
ok, fail = 0, 0
for task_id, name, phone in scored_tasks:
    resp = requests.post(f'{API}/api/admin/reviews/interview-scores/return',
        params={'reviewTaskId': task_id}, headers=headers, timeout=15).json()
    if resp.get('success'):
        print(f'  ✅ task_id={task_id} ({name})')
        ok += 1
    else:
        print(f'  ❌ task_id={task_id} ({name}): {resp.get("message")}')
        fail += 1

print(f'\n=== 成功 {ok} 条，失败 {fail} 条 ===')
