# -*- coding: utf-8 -*-
"""
详细检查数据库中的等级分布
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("数据库等级数据详细分析")
print("=" * 100)

# 测试各种等级的机构数量
test_levels = [
    '一级', '一甲', '一乙', '一丙',
    '二级', '二甲', '二乙', '二丙',
    '三级', '三甲', '三乙', '三丙',
    '未分级', '未定等', '无等级'
]

print("\n[测试] 逐个等级搜索统计...")
print("-" * 100)
print(f"{'等级':<15} {'机构数量':<10}")
print("-" * 100)

level_counts = {}

for level in test_levels:
    try:
        response = requests.post(
            f"{BASE_URL}/institutions/search",
            json={
                "keyword": "",
                "region": "",
                "level": level,
                "page": 0,
                "size": 1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                total = data.get('data', {}).get('totalElements', 0)
                level_counts[level] = total
                status = "[有数据]" if total > 0 else "[无数据]"
                print(f"{level:<15} {total:<10} {status}")
        else:
            print(f"{level:<15} {'错误':<10} HTTP {response.status_code}")
            
    except Exception as e:
        print(f"{level:<15} {'错误':<10} {str(e)[:30]}")

# 统计
print("\n" + "=" * 100)
print("统计结果")
print("=" * 100)

has_data = {k: v for k, v in level_counts.items() if v > 0}
no_data = {k: v for k, v in level_counts.items() if v == 0}

print(f"\n[有数据的等级] ({len(has_data)} 种):")
for level, count in sorted(has_data.items(), key=lambda x: x[1], reverse=True):
    print(f"  {level:<15} : {count:>6} 个")

print(f"\n[无数据的等级] ({len(no_data)} 种):")
for level in sorted(no_data.keys()):
    print(f"  {level}")

# 重点对比
print("\n" + "=" * 100)
print("重点对比（用户关注的等级）")
print("=" * 100)

key_levels = {
    '三甲': level_counts.get('三甲', 0),
    '三级': level_counts.get('三级', 0),
    '二甲': level_counts.get('二甲', 0),
    '二级': level_counts.get('二级', 0),
}

print(f"\n用户说：Excel中 '三级'、'二级' 有数据，'三甲' 没有数据")
print(f"数据库实际情况:\n")

for level, count in key_levels.items():
    if count > 0:
        print(f"  {level:<10} : {count:>6} 个 [有数据]")
    else:
        print(f"  {level:<10} : {count:>6} 个 [无数据]")

print("\n[对比结论]")
if key_levels['三级'] > 0 or key_levels['二级'] > 0:
    if key_levels['三甲'] == 0:
        print("  [符合] 符合用户描述：数据库中 '三级'/'二级' 有数据，'三甲' 无数据")
        print("  [结论] 说明数据库导入的是Excel数据，而不是其他来源")
    else:
        print("  [不符合] 不符合用户描述：数据库中 '三甲' 也有数据")
else:
    if key_levels['三甲'] > 0:
        print("  [完全相反] 数据库中 '三甲' 有数据，但 '三级'/'二级' 无数据")
        print("  [结论] 说明数据库可能不是从Excel导入的")

print("\n" + "=" * 100)
