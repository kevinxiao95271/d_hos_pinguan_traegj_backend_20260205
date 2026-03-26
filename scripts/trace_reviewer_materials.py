import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'
TASK_ID = 314
REG_ID = 1

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_json(url, token=None):
    headers = {}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {'error': e.read().decode(errors='replace')}
    except Exception as e:
        return 0, {'error': str(e)}

def get_raw(url, token):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}, 0

# ── 登录 ──
ops_login = post(BASE + '/api/auth/login-with-password', {'phone': '13800000005', 'password': 'ops2026'})
ops_token = ops_login['data']['token']
reset = post(BASE + '/api/admin/users/28/reset-password', {}, ops_token)
pwd = reset['data']['newPassword']
login = post(BASE + '/api/auth/login-with-password', {'phone': '13886509429', 'password': pwd})
rv_token = login['data']['token']
print(f'朱研究员登录成功  phone=13886509429  pwd={pwd}\n')
print('=' * 65)
print(f'  任务页面: task_id={TASK_ID}  reg_id={REG_ID}  stage=BOOK')
print('=' * 65)

# ── Step 1: 前端打开页面，先拉任务详情 ──
print('\n【Step 1】拉取评审任务详情')
urls_task = [
    f'/api/reviews/tasks/{TASK_ID}',
    f'/api/reviews/my-tasks/{TASK_ID}',
]
task_data = None
for u in urls_task:
    status, body = get_json(BASE + u, rv_token)
    print(f'  GET {u}  →  HTTP {status}')
    if status == 200 and body.get('data'):
        task_data = body['data']
        print(f'    task.id={task_data.get("id")} status={task_data.get("status")} stage={task_data.get("stage")}')
        break
    else:
        print(f'    {str(body)[:80]}')

# ── Step 2: 拉取报名详情（含材料）──
print(f'\n【Step 2】拉取报名详情  reg_id={REG_ID}')
reg_urls = [
    f'/api/registrations/{REG_ID}',
    f'/api/registrations/{REG_ID}/detail',
]
reg_data = None
for u in reg_urls:
    status, body = get_json(BASE + u, rv_token)
    print(f'  GET {u}  →  HTTP {status}')
    if status == 200 and body.get('data'):
        reg_data = body['data']
        mats = reg_data.get('materials', [])
        print(f'    materials 数组长度: {len(mats)}')
        for m in mats:
            print(f'    → id={m.get("id")}  type={m.get("type")}  file={m.get("fileName","?")[:40]}')
            print(f'       downloadUrl={m.get("downloadUrl","(无此字段)")}')
        break
    else:
        print(f'    {str(body)[:120]}')

# ── Step 3: 单独拉材料列表接口 ──
print(f'\n【Step 3】单独材料列表接口  reg_id={REG_ID}')
mat_urls = [
    f'/api/materials/registration/{REG_ID}',
    f'/api/registrations/{REG_ID}/materials',
]
materials = []
for u in mat_urls:
    status, body = get_json(BASE + u, rv_token)
    print(f'  GET {u}  →  HTTP {status}')
    if status == 200:
        items = body.get('data', [])
        if isinstance(items, list):
            materials = items
            print(f'    返回 {len(items)} 条材料')
            for m in items:
                print(f'    → id={m.get("id")}  type={m.get("type")}  file={m.get("fileName","?")[:40]}')
        else:
            print(f'    {str(body)[:120]}')
        break
    else:
        print(f'    {str(body)[:120]}')

# ── Step 4: 逐个测试下载 ──
all_mats = materials or (reg_data.get('materials', []) if reg_data else [])
print(f'\n【Step 4】下载测试（共 {len(all_mats)} 个附件）')
for m in all_mats:
    mid = m.get('id')
    mtype = m.get('type', '')
    fname = m.get('fileName', '?')
    # 下载接口
    dl_url = f'/api/materials/{mid}/download'
    status, headers, size = get_raw(BASE + dl_url, rv_token)
    ct = headers.get('Content-Type', '')
    cd = headers.get('Content-Disposition', '')
    ok = '✅' if status == 200 else '❌'
    print(f'\n  {ok} [{mtype}] id={mid}  {fname[:35]}')
    print(f'     GET {dl_url}  →  HTTP {status}')
    if status == 200:
        print(f'     Content-Type: {ct}')
        print(f'     Content-Disposition: {cd[:80]}')
        print(f'     文件大小: {size} bytes（前512字节）')
    else:
        print(f'     失败原因: HTTP {status}')

print('\n' + '=' * 65)
print('  前端对接完整流程总结')
print('=' * 65)
print(f'''
评委打开打分页面时，前端需调用：

1. 登录获取 token
   POST /api/auth/login-with-password
   Body: {{"phone":"13886509429","password":"{pwd}"}}

2. 获取报名详情（含 materials 数组）
   GET /api/registrations/{REG_ID}
   Authorization: Bearer {{token}}
   → 返回 data.materials[]，每项含 id / type / fileName

3. 遍历 materials，渲染下载按钮
   EVIDENCE 类型可能有多条，需 filter 不能 find：
   const evidenceList = materials.filter(m => m.type === 'EVIDENCE')

4. 点击下载时：
   GET /api/materials/{{id}}/download
   Authorization: Bearer {{token}}
   → 触发 blob 下载，注意 filename 从 Content-Disposition 解析
''')
