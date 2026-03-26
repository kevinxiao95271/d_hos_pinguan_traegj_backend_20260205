import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

req = urllib.request.Request(BASE + '/api/auth/login-with-password',
    json.dumps({'phone': '13800000005', 'password': 'ops2026'}).encode(),
    {'Content-Type': 'application/json'})
token = json.loads(urllib.request.urlopen(req, timeout=10).read())['data']['token']
print('登录成功')

for stage in ['BOOK', 'INTERVIEW']:
    url = f'{BASE}/api/admin/reviews/score-export?competitionId=1&stage={stage}'
    req2 = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req2, timeout=15) as r:
            content = r.read()
            ct = r.headers.get('Content-Type', '')
            cd = r.headers.get('Content-Disposition', '')
            print(f'\n[{stage}]')
            print(f'  Content-Type       : {ct}')
            print(f'  Content-Disposition: {cd}')
            print(f'  文件大小            : {len(content)} bytes')
            # 保存文件
            fname = f'scripts/export_{stage.lower()}.xlsx'
            with open(fname, 'wb') as f:
                f.write(content)
            print(f'  已保存到            : {fname}')
    except Exception as e:
        print(f'[{stage}] 失败: {e}')
