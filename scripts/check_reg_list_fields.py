import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
token = login['data']['token']

resp = get(BASE + '/api/admin/registrations/filter?competitionId=1&page=1&size=5', token)
items = resp['data']['items']
print('报名列表接口返回字段（前5条）:\n')
for item in items[:3]:
    print(json.dumps(item, ensure_ascii=False, indent=2, default=str))
    print()
