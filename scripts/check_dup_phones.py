# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', header=1, engine='openpyxl')
df.columns = ['unit', 'name', 'field', 'background', 'position', 'phone']
df = df.dropna(subset=['name'])
df['unit'] = df['unit'].astype(str).str.strip().str.replace('\n', '').str.replace(' ', '')
df['name'] = df['name'].astype(str).str.strip()
df['phone'] = df['phone'].astype(str).str.strip().str.replace('.0', '', regex=False)

total = len(df)
print(f'总人数: {total}')
print(f'唯一手机号数: {df["phone"].nunique()}')
print()

# 找重复手机号
dup_phones = df[df.duplicated(subset=['phone'], keep=False)].sort_values('phone')
print(f'手机号重复的条目数: {len(dup_phones)}')
print(f'涉及重复手机号数量: {dup_phones["phone"].nunique()}')
print()

# 按手机号分组输出
result = []
for phone, group in dup_phones.groupby('phone'):
    entry = {
        'phone': phone,
        'count': len(group),
        'experts': group[['name', 'unit', 'position']].to_dict('records')
    }
    result.append(entry)
    print(f'手机号 {phone} ({len(group)}人):')
    for _, row in group.iterrows():
        print(f'  {row["name"]} / {row["unit"]} / {row["position"]}')

with open('scripts/tmp_dup_phones_new.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 空手机号
empty = df[df['phone'].isin(['nan', '', 'None'])]
print(f'\n手机号为空的条目: {len(empty)}')
for _, row in empty.iterrows():
    print(f'  {row["name"]} / {row["unit"]}')
