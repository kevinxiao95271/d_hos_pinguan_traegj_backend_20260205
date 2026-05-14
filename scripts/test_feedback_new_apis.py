"""
自测脚本：验证两个新接口
1. GET  /api/admin/reviews/project-feedback/export  （导出 Excel）
2. PUT  /api/admin/reviews/project-feedback/batch   （批量保存草稿）
"""
import sys, io, json, urllib.request, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'http://81.71.44.180:6031'

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            ct = resp.headers.get('Content-Type', '')
            raw = resp.read()
            if 'json' in ct:
                return resp.status, json.loads(raw), ct
            return resp.status, raw, ct
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), ''
        except Exception:
            return e.code, raw, ''

def ok(label, cond, detail=''):
    mark = 'PASS' if cond else 'FAIL'
    print(f'  [{mark}] {label}  {detail}')

# ── 1. 登录获取 token ────────────────────────────────────────────
print('\n=== 1. 登录 (ops) ===')
code, res, _ = req('POST', '/api/auth/login-with-password',
                   {'phone': '13800000005', 'password': 'ops2026'})
ok('登录 200', code == 200)
token = res['data']['token']
print(f'  token 获取成功（前20位）: {token[:20]}...')

# ── 2. 查询 competitionId ──────────────────────────────────────
print('\n=== 2. 确定 competitionId ===')
competition_id = 21
print(f'  使用 competitionId={competition_id}')

# ── 3. 先查项目意见列表，取前几条 registrationId ────────────────
print('\n=== 3. 查询项目意见列表 ===')
code, res, _ = req('GET',
    f'/api/admin/reviews/project-feedback?competitionId={competition_id}&stage=BOOK',
    token=token)
ok('GET project-feedback 200', code == 200)
items = res.get('data', []) if isinstance(res, dict) else []
ok('有数据返回', len(items) > 0, f'共 {len(items)} 条')
sample_ids = [it['registrationId'] for it in items[:3]]
print(f'  样本 registrationId: {sample_ids}')

if not sample_ids:
    print('  [SKIP] 无可用样本数据，跳过批量保存写入测试（仍测试校验逻辑）')

# ── 4. 测试批量保存接口 ──────────────────────────────────────────
print('\n=== 4. PUT /project-feedback/batch ===')

# 4a. 正常批量保存（仅在有样本时执行写入）
if sample_ids:
    batch_body = {
        'items': [
            {'registrationId': rid, 'highlight': f'自测亮点-{rid}', 'weakness': f'自测不足-{rid}'}
            for rid in sample_ids
        ]
    }
    code, res, _ = req('PUT',
        f'/api/admin/reviews/project-feedback/batch?stage=BOOK',
        body=batch_body, token=token)
    ok(f'批量保存 {len(sample_ids)} 条 → 200', code == 200)
    saved = res.get('data', []) if isinstance(res, dict) else []
    ok('返回保存结果列表', isinstance(saved, list) and len(saved) == len(sample_ids),
       f'返回 {len(saved)} 条')
    if saved:
        first = saved[0]
        ok('editedHighlight 已写入', str(first.get('editedHighlight', '')).startswith('自测亮点'),
           first.get('editedHighlight', ''))
        ok('editedWeakness 已写入', str(first.get('editedWeakness', '')).startswith('自测不足'),
           first.get('editedWeakness', ''))
else:
    print('  [SKIP] 无样本，跳过写入验证')

# 4b. 超出 200 条限制
print('  -- 测试超出上限 --')
big_body = {'items': [{'registrationId': 1, 'highlight': 'x', 'weakness': 'y'}] * 201}
code, res, _ = req('PUT',
    f'/api/admin/reviews/project-feedback/batch?stage=BOOK',
    body=big_body, token=token)
ok('201 条 → 400', code == 400, str(code))

# 4c. 无 token → 401
dummy_body = {'items': [{'registrationId': 1, 'highlight': 'x', 'weakness': 'y'}]}
code, _, _ = req('PUT',
    f'/api/admin/reviews/project-feedback/batch?stage=BOOK',
    body=dummy_body)
ok('无 token → 401', code == 401, str(code))

# 4d. 清理：把刚才写的草稿清空
if sample_ids:
    clean_body = {
        'items': [
            {'registrationId': rid, 'highlight': None, 'weakness': None}
            for rid in sample_ids
        ]
    }
    code, res, _ = req('PUT',
        f'/api/admin/reviews/project-feedback/batch?stage=BOOK',
        body=clean_body, token=token)
    ok('清理测试数据（置空草稿）→ 200', code == 200)

# ── 5. 测试导出接口 ──────────────────────────────────────────────
print('\n=== 5. GET /project-feedback/export ===')

code, body, ct = req('GET',
    f'/api/admin/reviews/project-feedback/export?competitionId={competition_id}&stage=BOOK',
    token=token)
ok('export 200', code == 200, str(code))
ok('Content-Type 是 xlsx',
   'spreadsheetml' in ct or 'octet-stream' in ct, ct)
ok('响应体非空（有文件内容）', isinstance(body, bytes) and len(body) > 1000,
   f'{len(body) if isinstance(body, bytes) else "?"} bytes')

# 5b. 带筛选参数
code, body2, ct2 = req('GET',
    f'/api/admin/reviews/project-feedback/export?competitionId={competition_id}&stage=BOOK&published=false',
    token=token)
ok('带 published=false 筛选 export 200', code == 200)

# 5c. 无 token → 401
code, _, _ = req('GET',
    f'/api/admin/reviews/project-feedback/export?competitionId={competition_id}&stage=BOOK')
ok('无 token → 401', code == 401, str(code))

print('\n=== 自测完成 ===')
