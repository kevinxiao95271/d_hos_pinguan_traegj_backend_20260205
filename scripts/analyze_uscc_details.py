# -*- coding: utf-8 -*-
"""
【详细分析】重复USCC的具体情况
深入查看"多个主医院共享USCC"的真实特征
"""
import pandas as pd
import os

project_root = r"D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205"
excel_file = "2026.1全省医疗机构目录.xlsx"

print("=" * 100)
print("【详细分析】重复USCC的真实情况")
print("=" * 100)

# 读取Excel
file_path = os.path.join(project_root, excel_file)
df = pd.read_excel(file_path)

col_name = 0
col_uscc = 6
col_level = 4
col_region = 1

print(f"\nExcel总记录数: {len(df)}")

# 统计重复USCC
uscc_column = df.iloc[:, col_uscc].astype(str).str.strip()
uscc_counts = uscc_column.value_counts()
duplicates = uscc_counts[uscc_counts > 1]

# 排除特殊值
duplicates_clean = duplicates[~duplicates.index.isin(['nan', '', '000000000000000000'])]

print(f"有效重复USCC数量: {len(duplicates_clean)}")

# 详细分析每个重复USCC
print("\n" + "=" * 100)
print("详细分析重复USCC")
print("=" * 100)

# 分类统计
same_name_count = 0
similar_name_count = 0
different_name_count = 0

same_name_cases = []
similar_name_cases = []
different_name_cases = []

for uscc, count in duplicates_clean.items():
    mask = df.iloc[:, col_uscc].astype(str).str.strip() == uscc
    records = df[mask]
    
    names = []
    levels = []
    regions = []
    
    for idx, row in records.iterrows():
        name = str(row.iloc[col_name]).strip()
        level = str(row.iloc[col_level]).strip() if pd.notna(row.iloc[col_level]) else '未定级'
        region = str(row.iloc[col_region]).strip() if pd.notna(row.iloc[col_region]) else ''
        
        names.append(name)
        levels.append(level)
        regions.append(region)
    
    # 判断是否为分支机构
    branch_keywords = ['门诊部', '医务室', '卫生所', '诊所', '卫生站', '医疗点', '驻']
    
    # 过滤掉分支机构，只看主医院
    main_hospitals = []
    for i, name in enumerate(names):
        is_branch = any(keyword in name for keyword in branch_keywords)
        if not is_branch:
            main_hospitals.append({
                'name': name,
                'level': levels[i],
                'region': regions[i]
            })
    
    # 如果只有1个或0个主医院，跳过（这是正常的）
    if len(main_hospitals) <= 1:
        continue
    
    # 有多个主医院 - 分析名字相似度
    unique_names = list(set([h['name'] for h in main_hospitals]))
    
    if len(unique_names) == 1:
        # 名字完全相同
        same_name_count += 1
        if len(same_name_cases) < 10:  # 只保存前10个案例
            same_name_cases.append({
                'uscc': uscc,
                'count': len(main_hospitals),
                'name': unique_names[0],
                'hospitals': main_hospitals
            })
    else:
        # 名字不完全相同，检查是否相似
        # 提取基础名字（去掉分院、分部等后缀）
        base_names = []
        for name in unique_names:
            base = name
            for suffix in ['分院', '分部', '第一', '第二', '第三', '总院', '本部']:
                base = base.replace(suffix, '')
            base_names.append(base.strip())
        
        unique_base_names = list(set(base_names))
        
        if len(unique_base_names) == 1 or len(unique_names) <= 3:
            # 名字相似（可能是分院）
            similar_name_count += 1
            if len(similar_name_cases) < 10:
                similar_name_cases.append({
                    'uscc': uscc,
                    'count': len(main_hospitals),
                    'names': unique_names,
                    'hospitals': main_hospitals
                })
        else:
            # 名字完全不同
            different_name_count += 1
            if len(different_name_cases) < 10:
                different_name_cases.append({
                    'uscc': uscc,
                    'count': len(main_hospitals),
                    'names': unique_names,
                    'hospitals': main_hospitals
                })

print(f"\n[重新分类统计]")
print(f"1. 名字完全相同的多个主医院: {same_name_count} 个USCC")
print(f"   特征: 机构名称一样，USCC一样，但可能地区或等级不同")
print(f"\n2. 名字相似的多个主医院: {similar_name_count} 个USCC")
print(f"   特征: 可能是分院、分部关系（如XX医院第一分院、第二分院）")
print(f"\n3. 名字完全不同的主医院: {different_name_count} 个USCC")
print(f"   特征: 完全不同的医院共享USCC（这是真正的数据错误）")

# 显示案例
print("\n" + "=" * 100)
print("案例展示")
print("=" * 100)

if same_name_cases:
    print(f"\n【类型1: 名字完全相同】(前5个案例)")
    for i, case in enumerate(same_name_cases[:5], 1):
        print(f"\n{i}. USCC: {case['uscc']}")
        print(f"   机构名称: {case['name']}")
        print(f"   重复次数: {case['count']}")
        print(f"   详细信息:")
        for j, h in enumerate(case['hospitals'][:5], 1):
            print(f"      {j}) 地区: {h['region']}, 等级: {h['level']}")

if similar_name_cases:
    print(f"\n【类型2: 名字相似】(前5个案例)")
    for i, case in enumerate(similar_name_cases[:5], 1):
        print(f"\n{i}. USCC: {case['uscc']}")
        print(f"   重复次数: {case['count']}")
        print(f"   涉及机构:")
        for j, h in enumerate(case['hospitals'][:5], 1):
            print(f"      {j}) {h['name']} [{h['region']}] 等级: {h['level']}")

if different_name_cases:
    print(f"\n【类型3: 名字完全不同 - 真正的数据错误】(前5个案例)")
    for i, case in enumerate(different_name_cases[:5], 1):
        print(f"\n{i}. USCC: {case['uscc']}")
        print(f"   重复次数: {case['count']}")
        print(f"   涉及的完全不同的医院:")
        for j, h in enumerate(case['hospitals'][:5], 1):
            print(f"      {j}) {h['name']} [{h['region']}] 等级: {h['level']}")

# 总结
print("\n" + "=" * 100)
print("结论")
print("=" * 100)

print(f"""
重复USCC分析结果：

1. 名字完全相同的情况 ({same_name_count}个):
   - 这是Excel数据本身就重复录入
   - 可能是同一家医院在不同地区有记录
   - 或者是数据录入错误

2. 名字相似的情况 ({similar_name_count}个):
   - 大多是分院、分部关系
   - 共享主医院的USCC是合理的
   - 类似"平阳县人民医院"的情况

3. 名字完全不同的情况 ({different_name_count}个):
   - 这是真正的数据错误！
   - 完全不同的医院不应该共享USCC
   - 需要数据清洗

实际影响：
- 类型1和2: 可能是合理的业务场景
- 类型3: 必须处理的数据错误

建议：
- 对于类型1: 检查是否为数据重复录入，可能需要去重
- 对于类型2: 保持现状，使用(name+uscc)作为唯一标识
- 对于类型3: 必须核查并修正USCC
""")

print("\n分析完成！")
