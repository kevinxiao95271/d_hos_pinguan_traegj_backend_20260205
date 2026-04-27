"""
通过 API 导出 2026 品管大赛所有缴费回执照片
输出：
  export_receipts/
    summary.csv          报名人 / 手机 / 机构 / 文件名 / 下载状态
    files/
      {报名ID}_{机构}_{报名人}/
        {文件名}
用法：
  pip install requests
  python export_payment_proofs_api.py
"""

import sys, os, re, csv
sys.stdout.reconfigure(encoding='utf-8')
import requests

# ── 配置 ──────────────────────────────────────────────────────────────────────
BASE          = 'http://zkjb.zjmss.org.cn'
PHONE         = '13800010001'
PASSWORD      = 'ops2026'
COMPETITION_ID = 1
PAGE_SIZE     = 100
OUT_DIR       = os.path.join(os.path.dirname(__file__), 'export_receipts')
# ─────────────────────────────────────────────────────────────────────────────


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]', '_', str(s).strip())


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files_dir = os.path.join(OUT_DIR, 'files')
    os.makedirs(files_dir, exist_ok=True)

    # 1. 登录
    print('登录中...')
    r = requests.post(f'{BASE}/api/auth/login-with-password',
                      json={'phone': PHONE, 'password': PASSWORD}, timeout=15)
    r.raise_for_status()
    token = r.json()['data']['token']
    h = {'Authorization': f'Bearer {token}'}
    print('登录成功')

    # 2. 分页拉取所有报名 ID
    reg_ids = []
    page = 1
    while True:
        resp = requests.get(f'{BASE}/api/admin/registrations/filter',
                            params={'competitionId': COMPETITION_ID,
                                    'page': page, 'size': PAGE_SIZE},
                            headers=h, timeout=30).json()
        data = resp.get('data', {})
        # 兼容 items / content 两种字段名
        items = data.get('items') or data.get('content') or []
        for item in items:
            reg_ids.append(item.get('id'))
        total_pages = data.get('totalPages') or data.get('pages') or 1
        print(f'  第 {page}/{total_pages} 页，本页 {len(items)} 条')
        if page >= total_pages or not items:
            break
        page += 1

    print(f'共 {len(reg_ids)} 条报名，开始逐条查缴费回执...\n')

    # 3. 逐条拿详情 → 过滤 payment_proof → 下载
    csv_rows = []
    ok = err = skip = 0

    for i, reg_id in enumerate(reg_ids, 1):
        detail = requests.get(f'{BASE}/api/registrations/{reg_id}',
                              headers=h, timeout=15).json().get('data', {})

        # 报名基础信息
        proj_name  = detail.get('projectName') or ''
        inst_name  = (detail.get('institution') or {}).get('name') or detail.get('institutionName') or ''
        appl_name  = (detail.get('applicant')   or {}).get('name') or detail.get('applicantName')   or ''
        appl_phone = (detail.get('applicant')   or {}).get('phone') or detail.get('applicantPhone') or ''
        status     = detail.get('status') or ''

        # 所有材料里找缴费回执
        all_mats   = (detail.get('materials') or []) + (detail.get('paymentProofs') or [])
        proofs     = [m for m in all_mats if str(m.get('type', '')).lower() == 'payment_proof']

        if not proofs:
            skip += 1
            continue

        for mat in proofs:
            mat_id    = mat.get('id')
            file_name = mat.get('fileName') or mat.get('filename') or f'{mat_id}.bin'
            # 取原始扩展名
            ext = os.path.splitext(file_name)[1] or '.bin'
            # 文件名 = 报名人_手机号_机构名.ext（多张回执加序号）
            idx_suffix = f'_{proofs.index(mat)+1}' if len(proofs) > 1 else ''
            out_name   = safe(f'{appl_name}_{appl_phone}_{inst_name}{idx_suffix}') + ext
            local_path = os.path.join(files_dir, out_name)
            dl_status  = 'SKIP'

            if mat_id:
                try:
                    dl = requests.get(f'{BASE}/api/materials/{mat_id}/download',
                                      headers=h, timeout=30)
                    if dl.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(dl.content)
                        dl_status = 'OK'
                        ok += 1
                    else:
                        dl_status = f'HTTP_{dl.status_code}'
                        err += 1
                except Exception as e:
                    dl_status = f'ERR:{e}'
                    err += 1

            csv_rows.append({
                '报名ID': reg_id, '项目名称': proj_name, '报名状态': status,
                '机构名称': inst_name, '报名人': appl_name, '手机号': appl_phone,
                '文件名': file_name, '下载状态': dl_status, '本地路径': local_path,
            })

        print(f'[{i}/{len(reg_ids)}] reg={reg_id} {inst_name} {appl_name}  proofs={len(proofs)}')

    # 4. 写 CSV
    csv_path = os.path.join(OUT_DIR, 'summary.csv')
    if csv_rows:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            w.writeheader()
            w.writerows(csv_rows)

    print(f'\n{"="*50}')
    print(f'完成！  成功下载={ok}  失败={err}  无回执跳过={skip}')
    print(f'汇总CSV : {csv_path}')
    print(f'文件目录: {files_dir}')
    print('='*50)


if __name__ == '__main__':
    main()
