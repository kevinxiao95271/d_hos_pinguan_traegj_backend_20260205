import requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'
PHONE = '13811185687'  # 刘研究员（测试库FINAL评委）
PWD   = 'user123'

def pp(label, r):
    print(f"\n=== {label} ===")
    print(f"HTTP {r.status_code}")
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except:
        print(r.text)

# Step1: 登录，观察 pendingIntegrityNoticeKeys
r = requests.post(f'{BASE}/api/auth/login-with-password', json={'phone': PHONE, 'password': PWD})
pp("Step1: 登录", r)
data = r.json().get('data', {})
token = data.get('token')
pending = data.get('pendingIntegrityNoticeKeys')
print(f"\n>>> pendingIntegrityNoticeKeys = {pending}")

# Step2: 确认 FINAL 须知
r2 = requests.post(f'{BASE}/api/auth/notice/confirm',
    json={'noticeKey': 'FINAL'},
    headers={'Authorization': f'Bearer {token}'})
pp("Step2: confirm FINAL", r2)

# Step3: 再次登录，确认 FINAL 不再 pending
r3 = requests.post(f'{BASE}/api/auth/login-with-password', json={'phone': PHONE, 'password': PWD})
pp("Step3: 再次登录", r3)
data3 = r3.json().get('data', {})
pending3 = data3.get('pendingIntegrityNoticeKeys')
print(f"\n>>> pendingIntegrityNoticeKeys (after confirm) = {pending3}")
