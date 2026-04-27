import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

# 代表性账号 + 候选密码
accounts = [
    ('OPS',             '13800000005', ['ops2026', 'Yiguo9527_', '123456', 'admin123']),
    ('COMMITTEE_ADMIN', '13800000127', ['ops2026', 'Yiguo9527_', '123456', 'admin123']),
    ('REVIEWER',        '13800002569', ['ops2026', 'Yiguo9527_', '123456', 'admin123']),
    ('CONTESTANT',      '13799999112', ['ops2026', 'Yiguo9527_', '123456', 'admin123']),
]

print(f'{"角色":<20} {"手机号":<15} {"可用密码"}')
print('-' * 55)
for role, phone, passwords in accounts:
    found = None
    for pwd in passwords:
        try:
            r = requests.post(f'{BASE}/api/auth/login-with-password',
                json={'phone': phone, 'password': pwd}, timeout=5)
            if r.status_code == 200 and r.json().get('success'):
                found = pwd
                break
        except:
            pass
    print(f'{role:<20} {phone:<15} {found if found else "未找到"}')
