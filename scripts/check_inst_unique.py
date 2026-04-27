# -*- coding: utf-8 -*-
import pandas as pd
import json

# ---- 1. 读取新专家名单，去掉重复手机号的人 ----
df = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', header=1, engine='openpyxl')
df.columns = ['unit', 'name', 'field', 'background', 'position', 'phone']
df = df.dropna(subset=['name'])
df['unit'] = df['unit'].astype(str).str.strip().str.replace('\n', '').str.replace(' ', '')
df['name'] = df['name'].astype(str).str.strip()
df['phone'] = df['phone'].astype(str).str.strip().str.replace('.0', '', regex=False)

# 找出重复手机号
dup_mask = df.duplicated(subset=['phone'], keep=False)
df_clean = df[~dup_mask].copy()
print(f'原始人数: {len(df)}，去掉重复手机后剩余: {len(df_clean)}')

# ---- 2. 提取所有唯一机构名 ----
units = sorted(set(str(u).strip() for u in df_clean['unit'].unique() if str(u).strip() not in ('nan', '', 'None', 'NaN')))
print(f'需要核查的机构数: {len(units)}')

# ---- 3. 读取 const_init ----
ci = pd.read_csv('scripts/init_prod_const_init_institutions.csv',
                 encoding='utf-8-sig', dtype=str,
                 usecols=['code', 'uscc', 'name', 'city', 'level'])

# A 类：之前已确认的名称映射（别名→const_init实际名称）
alias_map = {
    '嘉兴市中医院':     '嘉兴市中医医院',
    '宁波医疗中心李惠利医院': '宁波市医疗中心李惠利医院',
    '宁波市第一医院':   '宁波大学附属第一医院',
    '宁波市第九医院':   '宁波市第九医院（宁波市第一医院江北分院、宁波市江北区人民医院）',
    '杭州市妇产科医院': '杭州市妇产科医院（杭州市妇幼保健院）钱塘院区',
    '湖州市第一人民医院': '湖州师范学院附属第一医院（湖州市第一人民医院）',
    '萧山医院':         '浙江萧山医院',
    # B类：const_init中名称略不同
    '萧山区第一人民医院': '杭州市萧山区第一人民医院',
    '杭州市红会医院':   '杭州市红十字会医院',
    '树兰(安吉)医院':  '树兰（安吉）医院',
}

# 特殊机构（非医疗或数据异常，不需要找 const_init）
special = {'省医管中心', '浙江大学', '浙江省质量协会', '公司'}

results = []
issues = []

for unit in units:
    if unit in special:
        results.append({'unit': unit, 'status': '⚠️ 非医疗机构', 'uscc': '', 'ci_name': '', 'level': '', 'unique': ''})
        continue

    lookup_name = alias_map.get(unit, unit)
    matched = ci[ci['name'] == lookup_name]

    # 只看主体医院（排除院区/门诊部/卫生室等）
    main = matched[matched['level'].isin(['三级', '二级', '一级'])]
    main_exact = matched[matched['name'] == lookup_name]

    if len(main_exact) == 0:
        status = '❌ 未找到'
        issues.append({'unit': unit, 'reason': 'not found'})
        results.append({'unit': unit, 'status': status, 'uscc': '', 'ci_name': '', 'level': '', 'unique': ''})
    else:
        # 取等级最高的唯一主体
        graded = main_exact[main_exact['level'].isin(['三级', '二级', '一级'])]
        if len(graded) == 1:
            row = graded.iloc[0]
            lv = row['level']
            status = '✅ 唯一三级' if lv == '三级' else f'⚠️ 唯一但{lv}'
            if lv != '三级':
                issues.append({'unit': unit, 'reason': f'level={lv}'})
            results.append({'unit': unit, 'status': status, 'uscc': row['uscc'],
                            'ci_name': row['name'], 'level': lv, 'unique': 'YES'})
        elif len(graded) > 1:
            # 多条主体记录
            rows = graded[['uscc', 'name', 'level']].to_dict('records')
            issues.append({'unit': unit, 'reason': f'multiple graded rows: {len(graded)}', 'rows': rows})
            results.append({'unit': unit, 'status': f'⚠️ 多条等级记录({len(graded)})',
                            'uscc': graded.iloc[0]['uscc'], 'ci_name': str([r["name"] for r in rows]),
                            'level': graded.iloc[0]['level'], 'unique': 'MULTI'})
        else:
            # 找到了但没有等级字段是三级
            row = main_exact.iloc[0]
            lv = row['level']
            status = f'⚠️ 找到但level={lv}'
            issues.append({'unit': unit, 'reason': f'level={lv}'})
            results.append({'unit': unit, 'status': status, 'uscc': row['uscc'],
                            'ci_name': row['name'], 'level': lv, 'unique': 'YES'})

with open('scripts/tmp_inst_unique_check.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'issues': issues}, f, ensure_ascii=False, indent=2)
print('Done.')
