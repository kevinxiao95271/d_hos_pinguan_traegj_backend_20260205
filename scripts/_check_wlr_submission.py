import csv, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

target_ids = [
    '20260130','20260147','20260387','20260545','20260673','20260706',
    '20260740','20260759','20260760','20260771','20260789','20260816',
    '20260821','20260831','20260842','20260846','20260879','20260888',
    '20260926','20260928','20260956',
]

# Project data with status
proj_info = {}
with open('项目数据（含机构ID+手法+主题0410.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        proj_info[row['registration_id']] = row

# Submitter info
submitter_info = {}
with open('项目提交人信息0413.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        submitter_info[row['registration_id']] = row

print('=== 王临润分配项目提交状态（共21个）===\n')
not_submitted = []
submitted = []
for rid in target_ids:
    pi = proj_info.get(rid, {})
    si = submitter_info.get(rid, {})
    status = pi.get('status', '未知')
    proj_name = pi.get('project_name', '未知')
    inst = pi.get('institution_name', '未知')
    submitted_name = si.get('submitter_name', '')
    submitted_phone = si.get('submitter_phone', '')

    flag = '✓' if status not in ['未提交', 'draft', '', '未知'] else '✗'
    row_info = {
        'rid': rid, 'proj_name': proj_name, 'inst': inst,
        'status': status, 'submitter': submitted_name, 'phone': submitted_phone
    }
    if status in ['未提交', 'draft', '']:
        not_submitted.append(row_info)
    else:
        submitted.append(row_info)

    print(f'[{flag}] {rid} | 状态:{status} | {inst}')
    print(f'     项目: {proj_name[:35]}')
    if submitted_name:
        print(f'     提交人: {submitted_name} {submitted_phone}')
    print()

print(f'\n== 汇总 ==')
print(f'已提交: {len(submitted)} 个')
print(f'未提交/状态异常: {len(not_submitted)} 个')
if not_submitted:
    print('\n未提交项目:')
    for r in not_submitted:
        print(f'  {r["rid"]} {r["inst"]} 状态:{r["status"]}')
