# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_csv('scripts/init_prod_const_init_institutions.csv',
                 encoding='utf-8-sig', dtype=str,
                 usecols=['code', 'uscc', 'name', 'city', 'level'])

fuzzy_searches = {
    '宁波市鄞州第二医院':  ['鄞州', '第二医院'],
    '杭州市第二人民医院':  ['杭州', '第二人民'],
    '杭州市红会医院':      ['红会', '红十字'],
    '树兰(安吉)医院':      ['安吉', '树兰'],
}

results = {}
for label, keywords in fuzzy_searches.items():
    mask = df['name'].str.contains(keywords[0], na=False)
    if len(keywords) > 1:
        mask &= df['name'].str.contains(keywords[1], na=False)
    matched = df[mask][['code', 'uscc', 'name', 'city', 'level']].to_dict('records')
    results[label] = matched
    print(f'\n[{label}] keywords={keywords} -> {len(matched)} match(es)')
    for r in matched:
        print(f'  uscc={r["uscc"]}  name={r["name"]}  city={r["city"]}  level={r["level"]}')

with open('scripts/tmp_fuzzy_search.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
