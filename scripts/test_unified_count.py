import requests, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 切换到 UNIFIED + COUNT=6
r = requests.put(f'{BASE}/api/admin/shortlist/book-scope',
    json={'scope':'UNIFIED','unifiedMode':'COUNT','unifiedValue':6}, headers=h).json()
print('设置结果:', r.get('success'))

# 读回确认
cfg = requests.get(f'{BASE}/api/admin/shortlist/book-scope', headers=h).json()['data']
print(f'当前配置: scope={cfg["scope"]} unifiedMode={cfg["unifiedMode"]} unifiedValue={cfg["unifiedValue"]}')

# 验证入围结果
items = requests.get(f'{BASE}/api/admin/shortlist',
    params={'competitionId':1,'stage':'BOOK'}, headers=h).json().get('data',[])

by_gt = defaultdict(list)
for x in items:
    by_gt[x['groupType']].append(x)
for gt, lst in by_gt.items():
    win = [x for x in lst if x['shortlisted']]
    print(f'{gt}: 共{len(lst)}条，入围={len(win)}')

total_win = sum(1 for x in items if x['shortlisted'])
print(f'\n总入围(UNIFIED COUNT=6): {total_win}')

print('\n前6名分布:')
sorted_items = sorted(items, key=lambda x: x.get('adjustedScore') or 0, reverse=True)
for x in sorted_items[:6]:
    gt = x['groupType']
    adj = x['adjustedScore']
    name = str(x['projectName'])[:25]
    print(f'  [{gt}] rank={x["irank"]} adj={adj:.2f} {name}')
