import pandas as pd, re, json

df = pd.read_excel('浙江省品管大赛专家库成员名单-2026.3.16部分专家号码已修正.xlsx',
                   sheet_name='专家库成员名单（3.16更新）', dtype=str, header=1)
df.rename(columns={'专家':'姓名','联系方式':'手机'}, inplace=True)
df['单位'] = df['单位'].ffill()
df = df.dropna(subset=['姓名','手机'])
df['单位'] = df['单位'].str.replace(r'\s+','',regex=True)

with open('scripts/gen_expert_insert_sql.py', encoding='utf-8') as f:
    src = f.read()
ns = {}
m = re.search(r'INST_USCC = \{(.+?)\}\s*\n\n', src, re.DOTALL)
exec('INST_USCC = {' + m.group(1) + '}', ns)
m2 = re.search(r'EXTRA_USCC = \{(.+?)\}\s*\nINST_USCC\.update', src, re.DOTALL)
exec('EXTRA_USCC = {' + m2.group(1) + '}', ns)
ns['INST_USCC'].update(ns['EXTRA_USCC'])
INST_USCC = ns['INST_USCC']

insts = df['单位'].dropna().unique()
uscc_to_names = {}
for inst in insts:
    uscc = INST_USCC.get(inst)
    if uscc:
        uscc_to_names.setdefault(uscc, []).append(inst)

uscc_list = sorted(uscc_to_names.keys())

lines = []
lines.append(f'-- 共需要 {len(uscc_list)} 个机构（按USCC唯一计）')
lines.append('SELECT uscc, name, level, is_ext FROM institutions WHERE uscc IN (')
for i, u in enumerate(uscc_list):
    comma = '' if i == len(uscc_list)-1 else ','
    names = ', '.join(uscc_to_names[u])
    lines.append(f"  '{u}'{comma}  -- {names}")
lines.append(') ORDER BY is_ext DESC, uscc;')

sql = '\n'.join(lines)
with open('scripts/check_inst_exist.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

with open('scripts/needed_uscc.json', 'w', encoding='utf-8') as f:
    json.dump({'total_uscc': len(uscc_list), 'mapping': uscc_to_names}, f, ensure_ascii=False, indent=2)

print('done, total USCC needed:', len(uscc_list))
