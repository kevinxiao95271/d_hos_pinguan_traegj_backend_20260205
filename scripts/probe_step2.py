import requests, re, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://zkjb.zjmss.org.cn'

def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]', '_', str(s).strip())

# 登录
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 拉第一页，兼容 items/content 两种 key
resp_data = requests.get(f'{BASE}/api/admin/registrations/filter',
    params={'competitionId':1,'page':1,'size':20}, headers=h, timeout=30
).json()['data']
print('data 顶层 keys:', list(resp_data.keys()))
items = resp_data.get('items') or resp_data.get('content') or []
print(f'本页报名数: {len(items)}')

# 只取有 paymentProofs 的
with_proof = [it for it in items if it.get('paymentProofs')]
print(f'有回执的: {len(with_proof)} 条，取前3条试下载')

out_dir = os.path.join(os.path.dirname(__file__), 'export_receipts_test')
os.makedirs(out_dir, exist_ok=True)

for item in with_proof[:3]:
    reg_id    = item['id']
    inst_name = item.get('institutionName', '')
    appl_name = item.get('applicantName', '')

    # 详情接口取手机号
    detail = requests.get(f'{BASE}/api/registrations/{reg_id}', headers=h, timeout=15).json().get('data', {})
    phone  = (detail.get('applicant') or {}).get('phone') or detail.get('applicantPhone') or 'unknown'
    print(f'\nreg={reg_id}  {appl_name}  {phone}  {inst_name}')

    for proof in item['paymentProofs']:
        ext  = os.path.splitext(proof['fileName'])[1] or '.bin'
        name = safe(f'{appl_name}_{phone}_{inst_name}') + ext
        path = os.path.join(out_dir, name)
        dl   = requests.get(BASE + proof['downloadUrl'], headers=h, timeout=30)
        if dl.status_code == 200:
            with open(path, 'wb') as f:
                f.write(dl.content)
            print(f'  ✓ 下载成功 {name}  ({len(dl.content)} bytes)')
        else:
            print(f'  ✗ 失败 HTTP {dl.status_code}  {proof["downloadUrl"]}')

print(f'\n文件保存在: {out_dir}')
