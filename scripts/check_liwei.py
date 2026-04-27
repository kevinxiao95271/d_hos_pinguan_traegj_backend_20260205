import openpyxl, csv, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205'

# 从专家文件中找李伟的原始行
wb = openpyxl.load_workbook(os.path.join(BASE, '书审专家单位(1)-0410.xlsx'), read_only=True)
ws = wb['书审']
cur_eg = None
print('=== 专家文件中所有"李伟"行 ===')
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i < 2: continue
    if row[0]: cur_eg = str(row[0]).strip()
    if row[3] and '李伟' in str(row[3]):
        print(f'  组: {cur_eg} | 行{i+1} | 原始数据: {[str(v) if v is not None else "" for v in row[:10]]}')
wb.close()

# 从生产库专家数据中搜索所有叫"李伟"的
print()
print('=== 生产库中所有"李伟" ===')
with open(os.path.join(BASE, '专家数据含机构ID0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        if '李伟' in str(row.get('name', '')):
            phone = re.sub(r'\D', '', str(row['phone'] or ''))
            print(f'  name={row["name"]} | phone={phone} | institution_id={row["institution_id"]} | institution_name={row["institution_name"]}')

# 检查手机号 13958009748 对应谁
print()
print('=== 手机 13958009748 在生产库中的记录 ===')
with open(os.path.join(BASE, '专家数据含机构ID0410.csv'), encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        phone = re.sub(r'\D', '', str(row['phone'] or ''))
        if phone == '13958009748':
            print(f'  name={row["name"]} | institution_id={row["institution_id"]} | institution_name={row["institution_name"]}')
