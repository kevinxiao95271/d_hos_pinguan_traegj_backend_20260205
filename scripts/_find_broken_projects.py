import csv, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

keywords = ['分片区RRT', '提高ICU', '门诊血透']

# Load project data for institution info
proj_data = {}
try:
    with open('项目数据（含机构ID+手法+主题0410.csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get('registration_id') or row.get('报名号') or row.get('id') or ''
            proj_data[rid] = row
    print(f'项目数据: {len(proj_data)} 条, 列: {list(list(proj_data.values())[0].keys()) if proj_data else []}')
except Exception as e:
    print(f'项目数据加载失败: {e}')

# Load submitter info
submitter_data = {}
try:
    with open('项目提交人信息0413.csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get('registration_id') or row.get('报名号') or row.get('id') or ''
            submitter_data[rid] = row
    print(f'提交人数据: {len(submitter_data)} 条, 列: {list(list(submitter_data.values())[0].keys()) if submitter_data else []}')
except Exception as e:
    print(f'提交人数据加载失败: {e}')

# Search in allocation list
with open('生产环境项目已分配清单0414.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print()
print('=== 匹配项目及分配专家 ===')
matched_ids = set()
for row in rows:
    proj = row.get('project_name', '')
    for kw in keywords:
        if kw in proj:
            rid = row['registration_id']
            matched_ids.add(rid)
            break

# Group by registration_id
from collections import defaultdict
grouped = defaultdict(list)
for row in rows:
    if row['registration_id'] in matched_ids:
        grouped[row['registration_id']].append(row)

for rid, entries in sorted(grouped.items()):
    proj_name = entries[0]['project_name']
    group_code = entries[0]['group_code']
    print(f'\n【报名号: {rid}】 组别: {group_code}')
    print(f'  项目名称: {proj_name}')
    # Get institution info from project data
    if rid in proj_data:
        pd = proj_data[rid]
        inst = pd.get('institution_name') or pd.get('机构名称') or pd.get('单位') or '未知'
        print(f'  参赛机构: {inst}')
    print(f'  分配专家:')
    for e in entries:
        print(f'    - {e["reviewer_name"]} ({e["reviewer_phone"]})')
