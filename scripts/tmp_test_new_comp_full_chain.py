#!/usr/bin/env python3
"""
全流程自测：2027赛事（comp 26）
1. OPS 登录 → 切换赛事到 comp 26
2. 参赛者登录（三级医院）→ 创建草稿 → 上传材料 → 提交
3. OPS 后台：筛选报名列表 → 检查新报名
4. OPS 后台：项目分组页 → 检查可见
"""
import io, sys, requests, pymysql, json
from datetime import datetime
import uuid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'http://81.71.44.180:6039'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root',
          password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

PASS_MARK = '✅'
FAIL_MARK = '❌'
results = []

def check(label, ok, detail=''):
    mark = PASS_MARK if ok else FAIL_MARK
    msg = f'{mark} {label}'
    if detail: msg += f'  ({detail})'
    print(msg)
    results.append((ok, label, detail))
    return ok

def api(method, path, token=None, **kwargs):
    h = {'Authorization': f'Bearer {token}'} if token else {}
    r = getattr(requests, method)(BASE + path, headers=h, timeout=15, **kwargs)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {}

print('=' * 60)
print('全流程测试 START', datetime.now().strftime('%H:%M:%S'))
print('=' * 60)

# ── STEP 1: OPS 登录 ────────────────────────────────────────
print('\n── STEP 1: OPS 登录 ──')
sc, d = api('post', '/api/auth/login-with-password',
            json={'phone': '13800000005', 'password': 'ops2026'})
ops_ok = sc == 200 and d.get('success')
check('OPS 登录', ops_ok, f'status={sc}')
ops_token = d.get('data', {}).get('token', '') if ops_ok else ''
ops_comp = d.get('data', {}).get('currentCompetitionId')
check('登录返回 currentCompetitionId', ops_comp is not None, str(ops_comp))

# ── STEP 2: OPS 切换赛事到 comp 26 ─────────────────────────
print('\n── STEP 2: 切换赛事到 comp 26 ──')
sc, d = api('post', '/api/admin/current-competition', ops_token,
            params={'competitionId': 26})
check('切换赛事 comp 26', sc == 200 and d.get('success'), str(d.get('message', '')))

# 验证 latest 接口也反映
sc, d = api('get', '/api/competitions/latest', ops_token)
cur_id = d.get('data', {}).get('id')
check('competitions/latest 返回 comp 26', cur_id == 26, f'id={cur_id}')

# ── STEP 3: 参赛者登录（三级医院）──────────────────────────
print('\n── STEP 3: 参赛者登录 ──')
sc, d = api('post', '/api/auth/login-with-password',
            json={'phone': '13900003301', 'password': 'user123'})
usr_ok = sc == 200 and d.get('success')
check('参赛者登录', usr_ok, f'status={sc}')
usr_token = d.get('data', {}).get('token', '') if usr_ok else ''
usr_comp = d.get('data', {}).get('currentCompetitionId')
check('参赛者登录 currentCompetitionId=26', usr_comp == 26, str(usr_comp))

# ── STEP 4: 创建草稿 ────────────────────────────────────────
print('\n── STEP 4: 创建草稿 ──')
proj_name = f'三级医院全流程测试_{uuid.uuid4().hex[:6]}'
sc, d = api('post', '/api/registrations', usr_token,
            json={'competitionId': 26, 'institutionId': 36103,
                  'projectName': proj_name, 'groupType': 'ADVANCED'})
draft_ok = sc == 200 and d.get('success')
check('创建草稿', draft_ok, str(d.get('message', '')))
draft_id = d.get('data', {}).get('id') if draft_ok else None
check('草稿 ID 有值', draft_id is not None, str(draft_id))

# 草稿不应显示正式编号
draft_num = d.get('data', {}).get('registrationNumber')
check('草稿阶段无项目编号', draft_num is None, str(draft_num))

# ── STEP 5: 上传材料（直接插库）────────────────────────────
print('\n── STEP 5: 上传材料 ──')
if draft_id:
    c = pymysql.connect(**DB); cur = c.cursor()
    cur.execute('SELECT file_url, file_name FROM material_files WHERE registration_id=20261176 AND type=%s LIMIT 1',
                ('REGISTRATION_FORM_DOC',))
    doc = cur.fetchone()
    cur.execute('SELECT file_url, file_name FROM material_files WHERE registration_id=20261176 AND type=%s LIMIT 1',
                ('REGISTRATION_FORM_PDF',))
    pdf = cur.fetchone()
    cur.execute('SELECT file_url, file_name FROM material_files WHERE registration_id=20261176 AND type=%s LIMIT 1',
                ('payment_proof',))
    pmt = cur.fetchone()
    now = datetime.now()
    for mat_type, mat in [('REGISTRATION_FORM_DOC', doc), ('REGISTRATION_FORM_PDF', pdf)]:
        if mat:
            cur.execute('INSERT INTO registration_draft_material_files (draft_id, type, file_name, file_url, uploaded_at) VALUES (%s,%s,%s,%s,%s)',
                        (draft_id, mat_type, mat[1], mat[0], now))
    c.commit(); cur.close(); c.close()
    check('草稿材料插入（DOC+PDF）', doc is not None and pdf is not None)
else:
    check('草稿材料插入', False, '草稿未创建，跳过')

# ── STEP 6: 提交草稿 ────────────────────────────────────────
print('\n── STEP 6: 提交草稿 ──')
reg_id = None
if draft_id:
    sc, d = api('post', f'/api/registrations/{draft_id}/submit', usr_token)
    sub_ok = sc == 200 and d.get('success')
    check('提交草稿', sub_ok, str(d.get('message', '')))
    reg_id = d.get('data', {}).get('id') if sub_ok else None
    if reg_id:
        year_ok = str(reg_id).startswith('2027')
        check(f'报名编号年份前缀 2027xxxx', year_ok, str(reg_id))
    else:
        check('报名编号有值', False, str(d))
else:
    check('提交草稿', False, '草稿未创建，跳过')

# ── STEP 7: 参赛者查我的报名 ────────────────────────────────
print('\n── STEP 7: 参赛者查我的报名 ──')
sc, d = api('get', '/api/registrations/my', usr_token)
my_regs = d.get('data', [])
found = any(r.get('id') == reg_id for r in my_regs) if reg_id else False
check('我的报名列表含新提交项', found, f'共{len(my_regs)}条')

# ── STEP 8: OPS 后台筛选（page=1）──────────────────────────
print('\n── STEP 8: OPS 后台筛选 ──')
sc, d = api('get', f'/api/admin/registrations/filter?competitionId=26&page=1&size=20', ops_token)
filter_ok = sc == 200 and d.get('success')
check('后台筛选 page=1 成功', filter_ok, f"total={d.get('data',{}).get('totalElements')}")
items = d.get('data', {}).get('content', [])
found_admin = any(r.get('id') == reg_id for r in items) if reg_id else False
check('后台筛选列表含新报名', found_admin, f'新ID={reg_id}')

# ── STEP 9: 项目分组页 ──────────────────────────────────────
print('\n── STEP 9: 项目分组页 ──')
sc, d = api('get', f'/api/admin/registrations/filter?competitionId=26&page=1&size=50', ops_token)
items2 = d.get('data', {}).get('content', [])
found_group = any(r.get('id') == reg_id for r in items2) if reg_id else False
check('项目分组列表含新报名', found_group, f'共{len(items2)}条')

# ── STEP 10: 我的赛事列表 ───────────────────────────────────
print('\n── STEP 10: 我的赛事 ──')
sc, d = api('get', '/api/registrations/my/competitions', usr_token)
comps = d.get('data') or []
cur26 = next((x for x in comps if x.get('competitionId') == 26), None)
check('我的赛事列表含 comp 26', cur26 is not None, f'共{len(comps)}条')
if cur26:
    check('comp 26 标记为 current', cur26.get('current') is True, str(cur26.get('current')))

# ── 汇总 ────────────────────────────────────────────────────
print('\n' + '=' * 60)
passed = sum(1 for ok, _, _ in results if ok)
total = len(results)
print(f'结果：{passed}/{total} 通过')
failures = [(l, d) for ok, l, d in results if not ok]
if failures:
    print('\n失败项：')
    for l, d in failures:
        print(f'  {FAIL_MARK} {l}  {d}')
else:
    print('全部通过 🎉')
print('=' * 60)
