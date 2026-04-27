import pandas as pd
import re
import json

# 1. Extract institution names from init SQL
with open('scripts/init_prod_institutions_and_reviewers.sql', encoding='utf-8') as f:
    sql_text = f.read()

# Parse institution names from INSERT VALUES section
sql_insts = re.findall(r"INSERT INTO institutions.*?VALUES(.*?)ON DUPLICATE", sql_text, re.DOTALL)
inst_names_in_sql = re.findall(r"\('([^']+)'", sql_insts[0]) if sql_insts else []
print('Institutions in SQL:', len(inst_names_in_sql))

# 2. Get all institution names from new expert file
df_new = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', header=1, engine='openpyxl')
df_new.columns = ['unit', 'name', 'field', 'background', 'position', 'phone']
df_new = df_new.dropna(subset=['name'])
df_new['unit_clean'] = df_new['unit'].astype(str).str.strip().str.replace('\n', '').str.replace(' ', '')

# Filter out empty / nan
new_units = set(str(u).strip() for u in df_new['unit_clean'].unique() if str(u).strip() not in ('', 'nan', 'NaN', 'None'))
print('Unique units in new file:', len(new_units))

# 3. Exact match check
sql_set = set(inst_names_in_sql)
exact_match = new_units & sql_set
exact_miss = new_units - sql_set

print('\nNot found in SQL (exact):', len(exact_miss))
for u in sorted(exact_miss):
    print('  MISS:', u)

print('\nFound in SQL (exact):', len(exact_match))
for u in sorted(exact_match):
    print('  OK:', u)

result = {
    'sql_institutions_count': len(inst_names_in_sql),
    'new_file_units_count': len(new_units),
    'exact_match_count': len(exact_match),
    'not_in_sql_count': len(exact_miss),
    'not_in_sql': sorted(exact_miss),
    'exact_match': sorted(exact_match),
    'sql_institutions': sorted(inst_names_in_sql),
}
with open('scripts/tmp_inst_compare.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\nSaved to scripts/tmp_inst_compare.json')
