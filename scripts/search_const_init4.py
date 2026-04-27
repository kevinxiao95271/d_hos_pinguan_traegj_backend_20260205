# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_csv('scripts/init_prod_const_init_institutions.csv',
                 encoding='utf-8-sig', dtype=str,
                 usecols=['code', 'uscc', 'name', 'city', 'level'])

searches = {
    '鄞州（全部）':    ['鄞州', None],
    '杭州市红':        ['杭州', '红'],
}

for label, (kw1, kw2) in searches.items():
    mask = df['name'].str.contains(kw1, na=False)
    if kw2:
        mask &= df['name'].str.contains(kw2, na=False)
    matched = df[mask][['uscc', 'name', 'city', 'level']]
    print(f'\n[{label}] -> {len(matched)} results')
    for _, r in matched.iterrows():
        print(f'  {r["uscc"]}  {r["name"]}  {r["city"]}  {r["level"]}')
