import pandas as pd, json

# 已存在的 USCC（从用户反馈整理）
existing = {
    'EXT000000003','EXT000000005','EXT000000006','EXT000000007',
    '12330000470003281H','12330000470032824N','12330000470051734A','12330000470051793D',
    '12330100470116622A','12330100470116657W','12330100470116673J',
    '12330109470453493C','12330109754405020K','1233020041952986XM',
    '12330205419550546R','12330227419611919D','12330227756286168R',
    '12330300470525557C','123303004705255657','12330381470860064L',
    '12330400470890693Q','12330681471481007R','12330782471771856W',
    '12330782689145495P','1233078347180163XH','12330900472092185H',
    '12331000796490606H','12331003472690185U','123310817458062608',
    '12332500472260070Y','12332500472310648J',
    '91330100321916626N','91330523MA28CUHJ9B',
}

# 全部需要的 USCC（56个）
needed = {
    '12330000470003281H','12330000470019360B','12330000470019376C',
    '12330000470019389U','12330000470019406W','12330000470019413U',
    '12330000470019424F','12330000470019428J','12330000470032824N',
    '12330000470051734A','12330000470051793D','12330000MA27YJY25A',
    '12330100470116622A','12330100470116637C','12330100470116641B',
    '12330100470116645J','12330100470116657W','12330100470116673J',
    '12330109470453493C','12330109754405020K','1233020041952986XM',
    '12330200470116670E','12330200470116671Y','12330205419550546R',
    '12330227419611919D','12330227756286168R','12330300470116760K',
    '12330300470116762P','12330300470116764U','12330300470525557C',
    '123303004705255657','12330381470860064L','12330400470460526N',
    '12330400470460530E','12330400470890693Q','12330500470460574F',
    '12330600470460618K','12330681471481007R','12330700470460651T',
    '12330782471771856W','12330782689145495P','1233078347180163XH',
    '12330800470460676T','12330900472092185H','12331000796490606H',
    '12331003472690185U','123310817458062608','12332500470460767T',
    '12332500472260070Y','12332500472310648J','91330100321916626N',
    '91330523MA28CUHJ9B',
    'EXT000000003','EXT000000005','EXT000000006','EXT000000007',
}

missing_uscc = needed - existing
print(f'Missing: {len(missing_uscc)}')

# 从 CSV 找对应的主院记录（用 USCC 匹配，取 level 不含"未定级/无级别/无等级"的优先，否则取第一条）
df = pd.read_csv('scripts/init_prod_const_init_institutions.csv', encoding='utf-8-sig')
df_miss = df[df['uscc'].isin(missing_uscc)].copy()

# 每个 USCC 选最佳记录（三级 > 其他有效等级 > 第一条）
level_order = {'三级':0,'二级':1,'一级':2}
df_miss['_ord'] = df_miss['level'].map(lambda x: level_order.get(x, 9))
best = df_miss.sort_values('_ord').groupby('uscc').first().reset_index()

lines = ['-- 补充缺失机构（从 const_init_institutions 复制）',
         'INSERT IGNORE INTO `institutions`',
         '    (`name`, `code`, `uscc`, `region`, `city`, `level`, `is_ext`, `created_at`)',
         'SELECT `name`, `code`, `uscc`, `region`, `city`, `level`, 0, NOW()',
         'FROM `const_init_institutions`',
         'WHERE `code` IN (']
for i, row in best.iterrows():
    comma = ',' if i < len(best)-1 else ''
    lines.append(f"  '{row['code']}'{comma}  -- {row['name']} ({row['uscc']})")
lines.append(');')

sql = '\n'.join(lines)
with open('scripts/insert_missing_institutions.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

# 报告未在 CSV 中找到的
found_uscc = set(best['uscc'].tolist())
not_in_csv = missing_uscc - found_uscc
result = {
    'missing_count': len(missing_uscc),
    'found_in_csv': len(found_uscc),
    'not_in_csv': list(not_in_csv)
}
with open('scripts/missing_inst_report.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False))
