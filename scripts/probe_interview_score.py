import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'

# 先查可用的管理员账号
def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

def get(path, token):
    req = urllib.request.Request(f'{BASE}{path}',
        headers={'Authorization': f'Bearer {token}'})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

# 尝试几个可能的管理员账号
for phone, pwd in [('13800000041','Admin1234!'),('13800000001','Admin1234!'),('admin','Admin1234!')]:
    try:
        r = post('/api/auth/login-with-password', {'phone': phone, 'password': pwd})
        if r.get('data') and r['data'].get('token'):
            token = r['data']['token']
            print(f"登录成功 phone={phone} role={r['data']['role']}")
            break
    except:
        continue
else:
    # 列出所有竞赛，不需要token
    r = get('/api/competitions', '')
    print("未登录，竞赛列表：", r)
    sys.exit(1)

# score-list INTERVIEW
r = get('/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', token)
items = r.get('data') or []
print(f"\n=== score-list INTERVIEW 共 {len(items)} 条 ===")
for item in items[:2]:
    print(f"\n  reg={item.get('registrationId')}  {item.get('projectName', '')[:30]}")
    for rs in (item.get('reviewerScores') or [])[:2]:
        print(f"    {rs.get('reviewerName')}  status={rs.get('status')}  total={rs.get('total')}")
        print(f"    topic={rs.get('topic')} process={rs.get('process')} op={rs.get('interviewOperation')} result={rs.get('result')}")

# review-details 单条
if items:
    rid = items[0].get('registrationId')
    r2 = get(f'/api/registrations/{rid}/review-details', token)
    print(f"\n=== /registrations/{rid}/review-details ===")
    print(json.dumps(r2.get('data'), ensure_ascii=False, indent=2)[:2000])
