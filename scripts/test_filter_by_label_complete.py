#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整测试按品管工具label筛选"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

BASE = "http://localhost:6031"

print("="*80)
print("测试按品管工具筛选：品管圈-课题达成")
print("="*80)

try:
    # 步骤1：登录组委会账号
    print("\n[步骤1] 登录组委会账号")
    print("-" * 80)
    
    login_resp = requests.post(f"{BASE}/api/auth/login", json={
        "phone": "13800000003",
        "name": "组委会管理员",
        "role": "COMMITTEE"
    }, timeout=10)
    
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        print(f"响应: {login_resp.text}")
        exit(1)
    
    token = login_resp.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    print(f"Token: {token[:50]}...")
    
    # 步骤2：获取所有报名（验证数据存在）
    print("\n\n[步骤2] 获取所有报名（验证数据存在）")
    print("-" * 80)
    
    all_resp = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={"competitionId": 21},
        headers=headers,
        timeout=10
    )
    
    if all_resp.status_code == 200:
        all_data = all_resp.json()['data']
        print(f"✅ 成功获取报名列表")
        print(f"   总数: {len(all_data)} 个报名")
        
        # 统计品管工具分布
        method_count = {}
        for item in all_data:
            method = item.get('methodLabel', 'N/A')
            method_count[method] = method_count.get(method, 0) + 1
        
        print(f"\n   品管工具分布:")
        for method, count in sorted(method_count.items(), key=lambda x: x[1], reverse=True):
            marker = "👉" if method == "品管圈-课题达成" else "  "
            print(f"   {marker} {method}: {count}个")
        
        # 找出品管圈-课题达成的报名
        target_items = [item for item in all_data if item.get('methodLabel') == '品管圈-课题达成']
        print(f"\n   品管圈-课题达成的报名:")
        for item in target_items:
            print(f"     - ID {item['registrationId']}: {item['projectName']}")
            print(f"       机构: {item['institutionName']}")
            print(f"       code: {item['methodCode']}")
    else:
        print(f"❌ 获取失败: {all_resp.status_code}")
        print(f"响应: {all_resp.text[:500]}")
        exit(1)
    
    # 步骤3：按label筛选（前端实际调用）
    print("\n\n[步骤3] 按label筛选：品管圈-课题达成")
    print("-" * 80)
    
    filter_resp = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodLabel": "品管圈-课题达成"
        },
        headers=headers,
        timeout=10
    )
    
    print(f"请求URL: {filter_resp.url}")
    print(f"状态码: {filter_resp.status_code}")
    
    if filter_resp.status_code == 200:
        filtered_data = filter_resp.json()['data']
        print(f"✅ 筛选成功")
        print(f"   返回: {len(filtered_data)} 个报名")
        
        if len(filtered_data) > 0:
            print(f"\n   筛选结果:")
            for item in filtered_data:
                print(f"     - ID {item['registrationId']}: {item['projectName']}")
                print(f"       机构: {item['institutionName']}")
                print(f"       组别: {item['groupType']}")
                print(f"       分组: {item['groupCode']}")
                print(f"       品管工具: {item['methodLabel']} ({item['methodCode']})")
                print(f"       报名人: {item['applicantName']}")
                print(f"       报名时间: {item['submittedAt']}")
                print()
        else:
            print(f"\n   ⚠️  返回空列表")
            print(f"   这可能是前端看到'暂无报名数据'的原因")
    else:
        print(f"❌ 筛选失败: {filter_resp.status_code}")
        print(f"响应: {filter_resp.text[:500]}")
    
    # 步骤4：验证不同的调用方式
    print("\n\n[步骤4] 验证不同的调用方式")
    print("-" * 80)
    
    # 方式1：按code筛选
    print("\n方式1: 按code筛选 (methodCode=qc_topic)")
    code_resp = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodCode": "qc_topic"
        },
        headers=headers,
        timeout=10
    )
    
    if code_resp.status_code == 200:
        code_data = code_resp.json()['data']
        print(f"  ✅ 返回 {len(code_data)} 个报名")
    else:
        print(f"  ❌ 失败")
    
    # 方式2：按另一个code筛选（method_2也对应品管圈-课题达成）
    print("\n方式2: 按另一个code筛选 (methodCode=method_2)")
    method2_resp = requests.get(
        f"{BASE}/api/admin/registrations/filter",
        params={
            "competitionId": 21,
            "methodCode": "method_2"
        },
        headers=headers,
        timeout=10
    )
    
    if method2_resp.status_code == 200:
        method2_data = method2_resp.json()['data']
        print(f"  ✅ 返回 {len(method2_data)} 个报名")
    else:
        print(f"  ❌ 失败")
    
    # 步骤5：生成前端调用代码
    print("\n\n[步骤5] 前端调用代码示例")
    print("-" * 80)
    
    print("""
// Vue 3 + Axios 示例
async function filterByMethod(methodLabel) {
  const response = await axios.get('/api/admin/registrations/filter', {
    params: {
      competitionId: 21,  // 当前赛事ID
      methodLabel: methodLabel  // 品管工具标签
    },
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  return response.data.data;
}

// 使用示例
const results = await filterByMethod('品管圈-课题达成');
console.log('筛选结果:', results);

// React 示例
const filterByMethod = async (methodLabel) => {
  const response = await axios.get('/api/admin/registrations/filter', {
    params: {
      competitionId: 21,
      methodLabel: methodLabel
    },
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  return response.data.data;
};
""")

except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败，服务器未启动")
    print("请启动服务器：mvn spring-boot:run")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)

print("""
总结：

如果步骤3返回了数据，说明后端正常，前端可以直接使用。
如果步骤3返回空列表，可能的原因：
  1. 赛事ID不对（确认是21）
  2. 品管工具label拼写不对（确认是"品管圈-课题达成"）
  3. token失效（重新登录）
  4. 参数没有正确传递（检查前端代码）

前端完整调用示例：

GET /api/admin/registrations/filter?competitionId=21&methodLabel=品管圈-课题达成
Headers: Authorization: Bearer YOUR_TOKEN

预期返回：
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第一医院",
      "groupType": "BASIC",
      "groupCode": "A1",
      "submittedAt": "2026-02-04T15:38:52.604359",
      "subjectTypeCode": "education",
      "methodCode": "qc_topic",
      "subjectTypeLabel": "教育训练",
      "methodLabel": "品管圈-课题达成",
      "applicantName": "参赛者1"
    },
    ...
  ]
}
""")
