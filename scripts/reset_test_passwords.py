"""
把评委和参赛者代表性账号统一重置为 test2026，方便接口测试
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

# OPS登录
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800000005','password':'ops2026'}).json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

# 要重置的账号 {userId: name}
targets = {
    # REVIEWER
    5:  '孙丽娟(REVIEWER)',
    27: '刘研究员(REVIEWER)',
    28: '朱研究员(REVIEWER)',
    29: '朱研究员2(REVIEWER)',
    30: '许研究员(REVIEWER)',
    # CONTESTANT
    4:  '王建国(CONTESTANT)',
    6:  '测试用户6(CONTESTANT)',
    8:  '测试用户8(CONTESTANT)',
}

NEW_PASSWORD = 'test2026'

print(f'{"userId":<8} {"name":<25} {"新密码"}')
print('-' * 55)
for uid, name in targets.items():
    r = requests.post(f'{BASE}/api/admin/users/{uid}/reset-password', headers=headers)
    d = r.json()
    if d.get('success'):
        new_pwd = d['data']['newPassword']
        print(f'{uid:<8} {name:<25} {new_pwd}')
    else:
        print(f'{uid:<8} {name:<25} ✗ {d.get("message","失败")} ({r.status_code})')
