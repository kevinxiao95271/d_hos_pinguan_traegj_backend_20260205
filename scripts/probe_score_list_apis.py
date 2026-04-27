import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'
h = {'Authorization': 'Bearer ' + requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']}

# ── 1. 现有书审汇总接口 ──────────────────────────────────
print('='*65)
print('【现有】GET /api/reviews/summary?competitionId=1&stage=BOOK')
r = requests.get(f'{BASE}/api/reviews/summary',
    params={'competitionId':1,'stage':'BOOK'}, headers=h).json()
items = r.get('data') or []
print(f'返回 {len(items)} 条，第一条完整数据：')
if items:
    print(json.dumps(items[0], ensure_ascii=False, indent=2))
print()
print('>>> 有的字段:', list(items[0].keys()) if items else '无')
print('>>> 缺少字段: 评委姓名、分值细项(plan/problem/action...)、机构等级、分组代码(groupCode)')

# ── 2. 现有面谈汇总接口 ──────────────────────────────────
print()
print('='*65)
print('【现有】GET /api/reviews/summary?competitionId=1&stage=INTERVIEW')
r = requests.get(f'{BASE}/api/reviews/summary',
    params={'competitionId':1,'stage':'INTERVIEW'}, headers=h).json()
items = r.get('data') or []
print(f'返回 {len(items)} 条，第一条：')
if items:
    print(json.dumps(items[0], ensure_ascii=False, indent=2))

# ── 3. 已有的 interview-summary（看字段是否更丰富）──────────
print()
print('='*65)
print('【现有】GET /api/admin/reviews/interview-summary?competitionId=1')
r = requests.get(f'{BASE}/api/admin/reviews/interview-summary',
    params={'competitionId':1}, headers=h).json()
items = r.get('data') or []
print(f'返回 {len(items)} 条，第一条完整数据：')
if items:
    print(json.dumps(items[0], ensure_ascii=False, indent=2))
print()
print('>>> 有的字段:', list(items[0].keys()) if items else '无')

# ── 4. 后台任务列表（书审，看字段）──────────────────────────
print()
print('='*65)
print('【现有】GET /api/admin/reviews/tasks?competitionId=1&stage=BOOK（前3条）')
r = requests.get(f'{BASE}/api/admin/reviews/tasks',
    params={'competitionId':1,'stage':'BOOK'}, headers=h).json()
items = r.get('data') or []
print(f'返回 {len(items)} 条，第一条：')
if items:
    print(json.dumps(items[0], ensure_ascii=False, indent=2))
