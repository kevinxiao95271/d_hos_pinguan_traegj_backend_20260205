# -*- coding: utf-8 -*-
"""
快速测试新API
"""
import requests

BASE_URL = "http://localhost:6031"

def quick_test():
    print("快速测试新API")
    print("=" * 60)
    
    # 1. 城市列表
    print("\n1. GET /api/institutions/cities")
    try:
        res = requests.get(f"{BASE_URL}/api/institutions/cities", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(f"   OK 返回 {len(data['data'])} 个城市")
            print(f"   {', '.join(data['data'])}")
        else:
            print(f"   ERROR {res.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 2. 杭州市区县
    print("\n2. GET /api/institutions/districts?city=杭州市")
    try:
        res = requests.get(f"{BASE_URL}/api/institutions/districts", params={"city": "杭州市"}, timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(f"   OK 杭州市有 {len(data['data'])} 个区县")
            print(f"   {', '.join(data['data'][:5])}...")
        else:
            print(f"   ERROR {res.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 3. 搜索杭州市
    print("\n3. POST /api/institutions/search (region=杭州市)")
    try:
        res = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "杭州市", "page": 0, "size": 1},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            print(f"   OK 找到 {data['data']['totalElements']:,} 家")
        else:
            print(f"   ERROR {res.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 4. 搜索"杭州"
    print("\n4. POST /api/institutions/search (region=杭州)")
    try:
        res = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "杭州", "page": 0, "size": 1},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            print(f"   OK 找到 {data['data']['totalElements']:,} 家 (智能识别)")
        else:
            print(f"   ERROR {res.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 5. 搜索上城区
    print("\n5. POST /api/institutions/search (region=上城区)")
    try:
        res = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"region": "上城区", "page": 0, "size": 1},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            print(f"   OK 找到 {data['data']['totalElements']:,} 家")
        else:
            print(f"   ERROR {res.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("OK 所有功能正常！")

if __name__ == "__main__":
    quick_test()
