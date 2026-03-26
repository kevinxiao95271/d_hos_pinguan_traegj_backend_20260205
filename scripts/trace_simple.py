import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'
REG_ID = 1

def call(method, url, token, body=None):
    headers = {'Authorization': 'Bearer ' + token}
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode()
    else:
        data = None
    req = urllib.request.Request(url, data, headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw)
            except:
                return r.status, {'raw_bytes': len(raw), 'ct': r.headers.get('Content-Type','')}
    except urllib.error.HTTPError as e:
        return e.code, {'error': e.read().decode(errors='replace')[:200]}
    except Exception as ex:
        return 0, {'error': str(ex)[:100]}

# 登录
ops = call('POST', BASE+'/api/auth/login-with-password', '',
           {'phone':'13800000005','password':'ops2026'})
ops_token = ops[1]['data']['token']
reset = call('POST', BASE+f'/api/admin/users/28/reset-password', ops_token, {})
pwd = reset[1]['data']['newPassword']
rv_login = call('POST', BASE+'/api/auth/login-with-password', '',
                {'phone':'13886509429','password':pwd})
rv_token = rv_login[1]['data']['token']
print(f'登录成功  pwd={pwd}\n')

# Step 1: 报名详情
print(f'── GET /api/registrations/{REG_ID} (评委身份) ──')
s, b = call('GET', BASE+f'/api/registrations/{REG_ID}', rv_token)
print(f'HTTP {s}')
if s == 200:
    d = b.get('data', {})
    mats = d.get('materials', [])
    print(f'materials 数组长度: {len(mats)}')
    for m in mats:
        print(f'  id={m["id"]}  type={m["type"]}  file={m.get("fileName","?")[:45]}')
        print(f'  downloadUrl字段: {m.get("downloadUrl","(无)")}')
else:
    print(b)

# Step 2: 单独材料列表
print(f'\n── GET /api/materials/registration/{REG_ID} (评委身份) ──')
s2, b2 = call('GET', BASE+f'/api/materials/registration/{REG_ID}', rv_token)
print(f'HTTP {s2}')
if s2 == 200:
    items = b2.get('data', [])
    print(f'返回 {len(items)} 条')
    for m in items:
        print(f'  id={m["id"]}  type={m["type"]}  file={m.get("fileName","?")[:45]}')
else:
    print(b2)

# Step 3: 下载测试
print('\n── 下载测试（评委身份）──')
for mid, mtype, fname in [(82,'EVIDENCE','附件(1).zip'),(79,'REGISTRATION_FORM_DOC','报名表.docx'),(81,'REPORT','报告.pdf')]:
    req = urllib.request.Request(BASE+f'/api/materials/{mid}/download',
                                 headers={'Authorization':'Bearer '+rv_token})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            sz = len(r.read())
            ct = r.headers.get('Content-Type','')
            cd = r.headers.get('Content-Disposition','')
            print(f'  ✅ [{mtype}] id={mid}  HTTP 200  size={sz}b  ct={ct}')
            print(f'     Content-Disposition: {cd[:80]}')
    except urllib.error.HTTPError as e:
        print(f'  ❌ [{mtype}] id={mid}  HTTP {e.code}  {e.read().decode(errors="replace")[:100]}')
    except Exception as ex:
        print(f'  ❌ [{mtype}] id={mid}  {ex}')
