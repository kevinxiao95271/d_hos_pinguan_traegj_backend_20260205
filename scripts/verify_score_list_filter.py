import requests

BASE = 'http://localhost:6031'
login_resp = requests.post(f'{BASE}/api/auth/login-with-password', json={'phone': '13800000005', 'password': 'ops2026'})
token = login_resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
s = requests.Session()
s.headers.update(headers)

for stage in ['BOOK', 'INTERVIEW']:
    r = s.get('http://localhost:6031/api/admin/reviews/score-list',
              params={'competitionId': 1, 'stage': stage})
    data = r.json().get('data', [])
    print(f'\n=== {stage} 得分列表，项目数: {len(data)} ===')
    for item in data[:5]:
        scores = item.get('reviewerScores', [])
        statuses = [rs['status'] for rs in scores]
        print(f'  {item["projectName"][:20]:20s} | totalReviewers={item["totalReviewers"]} scoredCount={item["scoredCount"]} | 评委状态={statuses}')
        for rs in scores:
            total = rs.get('total', 'N/A')
            print(f'      -> {rs["reviewerName"]} status={rs["status"]} total={total}')

print('\n验证完毕：列表中应只含 SCORED 状态评委行，无 PENDING/RETURNED')
