#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量分组API端到端测试
测试修改项目138的分组从A4改为C1
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:6031"

def wait_for_server():
    """等待服务器启动"""
    print("等待服务器启动...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/api/competitions", timeout=3)
            if response.status_code in [200, 401]:
                print(f"✓ 服务器已启动\n")
                return True
        except:
            pass
        time.sleep(2)
    print("✗ 服务器启动超时\n")
    return False

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": "13900000000",
        "name": "Admin User",
        "title": "Manager",
        "role": "OPS",
        "institutionId": 1
    })
    if response.status_code == 200:
        return response.json()["data"]["token"]
    raise Exception(f"登录失败: {response.status_code}")

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def get_registration_detail(registration_id, token):
    """查询项目详情"""
    url = f"{BASE_URL}/api/registrations/{registration_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"❌ 查询失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

def get_registration_from_list(registration_id, token):
    """从筛选列表中查询项目"""
    url = f"{BASE_URL}/api/admin/registrations/filter"
    response = requests.get(url, params={
        "competitionId": 21
    }, headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        data = response.json()["data"]
        # 如果是分页结果
        if isinstance(data, dict) and "content" in data:
            registrations = data["content"]
        else:
            registrations = data
            
        # 查找指定ID的项目（注意：列表API返回的字段名是registrationId）
        for reg in registrations:
            if reg.get("registrationId") == registration_id or reg.get("id") == registration_id:
                return reg
        print(f"⚠️  在列表中未找到项目ID {registration_id}")
        return None
    else:
        print(f"❌ 查询列表失败: {response.status_code}")
        return None

def batch_classify(registration_ids, group_code, token):
    """批量分组"""
    url = f"{BASE_URL}/api/admin/registrations/batch-classify"
    
    payload = {
        "registrationIds": registration_ids,
        "groupCode": group_code
    }
    
    print(f"📤 请求URL: {url}")
    print(f"📤 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    response = requests.post(url, 
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            })
    
    print(f"📥 响应状态: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"❌ 批量分组失败")
        print(f"错误信息: {response.text}")
        return None

def print_registration_info(reg, source=""):
    """打印项目信息"""
    if reg is None:
        print(f"❌ 无数据")
        return
    
    title = f"项目信息 ({source})" if source else "项目信息"
    print(f"\n【{title}】")
    # 兼容两种字段名
    reg_id = reg.get('id') or reg.get('registrationId') or reg.get('registration', {}).get('id')
    print(f"  ID: {reg_id}")
    print(f"  项目名称: {reg.get('projectName')}")
    print(f"  医疗机构: {reg.get('institutionName') or reg.get('institution', {}).get('name')}")
    print(f"  组别类型: {reg.get('groupType')}")
    print(f"  分组代码: {reg.get('groupCode')} ⬅️")
    print(f"  状态: {reg.get('status')}")

def main():
    print_section("批量分组API端到端测试")
    print("测试目标: 修改项目138的分组从A4改为C1\n")
    
    if not wait_for_server():
        return
    
    try:
        token = login()
        print("✓ 登录成功（OPS角色）\n")
        
        registration_id = 138
        target_group_code = "C1"
        
        # ========== 步骤1: 查询项目当前信息 ==========
        print_section("步骤1: 查询项目当前信息")
        
        print("1️⃣  通过详情API查询...")
        reg_detail = get_registration_detail(registration_id, token)
        print_registration_info(reg_detail, "详情API")
        original_group_code = reg_detail.get('groupCode') if reg_detail else None
        
        print("\n2️⃣  通过筛选列表API查询...")
        reg_from_list = get_registration_from_list(registration_id, token)
        print_registration_info(reg_from_list, "筛选列表API")
        
        if not reg_detail:
            print("\n❌ 无法获取项目信息，测试终止")
            return
        
        # ========== 步骤2: 修改分组 ==========
        print_section("步骤2: 批量修改分组")
        
        print(f"📝 修改目标:")
        print(f"   项目ID: {registration_id}")
        print(f"   原分组: {original_group_code}")
        print(f"   新分组: {target_group_code}\n")
        
        result = batch_classify([registration_id], target_group_code, token)
        
        if result:
            print(f"\n✅ API调用成功")
            print(f"📄 返回数据:")
            if isinstance(result, list) and len(result) > 0:
                updated_reg = result[0]
                print(f"   ID: {updated_reg.get('id')}")
                print(f"   项目名称: {updated_reg.get('projectName')}")
                print(f"   分组代码: {updated_reg.get('groupCode')} ⬅️ 应该是 {target_group_code}")
                
                if updated_reg.get('groupCode') == target_group_code:
                    print(f"\n✅ 返回的分组代码已更新为 {target_group_code}")
                else:
                    print(f"\n⚠️  返回的分组代码仍是 {updated_reg.get('groupCode')}，不是预期的 {target_group_code}")
            else:
                print(f"   {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"\n❌ 批量分组失败")
            return
        
        # ========== 步骤3: 再次查询验证 ==========
        print_section("步骤3: 再次查询验证修改结果")
        
        time.sleep(1)  # 稍微等待一下确保数据已保存
        
        print("1️⃣  通过详情API查询...")
        reg_detail_after = get_registration_detail(registration_id, token)
        print_registration_info(reg_detail_after, "详情API")
        
        print("\n2️⃣  通过筛选列表API查询...")
        reg_from_list_after = get_registration_from_list(registration_id, token)
        print_registration_info(reg_from_list_after, "筛选列表API")
        
        # ========== 步骤4: 结果对比 ==========
        print_section("步骤4: 结果对比")
        
        print("📊 分组代码变化:")
        print(f"   修改前: {original_group_code}")
        print(f"   目标值: {target_group_code}")
        
        detail_after_code = reg_detail_after.get('groupCode') if reg_detail_after else None
        list_after_code = reg_from_list_after.get('groupCode') if reg_from_list_after else None
        
        print(f"   修改后(详情API): {detail_after_code}")
        print(f"   修改后(列表API): {list_after_code}")
        
        # 判断是否成功
        success = (detail_after_code == target_group_code and 
                  list_after_code == target_group_code)
        
        print(f"\n{'='*80}")
        if success:
            print("✅ 测试通过！分组修改成功")
            print(f"   项目138的分组已从 {original_group_code} 成功修改为 {target_group_code}")
        else:
            print("❌ 测试失败！分组未成功修改")
            print(f"\n可能的原因:")
            print(f"   1. 详情API返回的分组码: {detail_after_code} (预期: {target_group_code})")
            print(f"   2. 列表API返回的分组码: {list_after_code} (预期: {target_group_code})")
            print(f"   3. 数据库可能没有实际保存更新")
            print(f"   4. 事务可能回滚了")
            print(f"   5. 缓存问题")
        print(f"{'='*80}\n")
        
        # ========== 额外: 检查数据库 ==========
        print_section("步骤5: API端完整请求响应日志")
        
        print("如果以上测试失败，请检查:")
        print("1. 服务器日志中是否有错误")
        print("2. 数据库中registrations表的group_code字段")
        print("3. 是否有事务回滚")
        print("\n直接SQL查询验证:")
        print(f"   SELECT id, project_name, group_code FROM registrations WHERE id = {registration_id};")
        
    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
