# -*- coding: utf-8 -*-
# 评估：去掉重复手机号后，145人中有多少能匹配到 institutions 表中的明确机构
# 仅评估，不动任何数据

import pandas as pd
import re
import json

# ---- 1. 读取新专家名单，去掉重复手机号 ----
df = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', header=1, engine='openpyxl')
df.columns = ['unit', 'name', 'field', 'background', 'position', 'phone']
df = df.dropna(subset=['name'])
df['unit'] = df['unit'].astype(str).str.strip().str.replace('\n', '').str.replace(' ', '')
df['name'] = df['name'].astype(str).str.strip()
df['phone'] = df['phone'].astype(str).str.strip().str.replace('.0', '', regex=False)

dup_mask = df.duplicated(subset=['phone'], keep=False)
df_clean = df[~dup_mask].copy()
print(f'去掉重复手机后剩余专家: {len(df_clean)} 人')

# ---- 2. 读取 institutions 表中已有记录（from init SQL）----
with open('scripts/init_prod_institutions_and_reviewers.sql', encoding='utf-8') as f:
    sql_text = f.read()

sql_insts = re.findall(r"INSERT INTO institutions.*?VALUES(.*?)ON DUPLICATE", sql_text, re.DOTALL)
inst_names_in_db = re.findall(r"\('([^']+)'", sql_insts[0]) if sql_insts else []

# 加上三个新增 EXT 机构（已确认要录入）
ext_institutions = ['浙江省质量协会', '浙江省医院管理中心', '浙江大学']
db_set = set(inst_names_in_db) | set(ext_institutions)

print(f'institutions 表中已有记录: {len(inst_names_in_db)} 家（+3 ext）')

# ---- 3. 别名映射（新文件写法 → institutions 表中实际名称）----
alias_map = {
    # 原有别名
    '嘉兴市中医院':           '嘉兴市中医医院',
    '宁波医疗中心李惠利医院': '宁波市医疗中心李惠利医院',
    '宁波市第一医院':         '宁波大学附属第一医院',
    '宁波市第九医院':         '宁波市第九医院（宁波市第一医院江北分院、宁波市江北区人民医院）',
    '杭州市妇产科医院':       '杭州市妇产科医院（杭州市妇幼保健院）钱塘院区',
    '湖州市第一人民医院':     '湖州师范学院附属第一医院（湖州市第一人民医院）',
    '萧山医院':               '浙江萧山医院',
    '杭州市红会医院':         '杭州市红十字会医院',
    '树兰(安吉)医院':         '树兰（安吉）医院',
    # 用户确认的映射
    '杭州市第二人民医院':     '杭州师范大学附属医院',
    '宁波市鄞州第二医院':     '宁波市中西医结合医院',
    # ext 机构映射
    '省医管中心':             '浙江省医院管理中心',
}

# ---- 4. 逐人匹配 ----
matched = []
unmatched = []
ext_matched = []

for _, row in df_clean.iterrows():
    unit_raw = str(row['unit']).strip()
    lookup = alias_map.get(unit_raw, unit_raw)

    if lookup in db_set:
        if lookup in ext_institutions or unit_raw in ('省医管中心', '浙江大学', '浙江省质量协会'):
            ext_matched.append({'name': row['name'], 'unit': unit_raw, 'mapped': lookup})
        else:
            matched.append({'name': row['name'], 'unit': unit_raw, 'mapped': lookup})
    else:
        unmatched.append({'name': row['name'], 'unit': unit_raw, 'phone': row['phone']})

print()
print(f'===== 匹配结果 =====')
print(f'可匹配到医院机构（非ext）: {len(matched)} 人')
print(f'匹配到 EXT 外部机构:       {len(ext_matched)} 人')
print(f'无法匹配:                  {len(unmatched)} 人')
print()

if unmatched:
    print('--- 无法匹配的专家 ---')
    for r in unmatched:
        print(f'  {r["name"]} / {r["unit"]}')

if ext_matched:
    print()
    print('--- EXT 外部机构专家 ---')
    for r in ext_matched:
        print(f'  {r["name"]} / {r["unit"]} -> {r["mapped"]}')

result = {
    'total_clean': len(df_clean),
    'matched_hospital': len(matched),
    'matched_ext': len(ext_matched),
    'unmatched': len(unmatched),
    'unmatched_list': unmatched,
    'ext_list': ext_matched,
}
with open('scripts/tmp_eval_match.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\n评估完成，结果已保存到 scripts/tmp_eval_match.json')
