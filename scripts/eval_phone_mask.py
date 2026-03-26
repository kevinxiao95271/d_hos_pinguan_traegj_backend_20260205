import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

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

reviewers = get(BASE + '/api/admin/reviewers', token).get('data', [])
print(f'评审专家总数: {len(reviewers)}\n')

# 模拟掩码：前3位 + 0000 + 后4位
def mask(phone):
    if phone and len(phone) == 11:
        return phone[:3] + '0000' + phone[7:]
    return phone

phones = [r.get('phone','') for r in reviewers if r.get('phone')]
masked = [mask(p) for p in phones]

# 检查掩码后是否有重复（unique冲突风险）
from collections import Counter
dup_masked = {m: cnt for m, cnt in Counter(masked).items() if cnt > 1}

print(f'原始手机号数: {len(phones)}')
print(f'掩码后手机号数: {len(set(masked))}')
if dup_masked:
    print(f'\n⚠️  掩码后存在重复（会导致 unique 约束冲突）: {len(dup_masked)} 组')
    for m, cnt in list(dup_masked.items())[:5]:
        orig = [p for p in phones if mask(p) == m]
        print(f'  掩码={m}  冲突原始号: {orig}')
else:
    print('✓ 掩码后无重复，无 unique 约束冲突风险')

# 检查是否有非11位号码
odd = [p for p in phones if len(p) != 11]
if odd:
    print(f'\n⚠️  非标准11位手机号: {odd}')
else:
    print('✓ 所有手机号均为标准11位')

# 检查 ops/admin 账号是否也在评审专家列表里
ops_phones = ['13800000005', '13800000001', '13800000002', '13800000003']
overlap = [p for p in phones if p in ops_phones]
if overlap:
    print(f'\n⚠️  OPS/管理员手机号也在评审专家列表: {overlap}')
else:
    print('✓ OPS/管理员账号不在评审专家范围内')

print('\n=== 功能影响评估 ===')
print('''
1. 登录凭证变更
   评委登录需用新掩码号码（前3+0000+后4）
   密码哈希不变，密码本身不受影响

2. JWT/会话
   Token 基于 userId 不基于手机号，现有 Token 不失效

3. 短信验证码
   SmsService 尚未接入真实服务商，无实际影响

4. 脚本/API 调用
   当前测试脚本中写死的评委手机号需同步更新

5. 前端展示
   评委管理页面会展示新的掩码号码，视觉上正常

6. 数据关联
   phone 字段无外键，仅是字符串，不影响 review_tasks 等关联表
''')
