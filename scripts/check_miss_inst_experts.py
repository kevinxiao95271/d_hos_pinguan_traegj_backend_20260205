# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', header=1, engine='openpyxl')
df.columns = ['unit', 'name', 'field', 'background', 'position', 'phone']
df = df.dropna(subset=['name'])
df['unit_clean'] = df['unit'].astype(str).str.strip().str.replace('\n','').str.replace(' ','')

miss_units = [
    '丽水市人民医院', '义乌市中心医院', '公司', '台州市第一人民医院', '嘉兴市中医院',
    '宁波医疗中心李惠利医院', '宁波市第一医院', '宁波市第九医院', '宁波市鄞州第二医院',
    '杭州市妇产科医院', '杭州市第二人民医院', '杭州市红会医院', '树兰(安吉)医院',
    '浙江中医药大学附属第二医院', '浙江大学', '浙江省立同德医院', '浙江省质量协会',
    '温州市人民医院', '湖州市第一人民医院', '瑞安市人民医院', '省医管中心',
    '萧山区第一人民医院', '萧山医院'
]

rows = df[df['unit_clean'].isin(miss_units)][['unit_clean', 'name', 'position', 'phone']].to_dict('records')
with open('scripts/tmp_miss_inst_experts.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print('Experts in missing inst:', len(rows))
for r in rows:
    print(f"  [{r['unit_clean']}] {r['name']} / {r['position']} / {r['phone']}")
