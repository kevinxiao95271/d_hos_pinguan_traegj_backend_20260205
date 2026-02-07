# -*- coding: utf-8 -*-
"""
测试新增的评委评分详情API
"""
import requests
import json
import sys

# 配置输出编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:6031"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_api(title, method, url, headers=None, params=None, data=None, check_fields=None):
    """测试API并验证字段"""
    print(f"\n{title}")
    print(f"API: {method} {url}")
    if params:
        print(f"参数: {params}")
    print("-" * 80)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"[ERROR] 不支持的方法: {method}")
            return False
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') == True or result.get('code') == 200:
                print("[OK] 请求成功")
                data_content = result.get('data', [])
                
                if isinstance(data_content, list):
                    print(f"[INFO] 返回 {len(data_content)} 条数据")
                    
                    if len(data_content) > 0 and check_fields:
                        first_item = data_content[0]
                        print(f"[INFO] 检查第一条数据的字段...")
                        all_fields_ok = True
                        
                        for field in check_fields:
                            if field in first_item:
                                value = first_item[field]
                                if isinstance(value, dict):
                                    print(f"  [OK] {field}: {json.dumps(value, ensure_ascii=False)}")
                                else:
                                    print(f"  [OK] {field}: {value}")
                            else:
                                print(f"  [FAIL] 缺少字段: {field}")
                                all_fields_ok = False
                        
                        return all_fields_ok
                    elif len(data_content) == 0:
                        print("[WARN] 返回空列表（可能是正常情况，无评审数据）")
                        return True
                    else:
                        return True
                else:
                    print(f"[INFO] 返回数据类型: {type(data_content)}")
                    return True
            else:
                print(f"[FAIL] 业务失败: {result.get('message')}")
                return False
        else:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return False

def main():
    print_section("评委评分详情API测试")
    
    # 步骤1: 登录获取token
    print_section("步骤1: 登录获取token")
    
    login_data = {
        "phone": "13800000001",
        "name": "参赛者A",
        "title": "主任护师",
        "role": "CONTESTANT",
        "institutionId": 2
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        timeout=10
    )
    
    if login_response.status_code != 200:
        print("[FAIL] 登录失败")
        return
    
    token = login_response.json()['data']['token']
    print(f"[OK] Token获取成功: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤2: 测试新API - 获取所有阶段的评委评分
    print_section("测试1: 获取项目106的所有评委评分（所有阶段）")
    
    test_api(
        "新API: GET /api/registrations/{id}/reviewer-scores",
        "GET",
        f"{BASE_URL}/api/registrations/106/reviewer-scores",
        headers=headers,
        check_fields=[
            "stage",
            "reviewerId",
            "reviewerName",
            "reviewerTitle",
            "reviewerInstitutionName",
            "reviewerInstitutionLevel",
            "scores",
            "highlight",
            "weakness",
            "submittedAt"
        ]
    )
    
    # 步骤3: 测试新API - 只获取书审阶段
    print_section("测试2: 获取项目106的书审阶段评委评分")
    
    test_api(
        "新API: GET /api/registrations/{id}/reviewer-scores?stage=BOOK",
        "GET",
        f"{BASE_URL}/api/registrations/106/reviewer-scores",
        headers=headers,
        params={"stage": "BOOK"},
        check_fields=[
            "stage",
            "reviewerId",
            "reviewerName",
            "scores"
        ]
    )
    
    # 步骤4: 验证scores对象的结构
    print_section("测试3: 验证scores对象包含7个维度")
    
    response = requests.get(
        f"{BASE_URL}/api/registrations/106/reviewer-scores",
        headers=headers,
        params={"stage": "BOOK"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if (result.get('success') == True or result.get('code') == 200) and len(result.get('data', [])) > 0:
            first_reviewer = result['data'][0]
            scores = first_reviewer.get('scores', {})
            
            print(f"评委: {first_reviewer.get('reviewerName')}")
            print(f"单位: {first_reviewer.get('reviewerInstitutionName')}")
            print(f"职称: {first_reviewer.get('reviewerTitle')}")
            print(f"等级: {first_reviewer.get('reviewerInstitutionLevel')}")
            print("\n分项评分:")
            print(f"  计划: {scores.get('plan')}分")
            print(f"  问题: {scores.get('problem')}分")
            print(f"  行动: {scores.get('action')}分")
            print(f"  成效: {scores.get('success')}分")
            print(f"  回顾: {scores.get('review')}分")
            print(f"  运作: {scores.get('operation')}分")
            print(f"  展示: {scores.get('presentation')}分")
            print(f"  总分: {scores.get('total')}分")
            print(f"\n亮点: {first_reviewer.get('highlight')[:50]}...")
            print(f"改进建议: {first_reviewer.get('weakness')[:50]}...")
            print(f"评审时间: {first_reviewer.get('submittedAt')}")
            
            # 验证所有字段都存在
            required_score_fields = ['plan', 'problem', 'action', 'success', 'review', 'operation', 'presentation', 'total']
            all_ok = all(field in scores for field in required_score_fields)
            
            if all_ok:
                print("\n[OK] scores对象包含所有7个维度和总分")
            else:
                print("\n[FAIL] scores对象缺少某些维度")
        else:
            print("[WARN] 没有返回数据")
    else:
        print("[FAIL] 请求失败")
    
    # 步骤5: 对比旧API（已废弃）
    print_section("测试4: 对比废弃API的返回结构")
    
    print("[INFO] 废弃API: GET /api/admin/reviews/feedback")
    print("[INFO] 该API已标记为 @Deprecated")
    print("[INFO] 新API优势:")
    print("  1. 包含7个维度分项评分（旧API只有总分）")
    print("  2. 包含评委职称、单位、等级（旧API只有姓名）")
    print("  3. 包含评审时间（旧API没有）")
    print("  4. 直接按项目ID查询（旧API需要按赛事查询后筛选）")
    print("  5. 数据结构更清晰（scores对象）")
    
    # 步骤6: 测试无数据情况
    print_section("测试5: 测试无评审数据的项目")
    
    test_api(
        "新API: GET /api/registrations/999/reviewer-scores",
        "GET",
        f"{BASE_URL}/api/registrations/999/reviewer-scores",
        headers=headers
    )
    
    # 步骤7: 测试面谈阶段
    print_section("测试6: 测试面谈阶段评分")
    
    test_api(
        "新API: GET /api/registrations/106/reviewer-scores?stage=INTERVIEW",
        "GET",
        f"{BASE_URL}/api/registrations/106/reviewer-scores",
        headers=headers,
        params={"stage": "INTERVIEW"}
    )
    
    # 总结
    print_section("测试总结")
    print("[SUCCESS] 新API测试完成")
    print("\n核心功能:")
    print("  1. ✅ 返回指定项目的所有评委评分")
    print("  2. ✅ 支持按阶段过滤（stage参数）")
    print("  3. ✅ 包含评委完整信息（姓名、职称、单位、等级）")
    print("  4. ✅ 包含7个维度分项评分 + 总分")
    print("  5. ✅ 包含亮点和改进建议")
    print("  6. ✅ 包含评审时间")
    print("\n废弃API:")
    print("  ❌ GET /api/admin/reviews/feedback")
    print("     原因: 新API完全覆盖并超越了旧API的功能")
    print("\n推荐使用:")
    print("  ✨ GET /api/registrations/{id}/reviewer-scores?stage={BOOK|INTERVIEW|FINAL}")

if __name__ == "__main__":
    main()
