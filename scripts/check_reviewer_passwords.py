import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://localhost:6031'
test_phones = ['13800002569', '13811185687', '13886509429', '13887790508']
# 常见测试密码
candidates = ['reviewer2026', 'abc123456', '123456', 'pinguan2026', 'test123456']

def post(url, data):
    req = urllib.request.Request(url, json.dumps(data).encode(), {'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

print("尝试常见密码登录评委账号...\n")
found = {}
for phone in test_phones:
    for pwd in candidates:
        resp = post(BASE + '/api/auth/login-with-password', {'phone': phone, 'password': pwd})
        if resp and resp.get('data') and resp['data'].get('token'):
            found[phone] = pwd
            print(f"  {phone}  密码: {pwd}  ✅")
            break
    else:
        print(f"  {phone}  常见密码均不对 ❌")
