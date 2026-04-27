"""
找出同名冲突（同一报名人+机构有多条报名）→ 打印清单 → 重新下载（文件名加报名ID区分）
"""
import requests, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE    = 'http://zkjb.zjmss.org.cn'
OUT_DIR = os.path.join(os.path.dirname(__file__), '报名表')

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', '_', str(s).strip())

token = requests.post(f'{BASE}/api/auth/login-with-password',
    json={'phone':'13800010001','password':'ops2026'}, timeout=10).json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 拉全部已提交报名
all_items = []
page = 1
while True:
    data  = requests.get(f'{BASE}/api/admin/registrations/filter',
        params={'competitionId':1,'page':page,'size':50}, headers=h, timeout=30).json()['data']
    items = data.get('content') or data.get('items') or []
    all_items += [it for it in items if it.get('status') == 'SUBMITTED']
    if page >= (data.get('totalPages') or 1):
        break
    page += 1

# 按 报名人_机构 分组，找出有多条的
from collections import defaultdict
groups = defaultdict(list)
for it in all_items:
    key = f'{safe(it.get("applicantName",""))}_{safe(it.get("institutionName",""))}'
    groups[key].append(it)

dups = {k: v for k, v in groups.items() if len(v) > 1}

print(f'共 {len(all_items)} 条已提交报名')
print(f'同名冲突组数: {len(dups)} 组，涉及报名 {sum(len(v) for v in dups.values())} 条\n')
print('=' * 60)

ok = err = 0
for key, items in sorted(dups.items()):
    print(f'\n【{key}】共 {len(items)} 条报名：')
    for item in items:
        reg_id = item['id']
        appl   = safe(item.get('applicantName',''))
        inst   = safe(item.get('institutionName',''))
        proj   = item.get('projectName','')[:30]
        print(f'  reg={reg_id}  {proj}')

        mats  = item.get('materials') or []
        forms = [m for m in mats if m.get('type') in {'REGISTRATION_FORM_PDF','REGISTRATION_FORM_DOC'}]
        for mat in forms:
            ext      = os.path.splitext(mat.get('fileName') or '')[1].lower() or '.pdf'
            tag      = 'PDF' if 'PDF' in mat['type'] else 'DOC'
            # 统一用 报名人_机构_报名ID_PDF/DOC.ext 命名，避免冲突
            filename = f'{appl}_{inst}_{reg_id}_{tag}{ext}'
            path     = os.path.join(OUT_DIR, filename)
            if os.path.exists(path):
                print(f'    ○ 已存在 {filename}')
                ok += 1
                continue
            dl = requests.get(BASE + mat['downloadUrl'], headers=h, timeout=60, stream=True)
            if dl.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in dl.iter_content(1024*256): f.write(chunk)
                print(f'    ✓ {filename}  ({os.path.getsize(path)//1024}KB)')
                ok += 1
            else:
                print(f'    ✗ {filename}  HTTP_{dl.status_code}')
                err += 1

print(f'\n{"="*60}')
print(f'完成！成功={ok}  失败={err}')
print(f'文件目录: {OUT_DIR}')
