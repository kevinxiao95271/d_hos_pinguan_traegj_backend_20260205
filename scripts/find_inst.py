import sys, csv
sys.stdout.reconfigure(encoding='utf-8')
path = r'd:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\机构全表0410.csv'

targets = ['杭州市第二人民医院', '丽水中心', '金华中心', '宁波市第一医院', '鄞州人民医院']
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

for t in targets:
    print(f'--- 搜索: {t} ---')
    for row in rows:
        if t in row['name'] or row['name'] in t:
            print(f"  id={row['id']}  name={row['name']}")
