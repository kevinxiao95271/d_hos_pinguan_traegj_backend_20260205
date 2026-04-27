import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'
h = {'Authorization': 'Bearer ' + requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']}

print('=== /api/reviews/summary?competitionId=1&stage=BOOK ===')
r = requests.get(f'{BASE}/api/reviews/summary', params={'competitionId':1,'stage':'BOOK'}, headers=h).json()
print(f'success={r.get("success")} data_count={len(r.get("data") or [])}')
if r.get('data'):
    print(f'  第一条: {json.dumps(r["data"][0], ensure_ascii=False)}')

print()
print('=== /api/reviews/summary?competitionId=1&stage=INTERVIEW ===')
r = requests.get(f'{BASE}/api/reviews/summary', params={'competitionId':1,'stage':'INTERVIEW'}, headers=h).json()
print(f'success={r.get("success")} data_count={len(r.get("data") or [])}')

print()
print('=== /api/admin/reviews/rankings?competitionId=1&stage=BOOK ===')
r = requests.get(f'{BASE}/api/admin/reviews/rankings', params={'competitionId':1,'stage':'BOOK'}, headers=h).json()
d = r.get('data') or []
print(f'返回 {len(d)} 条')

print()
print('=== /api/admin/reviews/interview-summary?competitionId=1 ===')
r = requests.get(f'{BASE}/api/admin/reviews/interview-summary', params={'competitionId':1}, headers=h).json()
print(json.dumps(r, ensure_ascii=False)[:300])

print()
print('=== /api/competitions/1 ===')
r = requests.get(f'{BASE}/api/competitions/1', headers=h).json()
comp = r.get('data', {})
print(f'stage={comp.get("stage")} bookReviewStart={comp.get("bookReviewStart")} bookReviewEnd={comp.get("bookReviewEnd")}')
print(f'interviewStart={comp.get("interviewStart")} interviewEnd={comp.get("interviewEnd")}')
