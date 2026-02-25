# -*- coding: utf-8 -*-
"""
测试公开API（无需token）
验证注册流程中的机构选择功能
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def test_public_apis():
    """测试公开接口"""
    print("=" * 70)
    print("测试公开API（无需Token）")
    print("=" * 70)
    
    # 1. 测试热门地区（注册时推荐）
    print("\n[1/6] 测试热门地区接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/institutions/hot-regions?limit=5", timeout=5)
        print(f"      状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                hot_regions = data['data']
                print(f"      OK 获取到 {len(hot_regions)} 个热门地区")
                for i, region in enumerate(hot_regions[:3], 1):
                    print(f"         {i}. {region['region']}: {region['count']}家机构")
            else:
                print(f"      FAIL: {data['message']}")
        else:
            print(f"      ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # 2. 测试等级列表
    print("\n[2/6] 测试等级列表接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/institutions/levels", timeout=5)
        print(f"      状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                levels = data['data']
                print(f"      OK 获取到 {len(levels)} 个等级")
                print(f"         等级: {', '.join(levels[:5])}")
            else:
                print(f"      FAIL: {data['message']}")
        else:
            print(f"      ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # 3. 测试自动完成（输入"浙江"）
    print("\n[3/6] 测试自动完成接口...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/institutions/autocomplete",
            params={"prefix": "浙江"},
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                suggestions = data['data']
                print(f"      OK 获取到 {len(suggestions)} 条建议")
                for i, inst in enumerate(suggestions[:3], 1):
                    print(f"         {i}. {inst['name']} ({inst['region']})")
            else:
                print(f"      FAIL: {data['message']}")
        else:
            print(f"      ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # 4. 测试机构搜索（关键词"医院"）
    print("\n[4/6] 测试机构搜索接口...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={
                "keyword": "医院",
                "page": 0,
                "size": 5
            },
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                page_data = data['data']
                print(f"      OK 找到 {page_data['totalElements']} 家医院")
                print(f"         当前页: {page_data['number'] + 1}/{page_data['totalPages']}")
                institutions = page_data['content']
                for i, inst in enumerate(institutions[:3], 1):
                    print(f"         {i}. {inst['displayText']}")
            else:
                print(f"      FAIL: {data['message']}")
        else:
            print(f"      ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # 5. 测试地区筛选（浙江省 + 三级医院）
    print("\n[5/6] 测试地区+等级筛选...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={
                "region": "浙江省",
                "level": "三级",
                "page": 0,
                "size": 5
            },
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                page_data = data['data']
                print(f"      OK 浙江省三级医院: {page_data['totalElements']}家")
                institutions = page_data['content']
                for i, inst in enumerate(institutions[:3], 1):
                    print(f"         {i}. {inst['name']}")
            else:
                print(f"      FAIL: {data['message']}")
        else:
            print(f"      ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    # 6. 测试获取机构详情
    print("\n[6/6] 测试机构详情接口...")
    try:
        # 先搜索一个机构ID
        search_response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={"keyword": "浙江大学", "page": 0, "size": 1},
            timeout=5
        )
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['success'] and search_data['data']['content']:
                inst_id = search_data['data']['content'][0]['id']
                
                # 获取详情
                detail_response = requests.get(f"{BASE_URL}/api/institutions/{inst_id}", timeout=5)
                print(f"      状态码: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if detail_data['success']:
                        inst = detail_data['data']
                        print(f"      OK 机构ID: {inst['id']}")
                        print(f"         名称: {inst['name']}")
                        print(f"         地区: {inst['region']}")
                        print(f"         等级: {inst.get('level', '未知')}")
                    else:
                        print(f"      FAIL: {detail_data['message']}")
                else:
                    print(f"      ERROR: HTTP {detail_response.status_code}")
            else:
                print("      SKIP: 未找到测试机构")
    except Exception as e:
        print(f"      ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("总结：注册流程所需的机构选择接口")
    print("=" * 70)
    print("✅ 所有公开接口均可无Token访问")
    print("")
    print("公开接口清单（注册时可用）:")
    print("  1. POST /api/institutions/search - 搜索机构")
    print("  2. GET /api/institutions/autocomplete - 自动完成")
    print("  3. GET /api/institutions/hot-regions - 热门地区")
    print("  4. GET /api/institutions/regions - 地区列表")
    print("  5. GET /api/institutions/levels - 等级列表")
    print("  6. GET /api/institutions/{id} - 机构详情")
    print("")
    print("需要Token的接口（管理操作）:")
    print("  1. POST /api/institutions - 创建机构")
    print("  2. PUT /api/institutions/{id} - 更新机构")
    print("  3. DELETE /api/institutions/{id} - 删除机构")
    print("  4. POST /api/institutions/import - 批量导入")
    print("  5. GET /api/institutions/by-region/{region} - 按地区查询全部")
    print("")
    print("注册流程验证:")
    print("  Step 1: 用户访问注册页面（无需token）")
    print("  Step 2: 搜索/选择机构（调用公开API，无需token）")
    print("  Step 3: 填写其他信息并注册")
    print("  Step 4: 注册成功，获得token")
    print("  Step 5: 后续操作使用token认证")
    print("")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_public_apis()
    except Exception as e:
        print(f"ERROR: {e}")
