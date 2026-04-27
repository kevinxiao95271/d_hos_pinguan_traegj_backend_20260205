import csv, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

target_name = '王临润'

# Expert data
expert_info = {}
with open('专家数据含机构ID0410.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('name') == target_name or row.get('姓名') == target_name:
            expert_info = row
            break

# Search in allocation list
with open('生产环境项目已分配清单0414.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    alloc_rows = list(reader)

# Project data
proj_info = {}
with open('项目数据（含机构ID+手法+主题0410.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        proj_info[row['registration_id']] = row

# Find all projects assigned to 王临润
assigned = [row for row in alloc_rows if row.get('reviewer_name') == target_name]

print(f'=== 专家【{target_name}】信息 ===\n')
if expert_info:
    for k, v in expert_info.items():
        if v:
            print(f'  {k}: {v}')
else:
    print('  在专家数据CSV中未找到该专家')
    # Try to get phone from allocation list
    if assigned:
        print(f'  手机 (来自分配清单): {assigned[0]["reviewer_phone"]}')

print(f'\n=== {target_name} 分配的项目（共 {len(assigned)} 个）===\n')
for row in assigned:
    rid = row['registration_id']
    pi = proj_info.get(rid, {})
    print(f'  报名号: {rid} | 组别: {row["group_code"]}')
    print(f'  项目: {pi.get("project_name", row.get("project_name", "未知"))}')
    print(f'  机构: {pi.get("institution_name", "未知")} | 城市: {pi.get("institution_city", "未知")}')
    print()
