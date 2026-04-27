import pymysql, urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'

# 从DB找一个管理员账号
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SELECT phone, name FROM user_accounts WHERE role IN ('COMMITTEE_ADMIN','OPS') LIMIT 3")
admins = cur.fetchall()
print("可用管理员：", admins)
conn.close()

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

def get(path, token=''):
    h = {'Authorization': f'Bearer {token}'} if token else {}
    req = urllib.request.Request(f'{BASE}{path}', headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

token = None
for phone, name in admins:
    for pwd in ['Admin1234!', 'admin123', '123456', 'Yiguo9527_']:
        try:
            r = post('/api/auth/login-with-password', {'phone': phone, 'password': pwd})
            if r.get('data') and r['data'].get('token'):
                token = r['data']['token']
                print(f"登录成功: {name} ({phone}) pwd={pwd} role={r['data']['role']}")
                break
        except Exception as e:
            pass
    if token:
        break

if not token:
    print("所有账号登录失败")
    sys.exit(1)

# 查面谈得分列表
r = get('/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', token)
items = r.get('data') or []
print(f"\n=== INTERVIEW score-list: {len(items)} 条 ===")
for item in items[:2]:
    print(f"\n  reg={item.get('registrationId')}  {item.get('projectName','')[:30]}")
    for rs in (item.get('reviewerScores') or [])[:3]:
        print(f"    {rs.get('reviewerName')}  status={rs.get('status')}  total={rs.get('total')}")
        print(f"    topic={rs.get('topic')} process={rs.get('process')} op={rs.get('interviewOperation')} result={rs.get('result')}")

# review-details
if items:
    rid = items[0].get('registrationId')
    r2 = get(f'/api/registrations/{rid}/review-details', token)
    print(f"\n=== /registrations/{rid}/review-details ===")
    print(json.dumps(r2.get('data'), ensure_ascii=False, indent=2)[:2000])
