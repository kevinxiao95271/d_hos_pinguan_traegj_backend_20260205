import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

print('=== 1. 设置时间窗口 + 阶段 ===')
payload = {
    "stage": "BOOK_REVIEW",
    "bookReviewStart": "2026-03-23T00:00:00",
    "bookReviewEnd":   "2026-04-30T23:59:59",
    "interviewStart":  "2026-03-23T00:00:00",
    "interviewEnd":    "2026-04-30T23:59:59"
}
r = requests.put(f'{BASE}/api/competitions/1/config', json=payload, headers=h).json()
comp = r.get('data', {})
print(f'  stage          = {comp.get("stage")}')
print(f'  bookReviewStart= {comp.get("bookReviewStart")}')
print(f'  bookReviewEnd  = {comp.get("bookReviewEnd")}')
print(f'  interviewStart = {comp.get("interviewStart")}')
print(f'  interviewEnd   = {comp.get("interviewEnd")}')

print()
print('=== 2. 验证书审得分 summary ===')
r = requests.get(f'{BASE}/api/reviews/summary', params={'competitionId':1,'stage':'BOOK'}, headers=h).json()
d = r.get('data') or []
print(f'  BOOK summary: {len(d)} 条')
if d:
    print(f'  第一条: {d[0]["projectName"][:25]}  avg={d[0]["avgTotal"]}')

print()
print('=== 3. 验证面谈得分 summary（Bug修复验证）===')
r = requests.get(f'{BASE}/api/reviews/summary', params={'competitionId':1,'stage':'INTERVIEW'}, headers=h).json()
d = r.get('data') or []
print(f'  INTERVIEW summary: {len(d)} 条（修复前为 0）')
if d:
    for item in d:
        print(f'  - {str(item["projectName"])[:30]}  avg={item["avgTotal"]}  count={item["scoresCount"]}')

print()
print('=== 4. 验证面谈排名 ===')
r = requests.get(f'{BASE}/api/admin/reviews/rankings', params={'competitionId':1,'stage':'INTERVIEW'}, headers=h).json()
d = r.get('data') or []
print(f'  INTERVIEW rankings: {len(d)} 条')
