"""
测试环境一键配置脚本：
1. 重置管理员密码为 $2a$ 格式
2. 查询有材料的参赛项目
3. 查询可用评委
4. 分配书审/面谈任务
5. 重置指定评委密码并输出
"""
import urllib.request, urllib.error, json, bcrypt, sys

BASE = 'http://localhost:6031'

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def make_hash(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(8)).decode().replace('$2b$', '$2a$')

def post(path, body, token=None): return req('POST', path, body, token)
def get(path, token=None):        return req('GET', path, token=token)
def patch(path, body, token=None):return req('PATCH', path, body, token)

# ── 1. 检查 OPS 账号密码是否可用 ─────────────────────────────────────────────
print('=== 尝试登录 ===')
login = post('/api/auth/login-with-password', {'phone': '13800010001', 'password': 'ops2026'})
print(json.dumps(login, ensure_ascii=False))

if not login.get('success'):
    print('\n>>> 密码不可用，写出重置 SQL，请手动执行后重跑本脚本')
    ops_hash = make_hash('ops2026')
    print(f"\nUPDATE user_accounts SET password='{ops_hash}' WHERE phone='13800010001';\n")
    sys.exit(1)

TOKEN = login['data']['token']
print(f'登录成功，token 前20位: {TOKEN[:20]}...')

# ── 2. 查竞赛列表 ─────────────────────────────────────────────────────────────
print('\n=== 竞赛列表 ===')
comps = get('/api/admin/competitions', TOKEN)
if comps.get('data'):
    for c in comps['data'][:5]:
        print(f"  id={c['id']} name={c.get('name','')} stage={c.get('stage','')}")
    comp_id = comps['data'][0]['id']
    print(f'  >>> 使用 competitionId={comp_id}')
else:
    print(comps)
    sys.exit(1)

# ── 3. 查有材料的参赛项目（SUBMITTED/APPROVED 状态）────────────────────────
print('\n=== 有材料的参赛项目（前15条） ===')
regs = get(f'/api/admin/registrations/filter?competitionId={comp_id}&page=1&size=15', TOKEN)
items = regs.get('data', {}).get('content', [])
reg_ids = []
for item in items[:15]:
    rid = item.get('registrationId') or item.get('id')
    pname = item.get('projectName', '')[:20]
    gc = item.get('groupCode', '-')
    gt = item.get('groupType', '-')
    has_mat = item.get('hasMaterials') or item.get('materialCount', 0) > 0
    print(f"  id={rid} groupType={gt} groupCode={gc} project={pname} hasMat={has_mat}")
    reg_ids.append(rid)

# ── 4. 查 REVIEWER 列表 ───────────────────────────────────────────────────────
print('\n=== 评委列表（前20条） ===')
reviewers = get('/api/admin/reviews/reviewers', TOKEN)
rvlist = reviewers.get('data', [])
for rv in rvlist[:20]:
    print(f"  id={rv['id']} name={rv['name']} phone={rv['phone']} "
          f"bookGrp={rv.get('reviewerGroupCode','-')} interviewGrp={rv.get('interviewGroupCode','-')}")

with open('scripts/test_env_data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'comp_id': comp_id,
        'reg_ids': reg_ids,
        'reviewers': rvlist[:20]
    }, f, ensure_ascii=False, indent=2)
print('\n数据已存到 scripts/test_env_data.json')
