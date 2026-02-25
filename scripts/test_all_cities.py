# -*- coding: utf-8 -*-
"""
测试所有11个城市的智能搜索
"""
import requests

BASE_URL = "http://localhost:6031"

# 预期结果（基于数据分析）
EXPECTED_RESULTS = {
    "杭州市": 6298,
    "温州市": 6118,
    "金华市": 4864,
    "宁波市": 4563,
    "台州市": 3728,
    "绍兴市": 2935,
    "丽水市": 1849,
    "衢州市": 1766,
    "嘉兴市": 1651,
    "湖州市": 1174,
    "舟山市": 585
}

def test_all_cities():
    """测试所有城市"""
    print("=" * 80)
    print("测试所有11个地级市的智能搜索")
    print("=" * 80)
    
    all_success = True
    total_tested = 0
    total_found = 0
    
    for city, expected_count in sorted(EXPECTED_RESULTS.items(), key=lambda x: x[1], reverse=True):
        try:
            response = requests.post(
                f"{BASE_URL}/api/institutions/search",
                json={"region": city, "page": 0, "size": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    actual_count = data['data']['totalElements']
                    total_tested += 1
                    total_found += actual_count
                    
                    # 允许±5%的误差
                    tolerance = expected_count * 0.05
                    is_match = abs(actual_count - expected_count) <= tolerance
                    
                    status = "[OK]" if is_match else "[WARN]"
                    print(f"{status} {city:10s} 预期:{expected_count:6,} 实际:{actual_count:6,}")
                    
                    if not is_match:
                        all_success = False
                        diff = actual_count - expected_count
                        print(f"       差异: {diff:+,} ({diff/expected_count*100:+.1f}%)")
                else:
                    print(f"[ERROR] {city} API返回失败: {data['message']}")
                    all_success = False
            else:
                print(f"[ERROR] {city} HTTP {response.status_code}")
                all_success = False
        except Exception as e:
            print(f"[ERROR] {city} 异常: {e}")
            all_success = False
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"测试城市数: {total_tested}/11")
    print(f"查询到的机构总数: {total_found:,} 家")
    print(f"预期机构总数: {sum(EXPECTED_RESULTS.values()):,} 家")
    print(f"覆盖率: {total_found/36050*100:.1f}%")
    
    if all_success:
        print("\n[OK] 所有城市测试通过！")
    else:
        print("\n[WARN] 部分城市结果与预期不符")

if __name__ == "__main__":
    test_all_cities()
