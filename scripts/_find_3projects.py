import csv, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

target_ids = ['20260774', '20260778', '20260784']

# Project data
proj_info = {}
with open('项目数据（含机构ID+手法+主题0410.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        proj_info[row['registration_id']] = row

# Allocation list
with open('生产环境项目已分配清单0414.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    alloc_rows = list(reader)

grouped = defaultdict(list)
for row in alloc_rows:
    if row['registration_id'] in target_ids:
        grouped[row['registration_id']].append(row)

print('=== 3个问题项目的分配专家 ===\n')
labels = {
    '20260774': '宁大康宁 - 分片区RRT',
    '20260778': '天台县医院 - 提高ICU',
    '20260784': '慈溪市医院 - 提高门诊血透',
}
for rid in target_ids:
    entries = grouped.get(rid, [])
    pi = proj_info.get(rid, {})
    print(f'【{labels[rid]}】')
    print(f'  报名号: {rid}')
    print(f'  组别: {entries[0]["group_code"] if entries else "未分配"}')
    print(f'  项目全名: {pi.get("project_name", "未知")}')
    print(f'  参赛机构: {pi.get("institution_name", "未知")}')
    print(f'  城市: {pi.get("institution_city", "未知")}')
    if entries:
        print(f'  分配评审专家:')
        for e in entries:
            print(f'    · {e["reviewer_name"]}  手机: {e["reviewer_phone"]}')
    else:
        print(f'  分配评审专家: 未找到')
    print()
