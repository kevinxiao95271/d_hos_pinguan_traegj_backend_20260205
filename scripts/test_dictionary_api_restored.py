# -*- coding: utf-8 -*-
"""
测试字典API恢复情况
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试字典API恢复情况")
print("=" * 100)

# 测试所需的字典类型
test_types = [
    'subject_type',      # 主题类型
    'method',            # 运用手法
    'experience_improve', # 改善就医感受
    'quality_topic'      # 医疗质量安全主题
]

success_count = 0
failed_count = 0

for dict_type in test_types:
    print(f"\n[测试] /api/dictionaries/{dict_type}")
    print("-" * 100)
    
    try:
        response = requests.get(f"{BASE_URL}/dictionaries/{dict_type}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  状态: 成功 (200)")
            print(f"  记录数: {len(data)}")
            
            if len(data) > 0:
                print(f"\n  数据示例 (前3条):")
                for i, item in enumerate(data[:3]):
                    print(f"    [{i+1}] code={item.get('code'):<20} label={item.get('label')}")
                
                success_count += 1
            else:
                print(f"  警告: 该类型没有数据！")
                failed_count += 1
        elif response.status_code == 404:
            print(f"  状态: 失败 (404 Not Found)")
            print(f"  错误: API不存在或未恢复")
            failed_count += 1
        else:
            print(f"  状态: 失败 ({response.status_code})")
            print(f"  响应: {response.text[:200]}")
            failed_count += 1
            
    except requests.exceptions.ConnectionError:
        print(f"  状态: 失败 (连接错误)")
        print(f"  错误: 无法连接到服务器，请检查服务是否启动")
        failed_count += 1
    except Exception as e:
        print(f"  状态: 失败 (异常)")
        print(f"  错误: {str(e)}")
        failed_count += 1

print("\n" + "=" * 100)
print("测试结果汇总")
print("=" * 100)
print(f"成功: {success_count}/{len(test_types)}")
print(f"失败: {failed_count}/{len(test_types)}")

if success_count == len(test_types):
    print("\n所有字典API已成功恢复！")
else:
    print("\n部分API测试失败，请检查日志")

# 额外测试：获取所有启用的字典项
print("\n" + "=" * 100)
print("[额外测试] 获取所有启用的字典项")
print("=" * 100)

try:
    response = requests.get(f"{BASE_URL}/dictionaries", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"状态: 成功 (200)")
        print(f"总记录数: {len(data)}")
        
        # 按类型统计
        type_counts = {}
        for item in data:
            t = item.get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print(f"\n各类型分布:")
        for t, count in sorted(type_counts.items()):
            print(f"  {t:<30} {count:>3} 条")
    else:
        print(f"状态: 失败 ({response.status_code})")
except Exception as e:
    print(f"状态: 失败 - {str(e)}")

print("\n" + "=" * 100)
print("测试完成！")
print("=" * 100)
