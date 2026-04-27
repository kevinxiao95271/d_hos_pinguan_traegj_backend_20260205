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

# Read only the 'name' column for speed, then join uscc/code
df = pd.read_csv('scripts/init_prod_const_init_institutions.csv',
                 encoding='utf-8-sig', dtype=str,
                 usecols=['code', 'uscc', 'name', 'city', 'level'])
print(f'Total rows: {len(df)}')

results = {}
for inst in target_insts:
    # name column match (contains)
    matched = df[df['name'].str.contains(inst, na=False, regex=False)]
    rows = matched[['code', 'uscc', 'name', 'city', 'level']].to_dict('records')
    results[inst] = {
        'count': len(rows),
        'matches': rows
    }

with open('scripts/tmp_const_init_search.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n=== SEARCH RESULTS ===')
for inst, res in results.items():
    print(f'\n[{inst}] -> {res["count"]} match(es)')
    for r in res['matches']:
        print(f'  uscc={r["uscc"]}  name={r["name"]}  city={r["city"]}  level={r["level"]}')
