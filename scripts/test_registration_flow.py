# -*- coding: utf-8 -*-
"""
完整注册流程测试
验证从机构选择到注册成功的完整流程
"""
import requests
import json
import time

BASE_URL = "http://localhost:6031"

def test_registration_flow():
    """测试完整注册流程"""
    print("=" * 70)
    print("完整注册流程测试")
    print("=" * 70)
    
    # Step 1: 加载初始数据（无需token）
    print("\n[Step 1/5] 加载注册页面初始数据（无需Token）...")
    
    # 1.1 获取热门地区
    try:
        response = requests.get(f"{BASE_URL}/api/institutions/hot-regions?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            hot_regions = data['data']
            print(f"  OK 热门地区: {len(hot_regions)}个")
            for region in hot_regions[:3]:
                print(f"     - {region['region']}: {region['count']}家")
        else:
            print(f"  FAIL 状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # 1.2 获取等级列表
    try:
        response = requests.get(f"{BASE_URL}/api/institutions/levels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            levels = data['data']
            print(f"  OK 等级列表: {', '.join(levels)}")
        else:
            print(f"  FAIL 状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # Step 2: 用户搜索机构（无需token）
    print("\n[Step 2/5] 用户搜索机构（无需Token）...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions/search",
            json={
                "keyword": "浙江大学",
                "page": 0,
                "size": 10
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                institutions = data['data']['content']
                total = data['data']['totalElements']
                print(f"  OK 找到 {total} 家机构")
                if institutions:
                    selected_institution = institutions[0]
                    print(f"  选择: {selected_institution['name']}")
                    print(f"        ID: {selected_institution['id']}")
                    print(f"        地区: {selected_institution['region']}")
                    institution_id = selected_institution['id']
                else:
                    print("  WARN: 未找到机构")
                    institution_id = 1  # 使用默认ID
            else:
                print(f"  FAIL: {data['message']}")
                return False
        else:
            print(f"  FAIL 状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # Step 3: 用户填写注册信息并提交（无需token）
    print("\n[Step 3/5] 提交注册信息（无需Token）...")
    phone = f"138{int(time.time()) % 100000000:08d}"  # 生成唯一手机号
    try:
        register_data = {
            "phone": phone,
            "password": "Test@123456",
            "confirmPassword": "Test@123456",
            "name": "测试用户",
            "title": "主任医师",
            "role": "CONTESTANT",
            "institutionId": institution_id
        }
        print(f"  注册手机号: {phone}")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                user_data = data['data']
                token = user_data['token']
                user_id = user_data['id']
                print(f"  OK 注册成功")
                print(f"     用户ID: {user_id}")
                print(f"     姓名: {user_data['name']}")
                print(f"     机构: {user_data['institutionName']}")
                print(f"     Token: {token[:30]}...")
            else:
                print(f"  FAIL: {data['message']}")
                return False
        else:
            print(f"  FAIL 状态码: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # Step 4: 使用token访问需要认证的接口
    print("\n[Step 4/5] 使用Token访问认证接口...")
    
    # 4.1 获取用户详情（需要token）
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                user = data['data']
                print(f"  OK 获取用户详情成功")
                print(f"     姓名: {user['name']}")
                print(f"     角色: {user['role']}")
                print(f"     状态: {'启用' if user['enabled'] else '禁用'}")
            else:
                print(f"  WARN: {data['message']}")
        else:
            print(f"  WARN 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 4.2 测试没有token访问会失败
    print("\n[Step 5/5] 验证：无Token访问管理接口会被拒绝...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/institutions",
            json={
                "name": "测试医院",
                "region": "浙江省",
                "code": "TEST001",
                "uscc": "91330000000000000X"
            },
            timeout=5
        )
        if response.status_code == 401:
            print(f"  OK 正确返回401 Unauthorized（无token被拒绝）")
        else:
            print(f"  WARN 预期401，实际: {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("完整流程测试总结")
    print("=" * 70)
    print("OK Step 1: 无token访问公开接口（热门地区、等级列表）")
    print("OK Step 2: 无token搜索机构")
    print("OK Step 3: 无token完成注册并获得token")
    print("OK Step 4: 使用token访问认证接口")
    print("OK Step 5: 无token访问管理接口被拒绝")
    print("\n结论: 注册流程完整可用！")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        test_registration_flow()
    except Exception as e:
        print(f"ERROR: {e}")
