"""
导出所有缴费回执文件
文件名: {报名人}_{机构名}.{ext}
输出目录: scripts/缴费回执/
"""
import requests, re, os, sys, csv
sys.stdout.reconfigure(encoding='utf-8')

BASE     = 'http://zkjb.zjmss.org.cn'
PHONE    = '13800010001'
PASSWORD = 'ops2026'
OUT_DIR  = os.path.join(os.path.dirname(__file__), '缴费回执')

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', '_', str(s).strip())

# 登录
print('登录中...')
token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone': PHONE, 'password': PASSWORD}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}
print('登录成功\n')

os.makedirs(OUT_DIR, exist_ok=True)

ok = err = skip = 0
csv_rows = []
page = 1

while True:
    data = requests.get(f'{BASE}/api/admin/registrations/filter',
        params={'competitionId': 1, 'page': page, 'size': 50},
        headers=h, timeout=30).json()['data']

    items       = data.get('content') or data.get('items') or []
    total_pages = data.get('totalPages') or 1
    print(f'第 {page}/{total_pages} 页，共 {len(items)} 条', flush=True)

    for item in items:
        proofs = item.get('paymentProofs') or []
        if not proofs:
            skip += 1
            continue

        appl = safe(item.get('applicantName') or '未知')
        inst = safe(item.get('institutionName') or '未知机构')

        for i, proof in enumerate(proofs, 1):
            ext      = os.path.splitext(proof.get('fileName') or '.jpg')[1] or '.jpg'
            suffix   = f'_{i}' if len(proofs) > 1 else ''
            filename = f'{appl}_{inst}{suffix}{ext}'
            path     = os.path.join(OUT_DIR, filename)

            # 已存在则跳过（断点续传）
            if os.path.exists(path):
                status = 'SKIP_EXISTS'
                ok += 1
                print(f'  ○ 已存在 {filename}')
            else:
                status = 'FAIL'
                for attempt in range(3):
                    try:
                        dl = requests.get(BASE + proof['downloadUrl'], headers=h,
                                          timeout=60, stream=True)
                        if dl.status_code == 200:
                            with open(path, 'wb') as f:
                                for chunk in dl.iter_content(chunk_size=1024*256):
                                    f.write(chunk)
                            status = 'OK'
                            size = os.path.getsize(path)
                            ok += 1
                            print(f'  ✓ {filename}  ({size//1024}KB)')
                            break
                        else:
                            status = f'HTTP_{dl.status_code}'
                            err += 1
                            print(f'  ✗ {filename}  {status}')
                            break
                    except Exception as e:
                        print(f'  ↻ 重试{attempt+1}/3  {filename}  {e}')
                        import time; time.sleep(2)
                else:
                    err += 1
                    print(f'  ✗ 放弃 {filename}')

            csv_rows.append({
                '报名ID':   item['id'],
                '项目名称': item.get('projectName', ''),
                '机构名称': item.get('institutionName', ''),
                '报名人':   item.get('applicantName', ''),
                '文件名':   filename,
                '状态':     status,
            })

    if page >= total_pages:
        break
    page += 1

# 写汇总 CSV
csv_path = os.path.join(OUT_DIR, '汇总.csv')
if csv_rows:
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)

print(f'\n{"="*50}')
print(f'完成！  成功={ok}  失败={err}  无回执跳过={skip}')
print(f'文件目录: {OUT_DIR}')
print(f'汇总CSV : {csv_path}')
