#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析26%可能来自哪里"""

# 地区分布数据
region_counts = {
    "杭州": 17,
    "舟山": 15,
    "宁波": 3,
    "温州": 2,
    "绍兴": 2,
    "嘉兴": 1,
    "台州": 1,
    "湖州": 1,
    "金华": 1,
    "衢州": 1,
    "丽水": 1
}

# 主题类型分布数据
subject_counts = {
    "病人照护": 10,
    "医疗信息": 8,
    "其他": 6,
    "满意度": 4,
    "时间效率": 4,
    "病历质量": 4,
    "安全环境": 3,
    "医疗质量与安全": 2,
    "成本效益": 2,
    "流程改造": 1,
    "教育训练": 1
}

total_regions = sum(region_counts.values())
total_subjects = sum(subject_counts.values())

print("=" * 80)
print("分析26%可能来自哪里")
print("=" * 80)

print("\n1. 地区分布分析:")
print("-" * 80)
print(f"{'地区':<15} {'数量':<10} {'占比':<10}")
print("-" * 80)

for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_regions * 100)
    print(f"{region:<15} {count:<10} {percentage:>6.2f}%")

print("-" * 80)
print(f"{'总计':<15} {total_regions:<10} 100.00%")

# 尝试找出26%的组合
print("\n2. 尝试找出26%的组合:")
print("-" * 80)

# 可能性1: 小地区合并
small_regions = {k: v for k, v in region_counts.items() if v <= 2}
small_total = sum(small_regions.values())
small_percentage = (small_total / total_regions * 100)

print(f"小地区（≤2条）合并: {list(small_regions.keys())}")
print(f"  数量: {small_total}")
print(f"  占比: {small_percentage:.2f}%")

# 可能性2: 除了前3名的其他地区
top3 = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:3]
top3_names = [x[0] for x in top3]
other_regions = {k: v for k, v in region_counts.items() if k not in top3_names}
other_total = sum(other_regions.values())
other_percentage = (other_total / total_regions * 100)

print(f"\n除前3名外的其他地区: {list(other_regions.keys())}")
print(f"  数量: {other_total}")
print(f"  占比: {other_percentage:.2f}%")

# 可能性3: 除了前2名的其他地区
top2 = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:2]
top2_names = [x[0] for x in top2]
other_regions2 = {k: v for k, v in region_counts.items() if k not in top2_names}
other_total2 = sum(other_regions2.values())
other_percentage2 = (other_total2 / total_regions * 100)

print(f"\n除前2名外的其他地区: {list(other_regions2.keys())}")
print(f"  数量: {other_total2}")
print(f"  占比: {other_percentage2:.2f}%")

print("\n3. 主题类型分布分析:")
print("-" * 80)
print(f"{'主题类型':<20} {'数量':<10} {'占比':<10}")
print("-" * 80)

for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_subjects * 100)
    marker = " ← 这是'其他'" if subject == "其他" else ""
    print(f"{subject:<20} {count:<10} {percentage:>6.2f}%{marker}")

print("-" * 80)
print(f"{'总计':<20} {total_subjects:<10} 100.00%")

print("\n4. 可能的解释:")
print("-" * 80)

if abs(other_percentage2 - 26) < 1:
    print(f"✅ 可能性最高: 前端将除杭州、舟山外的其他地区合并为'其他'")
    print(f"   占比: {other_percentage2:.2f}% ≈ 26%")
elif abs(small_percentage - 26) < 1:
    print(f"✅ 可能性: 前端将报名数≤2的地区合并为'其他'")
    print(f"   占比: {small_percentage:.2f}% ≈ 26%")
else:
    print(f"⚠️  26%不匹配任何已知的组合")
    print(f"   建议检查前端的分类逻辑")

print("\n5. 建议:")
print("-" * 80)
print("如果前端看到'其他'占26%，可能是前端的图表库或代码中有自定义的分类逻辑：")
print("  - 检查是否有 'Top N + 其他' 的逻辑")
print("  - 检查是否有按阈值合并小分类的逻辑")
print("  - 检查图表配置中是否有自动合并选项")
print("  - 清除浏览器缓存和localStorage")
