"""
下载所有已提交报名的报名表（PDF + DOC 全部下载）
文件名: {报名人}_{机构名}.{ext}
输出目录: scripts/报名表/
"""
import requests, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE    = 'http://zkjb.zjmss.org.cn'
OUT_DIR = os.path.join(os.path.dirname(__file__), '报名表')

FORM_TYPES = {'REGISTRATION_FORM_PDF', 'REGISTRATION_FORM_DOC'}

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', '_', str(s).strip())

def download(url, path, h):
    for attempt in range(3):
        try:
            dl = requests.get(url, headers=h, timeout=60, stream=True)
            if dl.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in dl.iter_content(chunk_size=1024 * 256):
                        f.write(chunk)
                return 'OK', os.path.getsize(path)
            else:
                return f'HTTP_{dl.status_code}', 0
        except Exception as e:
            print(f'    ↻ 重试{attempt+1}/3  {e}')
            import time; time.sleep(2)
    return 'FAIL', 0

# 登录（运行时输入，不写死）
PHONE    = input('OPS账号手机号: ').strip()
PASSWORD = input('密码: ').strip()

print('登录中...')
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone': PHONE, 'password': PASSWORD}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}
print('登录成功\n')

os.makedirs(OUT_DIR, exist_ok=True)

ok = err = skip = 0
page = 1

while True:
    data = requests.get(f'{BASE}/api/admin/registrations/filter',
        params={'competitionId': 1, 'page': page, 'size': 50},
        headers=h, timeout=30).json()['data']

    items       = data.get('content') or data.get('items') or []
    total_pages = data.get('totalPages') or 1
    print(f'第 {page}/{total_pages} 页，共 {len(items)} 条', flush=True)

    for item in items:
        if item.get('status') != 'SUBMITTED':
            continue

        appl  = safe(item.get('applicantName') or '未知')
        inst  = safe(item.get('institutionName') or '未知机构')
        mats  = item.get('materials') or []
        forms = [m for m in mats if m.get('type') in FORM_TYPES]

        if not forms:
            skip += 1
            print(f'  - 无报名表 reg={item["id"]}  {appl}_{inst}')
            continue

        for mat in forms:
            orig_name = mat.get('fileName') or ''
            ext       = os.path.splitext(orig_name)[1].lower() or '.pdf'
            filename  = f'{appl}_{inst}{ext}'
            path      = os.path.join(OUT_DIR, filename)

            # 同名文件已存在（同一报名人同格式）加 _PDF/_DOC 区分
            if os.path.exists(path):
                tag      = '_PDF' if 'PDF' in mat.get('type', '') else '_DOC'
                filename = f'{appl}_{inst}{tag}{ext}'
                path     = os.path.join(OUT_DIR, filename)

            if os.path.exists(path):
                ok += 1
                print(f'  ○ 已存在 {filename}')
                status = 'SKIP_EXISTS'
            else:
                status, size = download(BASE + mat['downloadUrl'], path, h)
                if status == 'OK':
                    ok += 1
                    print(f'  ✓ {filename}  ({size // 1024}KB)')
                else:
                    err += 1
                    print(f'  ✗ {filename}  {status}')

    if page >= total_pages:
        break
    page += 1

print(f'\n{"="*50}')
print(f'完成！  成功={ok}  失败={err}  无报名表跳过={skip}')
print(f'文件目录: {OUT_DIR}')
