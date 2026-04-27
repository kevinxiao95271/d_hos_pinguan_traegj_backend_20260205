import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

login = post(BASE + '/api/auth/login-with-password', {'phone': '13811185687', 'password': '691659'})
token = login['data']['token']
print(f'刘研究员登录成功 (id=27)\n')

# 尝试不同的任务接口
for url in [
    '/api/reviews/tasks',
    '/api/reviews/tasks?competitionId=1',
    '/api/reviews/my-tasks',
    '/api/reviews/tasks?stage=BOOK',
    '/api/reviews/tasks?stage=INTERVIEW',
]:
    resp = get(BASE + url, token)
    if resp is None:
        print(f'{url} -> 404/无响应')
    else:
        d = resp.get('data')
        code = resp.get('code')
        if isinstance(d, list):
            print(f'{url} -> code={code} 返回{len(d)}条')
            for item in d[:2]:
                print(f'  task_id={item.get("id")} stage={item.get("stage")} status={item.get("status")} reg={item.get("registrationId")}')
        elif isinstance(d, dict):
            print(f'{url} -> code={code} data.keys={list(d.keys())}')
            items = d.get('content', [])
            print(f'  分页: {len(items)}条 total={d.get("totalElements")}')
        else:
            print(f'{url} -> code={code} msg={resp.get("message")}')
