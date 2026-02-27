# -*- coding: utf-8 -*-
"""
检查数据库中实际的等级值分布
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("检查数据库实际等级值分布")
print("=" * 100)

# 测试各种可能的等级值
test_levels = [
    '一级', '二级', '三级',
    '未定级', '无级别', '无等级',
    # 可能的其他变体
    '未分级', '未定等', '无定级',
    ''  # 空字符串
]

print("\n逐个测试各等级值的机构数量:")
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
                
                display_name = level if level else '[空字符串]'
                if total > 0:
                    print(f"  {display_name:<15} : {total:>6} 个 ✓")
                else:
                    print(f"  {display_name:<15} : {total:>6} 个")
    except Exception as e:
        print(f"  {level:<15} : 错误 - {e}")

# 统计总数
print("\n" + "=" * 100)
print("统计汇总")
print("=" * 100)

has_data = {k: v for k, v in level_counts.items() if v > 0}
total_with_level = sum(has_data.values())

print(f"\n有数据的等级值 ({len(has_data)} 种):")
for level, count in sorted(has_data.items(), key=lambda x: x[1], reverse=True):
    display_name = level if level else '[空字符串]'
    print(f"  {display_name:<15} : {count:>6} 个")

print(f"\n总计: {total_with_level} 个")

# 与Excel对比
print("\n" + "=" * 100)
print("与Excel数据对比")
print("=" * 100)

excel_data = {
    '一级': 223,
    '二级': 253,
    '三级': 164,
    '未定级': 24732,
    '无级别': 1675,
    '[空值/无等级]': 14839
}

print("\n期望的数据分布（根据Excel）:")
for level, count in excel_data.items():
    db_count = level_counts.get(level.replace('[空值/无等级]', ''), '?')
    match = '✓' if db_count == count else '✗'
    print(f"  {level:<20} : Excel {count:>6} 个, 数据库 {str(db_count):>6} 个 {match}")

print("\n总计（Excel）:", sum(excel_data.values()), "个")

# 无条件查询总数
response = requests.post(
    f"{BASE_URL}/institutions/search",
    json={"keyword": "", "region": "", "level": "", "page": 0, "size": 1},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        db_total = data.get('data', {}).get('totalElements', 0)
        print("总计（数据库）:", db_total, "个")
        
        if db_total != sum(excel_data.values()):
            print("\n[警告] 数据库总数与Excel不一致！")
            print(f"  差异: {db_total - sum(excel_data.values())} 个")

print("\n" + "=" * 100)
