# -*- coding: utf-8 -*-
"""
测试报名详情接口 - 检查赛事信息是否正确返回
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def test_registration_detail():
    """测试报名详情"""
    print("=" * 80)
    print("测试报名详情 - 王可心账号")
    print("=" * 80)
    
    # 步骤1: 登录
    print("\n[步骤1] 登录（使用密码登录）")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login-with-password",
            json={
                "phone": "13600001234",
                "password": "test001234"
            },
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
                print(f"    机构: {user_info.get('institutionName')}")
            else:
                print(f"  ERROR: {data['message']}")
                return
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            return
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    
    # 步骤2: 查询我的报名列表
    print("\n[步骤2] 查询我的报名列表")
    try:
        response = requests.get(
            f"{BASE_URL}/api/registrations/my",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                registrations = data['data']
                print(f"  [OK] 查询到 {len(registrations)} 个报名")
                
                if registrations:
                    # 选择第一个报名
                    reg = registrations[0]
                    reg_id = reg.get('id')
                    print(f"\n  报名列表第一条:")
                    print(f"    ID: {reg_id}")
                    print(f"    项目名: {reg.get('projectName')}")
                    print(f"    状态: {reg.get('status')}")
                    print(f"    赛事ID: {reg.get('competitionId')}")
                    print(f"    赛事名: {reg.get('competitionName')}")
                    print(f"    机构ID: {reg.get('institutionId')}")
                    print(f"    机构名: {reg.get('institutionName')}")
                else:
                    print(f"  WARN: 没有报名记录")
                    return
            else:
                print(f"  ERROR: {data['message']}")
                return
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    
    # 步骤3: 查询报名详情
    print(f"\n[步骤3] 查询报名详情 (ID: {reg_id})")
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
                print(f"\n  返回的数据结构:")
                print(json.dumps(detail, indent=2, ensure_ascii=False))
                
                # 检查关键字段
                registration_obj = detail.get('registration', {})
                institution_obj = detail.get('institution', {})
                
                print(f"\n  [检查] 关键字段:")
                print(f"    registration.id: {registration_obj.get('id')}")
                print(f"    registration.projectName: {registration_obj.get('projectName')}")
                print(f"    registration.status: {registration_obj.get('status')}")
                print(f"    registration.groupType: {registration_obj.get('groupType')}")
                
                # 检查赛事信息
                print(f"\n  [重点检查] 赛事信息:")
                if 'competition' in registration_obj:
                    comp = registration_obj.get('competition')
                    print(f"    registration.competition (对象): {comp}")
                else:
                    print(f"    registration.competition: 未找到")
                
                if 'competitionId' in detail:
                    print(f"    detail.competitionId (顶层): {detail.get('competitionId')}")
                else:
                    print(f"    detail.competitionId: 未找到")
                
                # 检查机构信息
                print(f"\n  [检查] 机构信息:")
                print(f"    institution.id: {institution_obj.get('id')}")
                print(f"    institution.name: {institution_obj.get('name')}")
                
                # 问题诊断
                print(f"\n  [诊断] 前端需要的字段:")
                has_competition_id = 'competitionId' in detail or 'competitionId' in registration_obj
                print(f"    赛事ID是否存在: {'是' if has_competition_id else '否 ❌ 缺失'}")
                print(f"    机构ID是否存在: {'是' if institution_obj.get('id') else '否'}")
                
            else:
                print(f"  ERROR: {data['message']}")
        else:
            print(f"  ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_registration_detail()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
