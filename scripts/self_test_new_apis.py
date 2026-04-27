import sys, io, json, urllib.request, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'http://localhost:6031'

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {}

def ok(label, cond, detail=''):
    mark = 'PASS' if cond else 'FAIL'
    print(f'  [{mark}] {label}  {detail}')

# ── 登录 ──────────────────────────────────────────────────────────────────────
print('\n=== 1. 登录 (ops) ===')
code, res = req('POST', '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
confirmed = res['data'].get('noticeConfirmed')
token = res['data']['token']
ok('登录成功 200', code == 200)
ok('noticeConfirmed 字段存在', 'noticeConfirmed' in res['data'], str(confirmed))

# ── 须知确认 ──────────────────────────────────────────────────────────────────
print('\n=== 2. 须知确认 ===')
if not confirmed:
    code, res = req('POST', '/api/auth/notice/confirm', token=token)
    ok('POST /api/auth/notice/confirm 200', code == 200, str(res))
    # 再次登录应为true
    code2, res2 = req('POST', '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
    ok('确认后 noticeConfirmed=true', res2['data'].get('noticeConfirmed') == True)
    token = res2['data']['token']
else:
    print('  (已确认过，跳过首次确认测试)')

# ── self-change-password ──────────────────────────────────────────────────────
print('\n=== 3. self-change-password ===')
# 无token → 401
code, _ = req('POST', '/api/auth/self-change-password',
              {'oldPassword': 'x', 'newPassword': 'y123456', 'confirmPassword': 'y123456'})
ok('无token → 401', code == 401)

# 旧密码错误 → fail
code, res = req('POST', '/api/auth/self-change-password',
                {'oldPassword': 'wrongpwd', 'newPassword': 'newpwd123', 'confirmPassword': 'newpwd123'},
                token=token)
ok('旧密码错误 → fail', res.get('success') == False, res.get('message', ''))

# 两次新密码不一致 → fail
code, res = req('POST', '/api/auth/self-change-password',
                {'oldPassword': 'ops2026', 'newPassword': 'newpwd123', 'confirmPassword': 'diff123'},
                token=token)
ok('两次密码不一致 → fail', res.get('success') == False, res.get('message', ''))

# ── 规避原因字典 ───────────────────────────────────────────────────────────────
print('\n=== 4. 规避原因字典 recuse_reason ===')
code, res = req('GET', '/api/dictionaries/recuse_reason')
items = res.get('data', [])
ok('GET /api/dictionaries/recuse_reason 200', code == 200)
ok('包含4条默认数据', len(items) >= 4, str(len(items)))
codes = [i['code'] for i in items]
ok('包含 GUIDED_PROJECT', 'GUIDED_PROJECT' in codes)
ok('包含 OTHER', 'OTHER' in codes)
for it in items:
    print(f'    {it["code"]:25s} {it["label"]}')

# ── 评审任务统计接口 ───────────────────────────────────────────────────────────
print('\n=== 5. GET /api/reviews/my-tasks/stats ===')
# 用一个评委账号测
rtoken = token
code, res = req('GET', '/api/reviews/my-tasks/stats', token=rtoken)
ok('stats接口可访问', code == 200)
data = res.get('data', {})
ok('返回total字段', 'total' in data, str(data))

# ── 我的任务列表（验证total字段）─────────────────────────────────────────────
print('\n=== 6. GET /api/reviews/my-tasks (验证total字段) ===')
code, res = req('GET', '/api/reviews/my-tasks', token=rtoken)
ok('my-tasks可访问', code == 200)
items2 = res.get('data', [])
ok('返回列表', isinstance(items2, list), f'条数={len(items2)}')
if items2:
    first = items2[0]
    ok('每条有total字段', 'total' in first, str(first.get('total')))

print('\n=== 完成 ===')
