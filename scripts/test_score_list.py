import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'
h = {'Authorization': 'Bearer ' + requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']}

for stage in ['BOOK', 'INTERVIEW']:
    print('='*65)
    print(f'GET /api/admin/reviews/score-list?competitionId=1&stage={stage}')
    r = requests.get(f'{BASE}/api/admin/reviews/score-list',
        params={'competitionId':1,'stage':stage}, headers=h).json()
    items = r.get('data') or []
    print(f'返回 {len(items)} 条，第一条完整数据：')
    if items:
        # 找第一条有打分的
        scored = next((x for x in items if x.get('scoredCount',0) > 0), items[0])
        print(json.dumps(scored, ensure_ascii=False, indent=2))
