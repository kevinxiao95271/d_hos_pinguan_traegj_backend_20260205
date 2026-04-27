import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031'

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

for scope_mode in [
    ('PER_GROUP', None, None),
    ('UNIFIED', 'COUNT', 6),
    ('UNIFIED', 'RATIO', 0.4),
]:
    scope, umode, uval = scope_mode
    if scope == 'PER_GROUP':
        requests.put(f'{BASE}/api/admin/shortlist/book-scope', json={'scope': 'PER_GROUP'}, headers=h)
    else:
        requests.put(f'{BASE}/api/admin/shortlist/book-scope',
            json={'scope':'UNIFIED','unifiedMode':umode,'unifiedValue':uval}, headers=h)

    r = requests.get(f'{BASE}/api/admin/shortlist',
        params={'competitionId':1,'stage':'BOOK'}, headers=h).json()['data']

    print(f'\n{"="*60}')
    print(f'模式: {scope}' + (f'  {umode}={uval}' if umode else ''))
    print(f'  stage={r["stage"]}  snapshotAt={r["snapshotAt"]}')
    print(f'  totalCount={r["totalCount"]}  shortlistCount={r["shortlistCount"]}  ratio={r["shortlistRatio"]}')
    if r.get('scope'):
        print(f'  scope={r["scope"]}', end='')
        if r.get('unifiedMode'):
            print(f'  unifiedMode={r["unifiedMode"]}  unifiedValue={r["unifiedValue"]}  unifiedCutoff={r["unifiedCutoff"]}', end='')
        print()
    if r.get('groupConfigs'):
        print('  groupConfigs:')
        for gc in r['groupConfigs']:
            print(f'    [{gc["groupType"]}] mode={gc["mode"]} value={gc["value"]} '
                  f'cutoff={gc["cutoff"]} total={gc["total"]} withinLineCount={gc["withinLineCount"]}')

# 恢复 PER_GROUP
requests.put(f'{BASE}/api/admin/shortlist/book-scope', json={'scope': 'PER_GROUP'}, headers=h)
print('\n（已恢复 PER_GROUP 模式）')
