# -*- coding: utf-8 -*-
import pandas as pd
import json

target_insts = [
    '丽水市人民医院',
    '义乌市中心医院',
    '台州市第一人民医院',
    '宁波市鄞州第二医院',
    '杭州市第二人民医院',
    '杭州市红会医院',
    '树兰(安吉)医院',
    '浙江中医药大学附属第二医院',
    '浙江省立同德医院',
    '温州市人民医院',
    '瑞安市人民医院',
    '萧山区第一人民医院',
]

# Read const_init CSV
df = pd.read_csv('scripts/init_prod_const_init_institutions.csv', encoding='utf-8-sig', dtype=str)
print('const_init total rows:', len(df))
print('Columns:', df.columns.tolist())
print()

results = {}
for inst in target_insts:
    # Exact match
    exact = df[df.apply(lambda r: r.astype(str).str.contains(inst, regex=False).any(), axis=1)]
    results[inst] = {
        'exact_count': len(exact),
        'matches': exact.to_dict('records') if len(exact) <= 5 else exact.head(3).to_dict('records')
    }
    print(f'[{inst}] exact matches: {len(exact)}')
    for _, row in exact.iterrows():
        # Print key fields
        name_col = [c for c in df.columns if 'name' in c.lower() or '名' in c]
        uscc_col = [c for c in df.columns if 'uscc' in c.lower() or '信用' in c or '统一' in c]
        print(f'  name_cols={name_col}, uscc_cols={uscc_col}')
        break

with open('scripts/tmp_const_init_search.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\nSaved to scripts/tmp_const_init_search.json')
