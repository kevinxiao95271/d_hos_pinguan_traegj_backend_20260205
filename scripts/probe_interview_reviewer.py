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

# 找到那个项目 "三门县人民医院" + 进阶组的 registrationId
# 用 score-list 来找
r1 = get('/api/admin/reviews/score-list?competitionId=1&stage=INTERVIEW', token)
items = r1.get('data') or []

# 找三门县人民医院的项目
target = None
for item in items:
    if '三门' in (item.get('institutionName') or ''):
        target = item
        print(f"找到: reg={item['registrationId']} project={item.get('projectName','')[:40]}")
        print(f"  institutionName={item.get('institutionName')}")
        print(f"  groupCode={item.get('groupCode')} avgTotal={item.get('avgTotal')}")
        print(f"  reviewerScores:")
        for rs in (item.get('reviewerScores') or []):
            print(f"    reviewerId={rs.get('reviewerId')} name={rs.get('reviewerName')} status={rs.get('status')}")
            print(f"    topic={rs.get('topic')} process={rs.get('process')} op={rs.get('interviewOperation')} result={rs.get('result')} total={rs.get('total')}")

if not target:
    print("未找到三门县，列出所有项目:")
    for item in items[:5]:
        print(f"  reg={item['registrationId']} inst={item.get('institutionName')} group={item.get('groupCode')}")

# 也测试 interview-summary 接口
print("\n=== interview-summary 中的同一项目 ===")
r2 = get('/api/admin/reviews/interview-summary?competitionId=1', token)
for item in (r2.get('data') or []):
    if '三门' in (item.get('institutionName') or ''):
        print(json.dumps(item, ensure_ascii=False, indent=2))
