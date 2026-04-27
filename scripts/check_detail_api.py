import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'
# 用 OPS 账号登录
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone': '13800000005', 'password': 'ops2026'}).json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

r = requests.get(f'{BASE}/api/registrations/150', headers=headers)
data = r.json().get('data', {})

print(f"status: {data.get('registration', {}).get('status')}")
mats = data.get('materials', [])
print(f"\nmaterials ({len(mats)} 条):")
for m in mats:
    print(f"  id={m['id']} type={m['type']} fileName={m['fileName']}")
pay = data.get('paymentProofs', [])
print(f"\npaymentProofs ({len(pay)} 条):")
for m in pay:
    print(f"  id={m['id']} type={m['type']} fileName={m['fileName']}")
