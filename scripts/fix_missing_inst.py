import pandas as pd, json

df = pd.read_csv('scripts/init_prod_const_init_institutions.csv', encoding='utf-8-sig')

# 23 家缺失机构的名称（用于 CSV 精确查找）
target_names = [
    '浙江大学医学院附属第一医院',
    '浙江大学医学院附属第二医院',
    '浙江大学医学院附属邵逸夫医院',
    '浙江大学医学院附属妇产科医院',
    '浙江省人民医院',
    '浙江省中医院',
    '浙江大学医学院附属儿童医院',
    '浙江省肿瘤医院',
    '杭州市中医院',
    '杭州市第一人民医院',
    '杭州市妇产科医院',
    '宁波市第一医院',
    '宁波市第二医院',
    '温州医科大学附属第一医院',
    '温州医科大学附属第二医院',
    '温州医科大学附属眼视光医院',
    '嘉兴市第一医院',
    '嘉兴市第二医院',
    '湖州市中心医院',
    '绍兴市人民医院',
    '金华市中心医院',
    '衢州市人民医院',
    '丽水市中心医院',
]

# 等级优先取主院
level_order = {'三级': 0, '二级': 1, '一级': 2}
df['_ord'] = df['level'].map(lambda x: level_order.get(x, 9))
df_target = df[df['name'].isin(target_names)].copy()
best = df_target.sort_values('_ord').groupby('name').first().reset_index()

found_names = set(best['name'].tolist())
not_found = [n for n in target_names if n not in found_names]

with open('scripts/missing_inst_actual.json', 'w', encoding='utf-8') as f:
    json.dump({
        'found': best[['name','code','uscc','level','region','city']].to_dict('records'),
        'not_found': not_found
    }, f, ensure_ascii=False, indent=2)

# 生成 INSERT IGNORE ... SELECT SQL
lines = [
    '-- 从 const_init_institutions 补充缺失的 23 个机构',
    'INSERT IGNORE INTO `institutions`',
    '    (`name`, `code`, `uscc`, `region`, `city`, `level`, `is_ext`, `created_at`)',
    'SELECT `name`, `code`, `uscc`, `region`, `city`, `level`, 0, NOW()',
    'FROM `const_init_institutions`',
    'WHERE `code` IN ('
]
rows = best.to_dict('records')
for i, row in enumerate(rows):
    comma = '' if i == len(rows)-1 else ','
    lines.append(f"  '{row['code']}'{comma}  -- {row['name']}")
lines.append(');')

with open('scripts/insert_missing_institutions.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"found: {len(best)}, not_found: {not_found}")
