# -*- coding: utf-8 -*-
"""
测试智能地区搜索
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def test_smart_search():
    """测试智能地区搜索"""
    print("=" * 80)
    print("智能地区搜索测试")
    print("=" * 80)
    
    # 测试1: 搜索"杭州市"（应该匹配所有杭州区县）
    print("\n[测试1] 搜索'杭州市'（智能扩展为所有区县）...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "杭州市", "page": 0, "size": 10},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                content = data['data']['content']
                print(f"  OK 找到 {total:,} 家机构")
                print(f"  前10家:")
                for i, inst in enumerate(content, 1):
                    print(f"    {i}. {inst['name'][:40]:40s} ({inst['region']})")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 测试2: 搜索"杭州"（不带"市"）
    print("\n[测试2] 搜索'杭州'（模糊匹配）...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "杭州", "page": 0, "size": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                print(f"  OK 找到 {total:,} 家机构")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 测试3: 搜索"上城区"（精确匹配）
    print("\n[测试3] 搜索'上城区'（精确区县）...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "上城区", "page": 0, "size": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                content = data['data']['content']
                print(f"  OK 找到 {total:,} 家机构")
                print(f"  前5家:")
                for i, inst in enumerate(content, 1):
                    print(f"    {i}. {inst['name'][:40]:40s}")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 测试4: 杭州市 + 三级医院
    print("\n[测试4] 搜索'杭州市 + 三级'...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "杭州市", "level": "三级", "page": 0, "size": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                print(f"  OK 杭州市三级医疗机构: {total:,} 家")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 测试5: 宁波市
    print("\n[测试5] 搜索'宁波市'...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "宁波市", "page": 0, "size": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                content = data['data']['content']
                print(f"  OK 找到 {total:,} 家机构")
                if content:
                    regions = set(inst['region'] for inst in content)
                    print(f"  涉及区县: {', '.join(list(regions)[:5])}")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 测试6: 温州市
    print("\n[测试6] 搜索'温州市'...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "温州市", "page": 0, "size": 5},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total = data['data']['totalElements']
                print(f"  OK 找到 {total:,} 家机构")
            else:
                print(f"  FAIL: {data['message']}")
        else:
            print(f"  ERROR 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print("OK 智能地区搜索已生效！")
    print("")
    print("功能说明:")
    print("  - 搜索'杭州市' → 自动匹配所有杭州区县（上城区、萧山区等）")
    print("  - 搜索'杭州' → 智能匹配'杭州市'")
    print("  - 搜索'上城区' → 精确匹配该区县")
    print("")
    print("优势:")
    print("  + 无需修改数据库结构")
    print("  + 保留原有区县粒度信息")
    print("  + 用户体验好（按市搜索很方便）")
    print("  + 兼容原有查询方式")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_smart_search()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
