import openpyxl, csv, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205'

# 读生产库专家数据
phone2db = {}
name2db  = {}
with open(os.path.join(BASE, '专家数据含机构ID0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        phone = re.sub(r'\D', '', str(row['phone'] or ''))
        name  = str(row['name'] or '').strip()
        info  = {
            'institution_id':   int(row['institution_id']) if row['institution_id'] else None,
            'institution_name': str(row['institution_name'] or '').strip(),
        }
        if phone: phone2db[phone] = info
        if name:  name2db[name]  = info

def lookup(name, phone_raw):
    phone = re.sub(r'\D', '', str(phone_raw or ''))
    if phone and phone in phone2db: return phone2db[phone], 'phone'
    if name  and name  in name2db:  return name2db[name],  'name'
    return None, None

# 读专家分组文件
wb = openpyxl.load_workbook(os.path.join(BASE, '书审专家单位(1)-0410.xlsx'), read_only=True)
ws = wb['书审']

ok_list      = []   # 机构一致
mismatch_list = []  # 机构不一致
notfound_list = []  # 生产库未找到

cur_eg = None
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i < 2: continue
    if row[0]: cur_eg = str(row[0]).strip()
    if not row[3]: continue
    name      = str(row[3]).strip()
    phone_raw = str(row[7] or '').strip()
    unit_excel = str(row[5] or '').strip()   # 专家文件里的"单位"列

    db_info, match_by = lookup(name, phone_raw)

    if db_info is None:
        notfound_list.append({
            'group': cur_eg, 'name': name, 'phone': phone_raw,
            'excel_unit': unit_excel,
        })
        continue

    db_unit = db_info['institution_name']
    db_id   = db_info['institution_id']
    matched_by = match_by

    # 简单判断是否一致（Excel里往往是缩写，做包含关系判断）
    consistent = (unit_excel in db_unit) or (db_unit in unit_excel) or (unit_excel == db_unit)

    entry = {
        'group': cur_eg, 'name': name, 'phone': phone_raw,
        'excel_unit': unit_excel, 'db_unit': db_unit, 'db_id': db_id,
        'match_by': matched_by,
    }
    if consistent:
        ok_list.append(entry)
    else:
        mismatch_list.append(entry)

wb.close()

# 输出
print(f'{"="*70}')
print(f'总专家数: {len(ok_list)+len(mismatch_list)+len(notfound_list)}')
print(f'  机构一致: {len(ok_list)}')
print(f'  机构不一致: {len(mismatch_list)}')
print(f'  生产库未找到: {len(notfound_list)}')
print(f'{"="*70}')

if mismatch_list:
    print(f'\n【机构不一致】（{len(mismatch_list)} 人）')
    print(f'{"组":4s} {"姓名":10s} {"手机":14s} {"Excel单位":20s} → {"生产库机构"}')
    print('-'*80)
    for e in mismatch_list:
        print(f'{e["group"]:4s} {e["name"]:10s} {e["phone"]:14s} {e["excel_unit"]:20s} → {e["db_unit"]}  (id={e["db_id"]})')

if notfound_list:
    print(f'\n【生产库未找到】（{len(notfound_list)} 人）')
    print(f'{"组":4s} {"姓名":10s} {"手机":14s} {"Excel单位"}')
    print('-'*60)
    for e in notfound_list:
        print(f'{e["group"]:4s} {e["name"]:10s} {e["phone"]:14s} {e["excel_unit"]}')
