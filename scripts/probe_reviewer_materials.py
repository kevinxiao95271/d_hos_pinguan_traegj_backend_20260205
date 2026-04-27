import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_raw(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), r.read(512)
    except urllib.error.HTTPError as e:
        return e.code, {}, e.read(512)
    except Exception as e:
        return 0, {}, str(e).encode()

def get_json(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'msg': e.read().decode(errors='replace')}
    except Exception as e:
        return {'error': str(e)}

# ── 以朱研究员身份登录 ──
ops_login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
ops_token = ops_login['data']['token']
reset = post(BASE + '/api/admin/users/28/reset-password', {}, ops_token)
pwd = reset['data']['newPassword']
login = post(BASE + '/api/auth/login-with-password', {'phone': '13886509429', 'password': pwd})
rv_token = login['data']['token']
print(f'朱研究员登录成功 (密码已重置为: {pwd})\n')

# ── 拿朱研究员的任务，找关联的报名 ──
tasks_resp = get_json(BASE + '/api/reviews/my-tasks', rv_token)
tasks = tasks_resp.get('data', [])
reg_ids = list({t.get('registrationId') for t in tasks if t.get('registrationId')})
print(f'关联报名ID: {reg_ids[:5]}\n')

# ── 对每个报名查材料 ──
all_materials = []
for reg_id in reg_ids[:3]:
    resp = get_json(BASE + f'/api/registrations/{reg_id}', rv_token)
    if resp.get('error'):
        print(f'reg_id={reg_id} 详情接口: {resp}')
        continue
    mats = resp.get('data', {}).get('materials', [])
    if not mats:
        # 尝试直接拉材料列表
        mat_resp = get_json(BASE + f'/api/materials/registration/{reg_id}', rv_token)
        mats = mat_resp.get('data', []) if mat_resp and not mat_resp.get('error') else []
    print(f'reg_id={reg_id}  材料数: {len(mats)}')
    for m in mats:
        print(f'  id={m.get("id")}  type={m.get("type")}  file={m.get("fileName","?")}')
        all_materials.append(m)

# ── 按类型分类测试下载 ──
print('\n=== 下载测试 ===')
tested_types = set()
for mat in all_materials:
    t = mat.get('type','')
    mid = mat.get('id')
    if not mid or t in tested_types:
        continue
    tested_types.add(t)

    # 方式1: /api/materials/{id}/download
    url1 = BASE + f'/api/materials/{mid}/download'
    status1, headers1, body1 = get_raw(url1, rv_token)
    ct1 = headers1.get('Content-Type','')
    cd1 = headers1.get('Content-Disposition','')
    print(f'\n  [{t}] id={mid}  文件={mat.get("fileName","")[:30]}')
    print(f'  GET {url1}')
    print(f'  → HTTP {status1}  Content-Type={ct1[:50]}')
    if status1 == 200:
        print(f'    Content-Disposition={cd1}  前512字节长度={len(body1)}  ✅ 可下载')
    else:
        print(f'    响应体: {body1[:200].decode(errors="replace")}  ❌ 失败')

    # 方式2: /api/materials/{id}/preview (如果存在)
    url2 = BASE + f'/api/materials/{mid}/preview'
    status2, headers2, body2 = get_raw(url2, rv_token)
    if status2 != 404:
        print(f'  GET {url2} → HTTP {status2}  Content-Type={headers2.get("Content-Type","")}')
