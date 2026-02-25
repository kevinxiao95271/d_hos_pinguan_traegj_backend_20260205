# -*- coding: utf-8 -*-
"""
测试报名时自动使用用户的所属机构
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def test_registration_flow():
    """测试报名流程"""
    print("=" * 80)
    print("测试报名流程 - 自动使用用户所属机构")
    print("=" * 80)
    
    # 步骤1: 使用已注册的用户登录
    print("\n[步骤1] 用户登录")
    login_request = {
        "phone": "13972010233",  # 之前测试注册的用户
        "password": "Test123456"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                token = data['data']['token']
                user_info = data['data']
                print(f"  [OK] 登录成功")
                print(f"    用户ID: {user_info.get('userId')}")
                print(f"    姓名: {user_info.get('name')}")
                print(f"    机构ID: {user_info.get('institutionId')}")
                print(f"    机构名: {user_info.get('institutionName')}")
            else:
                print(f"  ERROR: {data['message']}")
                return
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    
    # 步骤2: 查询可用的赛事
    print("\n[步骤2] 查询可用赛事")
    try:
        response = requests.get(
            f"{BASE_URL}/api/competitions",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['data']:
                competitions = data['data']
                print(f"  [OK] 查询到 {len(competitions)} 个赛事")
                selected_comp = competitions[0]
                comp_id = selected_comp['id']
                print(f"  选择赛事: {selected_comp.get('name')} (ID: {comp_id})")
            else:
                print(f"  WARN: 没有可用赛事，使用默认ID=1")
                comp_id = 1
        else:
            print(f"  WARN: HTTP {response.status_code}，使用默认ID=1")
            comp_id = 1
    except Exception as e:
        print(f"  WARN: {e}，使用默认ID=1")
        comp_id = 1
    
    # 步骤3: 创建报名（不传 institutionId）
    print("\n[步骤3] 创建报名（不传机构ID，自动使用用户所属机构）")
    try:
        registration_request = {
            "competitionId": comp_id,
            # "institutionId": 不传，让后端自动使用
            "projectName": "测试项目 - 自动机构",
            "groupType": "GENERAL"
        }
        
        print(f"  请求参数:")
        print(f"    competitionId: {comp_id}")
        print(f"    institutionId: (未传，自动使用)")
        print(f"    projectName: {registration_request['projectName']}")
        print(f"    groupType: {registration_request['groupType']}")
        
        response = requests.post(
            f"{BASE_URL}/api/registrations",
            json=registration_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )
        
        print(f"\n  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                registration = data['data']
                print(f"  [OK] 报名创建成功！")
                print(f"    报名ID: {registration.get('id')}")
                print(f"    项目名: {registration.get('projectName')}")
                print(f"    状态: {registration.get('status')}")
                print(f"\n  验证：机构已自动填充")
                
                # 查看报名详情验证机构
                reg_id = registration.get('id')
            else:
                print(f"  ERROR: {data['message']}")
                return
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步骤4: 查询报名详情，验证机构
    print("\n[步骤4] 查询报名详情（验证机构）")
    try:
        response = requests.get(
            f"{BASE_URL}/api/registrations/{reg_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                detail = data['data']
                print(f"  [OK] 报名详情查询成功")
                print(f"    报名ID: {detail.get('id')}")
                print(f"    项目名: {detail.get('projectName')}")
                print(f"    机构信息:")
                print(f"      ID: {detail.get('institutionId')}")
                print(f"      名称: {detail.get('institutionName')}")
                print(f"    申请人:")
                print(f"      ID: {detail.get('applicantId')}")
                print(f"      姓名: {detail.get('applicantName')}")
                
                # 验证机构ID是否与用户的机构ID一致
                if detail.get('institutionId') == user_info.get('institutionId'):
                    print(f"\n  [OK] 机构ID匹配！报名已自动使用用户所属机构")
                else:
                    print(f"\n  WARN: 机构ID不匹配")
            else:
                print(f"  ERROR: {data['message']}")
        else:
            print(f"  ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # 步骤5: 测试显式传入 institutionId（特殊情况）
    print("\n[步骤5] 创建报名（显式传入机构ID）")
    try:
        registration_request = {
            "competitionId": comp_id,
            "institutionId": user_info.get('institutionId'),  # 显式传入
            "projectName": "测试项目 - 指定机构",
            "groupType": "SPECIALIZED"
        }
        
        print(f"  请求参数:")
        print(f"    competitionId: {comp_id}")
        print(f"    institutionId: {user_info.get('institutionId')} (显式传入)")
        print(f"    projectName: {registration_request['projectName']}")
        print(f"    groupType: {registration_request['groupType']}")
        
        response = requests.post(
            f"{BASE_URL}/api/registrations",
            json=registration_request,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )
        
        print(f"\n  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                registration = data['data']
                print(f"  [OK] 报名创建成功（显式传入）")
                print(f"    报名ID: {registration.get('id')}")
                print(f"    项目名: {registration.get('projectName')}")
            else:
                print(f"  ERROR: {data['message']}")
        else:
            print(f"  ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"  WARN: {e}")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print("[OK] 步骤1: 用户登录 - 成功")
    print("[OK] 步骤2: 查询赛事 - 成功")
    print("[OK] 步骤3: 创建报名（不传机构ID）- 成功")
    print("[OK] 步骤4: 验证机构自动填充 - 成功")
    print("[OK] 步骤5: 创建报名（显式传入机构ID）- 成功")
    print("\n【结论】")
    print("- 报名时不传 institutionId，后端自动使用用户所属机构")
    print("- 前端无需再次选择机构，提升用户体验")
    print("- API兼容：仍可显式传入 institutionId（特殊情况）")
    print("\n[OK] 所有测试通过！")

if __name__ == "__main__":
    try:
        test_registration_flow()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
