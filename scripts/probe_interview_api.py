import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

def get(path, token):
    req = urllib.request.Request(f'{BASE}{path}',
        headers={'Authorization': f'Bearer {token}'})
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

r = post('/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = r['data']['token']
print(f"登录成功 role={r['data']['role']}\n")

# 1. score-list INTERVIEW
r1 = get('/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', token)
items = r1.get('data') or []
print(f"=== score-list INTERVIEW: {len(items)} 条 ===")
if items:
    item = items[0]
    print(f"  首条: reg={item.get('registrationId')} {item.get('projectName','')[:30]}")
    for rs in (item.get('reviewerScores') or [])[:2]:
        print(f"  评委={rs.get('reviewerName')} status={rs.get('status')} total={rs.get('total')}")
        print(f"  topic={rs.get('topic')} process={rs.get('process')} interviewOperation={rs.get('interviewOperation')} result={rs.get('result')}")

# 2. review-details 单条（用有面谈数据的那条）
rid = items[0].get('registrationId') if items else None
if rid:
    r2 = get(f'/api/registrations/{rid}/review-details', token)
    print(f"\n=== /registrations/{rid}/review-details ===")
    print(json.dumps(r2.get('data'), ensure_ascii=False, indent=2)[:3000])

# 3. interview-summary
r3 = get('/api/admin/reviews/interview-summary?competitionId=1', token)
print(f"\n=== interview-summary: {len(r3.get('data') or [])} 条 ===")
if r3.get('data'):
    print(json.dumps(r3['data'][0], ensure_ascii=False, indent=2)[:800])
