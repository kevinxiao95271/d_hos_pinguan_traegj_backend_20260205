# -*- coding: utf-8 -*-
"""
验证部署结果
"""
import requests
import json

BASE_URL = "http://81.71.44.180:6031"

print("=" * 100)
print("验证部署结果")
print("=" * 100)

# 1. 健康检查
print("\n[1] 健康检查")
try:
    response = requests.get(f"{BASE_URL}/actuator/health", timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    if response.status_code == 200 and response.json().get('status') == 'UP':
        print("[OK] Health check passed")
    else:
        print("[FAIL] Health check failed")
except Exception as e:
    print(f"[FAIL] Health check failed: {e}")

# 2. 测试机构搜索API（无需认证）
print("\n[2] 测试机构搜索API（POST /api/institutions/search）")
try:
    response = requests.post(
        f"{BASE_URL}/api/institutions/search",
        json={
            "city": "杭州市",
            "keyword": "人民"
        },
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            content = data['data']['content']
            print(f"[OK] Search success, returned {len(content)} results")
            if len(content) > 0:
                first = content[0]
                print(f"  First: {first['name']} [{first.get('level', 'N/A')}]")
                # 验证排序（三级医院应该排在前面）
                top3_levels = [item.get('level') for item in content[:3]]
                print(f"  Top 3 levels: {top3_levels}")
        else:
            print(f"[FAIL] API returned failure: {data.get('message')}")
    else:
        print(f"[FAIL] Request failed, status: {response.status_code}")
        print(response.text[:500])
except Exception as e:
    print(f"[FAIL] Test failed: {e}")

# 3. 测试GET搜索API
print("\n[3] 测试机构搜索API（GET /api/institutions/search）")
try:
    response = requests.get(
        f"{BASE_URL}/api/institutions/search",
        params={
            "keyword": "浙江大学",
            "page": 0,
            "size": 10
        },
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            content = data['data']['content']
            print(f"[OK] Search success, returned {len(content)} results")
            for i, item in enumerate(content[:3], 1):
                print(f"  {i}. {item['name']} [{item.get('level', 'N/A')}]")
        else:
            print(f"[FAIL] API returned failure: {data.get('message')}")
    else:
        print(f"[FAIL] Request failed, status: {response.status_code}")
except Exception as e:
    print(f"[FAIL] Test failed: {e}")

# 4. 测试字典API
print("\n[4] 测试字典API（GET /api/dictionaries/institution_level）")
try:
    response = requests.get(f"{BASE_URL}/api/dictionaries/institution_level", timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            items = data['data']
            print(f"[OK] Success, got {len(items)} level options")
            for item in items:
                print(f"  - {item['label']} (code: {item['code']})")
        else:
            print(f"[FAIL] API returned failure: {data.get('message')}")
    else:
        print(f"[FAIL] Request failed, status: {response.status_code}")
except Exception as e:
    print(f"[FAIL] Test failed: {e}")

print("\n" + "=" * 100)
print("验证完成！")
print("=" * 100)
print(f"\n服务地址: {BASE_URL}")
print(f"API文档: {BASE_URL}/swagger-ui.html")
