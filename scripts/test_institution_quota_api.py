#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试机构报名配额查询API"""

import requests
import json

BASE_URL = "http://localhost:6031"

def test_quota_api():
    """测试机构报名配额查询API"""
    print("=" * 80)
    print("测试机构报名配额查询API")
    print("=" * 80)
    
    # 1. 登录参赛者
    print("\n【步骤1】登录参赛者")
    login_data = {
        "phone": "13800000001",
        "name": "张三",
        "role": "CONTESTANT"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ 登录失败: {result.get('message')}")
        return
    
    token = result["data"]["token"]
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 查询机构报名配额
    print(f"\n【步骤2】查询机构报名配额")
    
    competition_id = 21
    institution_id = 1  # 浙江大学医学院附属第二医院
    
    response = requests.get(
        f"{BASE_URL}/api/registrations/institution-quota?competitionId={competition_id}&institutionId={institution_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ API调用失败: {result.get('message')}")
        return
    
    print("✅ API调用成功")
    
    data = result["data"]
    
    # 3. 显示配额信息
    print("\n" + "=" * 80)
    print("机构报名配额信息")
    print("=" * 80)
    
    print(f"\n机构信息:")
    print(f"  机构ID: {data.get('institutionId')}")
    print(f"  机构名称: {data.get('institutionName')}")
    
    print(f"\n赛事信息:")
    print(f"  赛事ID: {data.get('competitionId')}")
    print(f"  赛事名称: {data.get('competitionName')}")
    
    print(f"\n配额信息:")
    print(f"  已报名数量: {data.get('currentCount')}")
    print(f"  最大数量: {data.get('maxCount')}")
    print(f"  剩余数量: {data.get('remainingCount')}")
    print(f"  是否可报名: {'✅ 是' if data.get('canRegister') else '❌ 否'}")
    
    # 4. 显示提示信息
    current = data.get('currentCount', 0)
    max_count = data.get('maxCount', 0)
    remaining = data.get('remainingCount', 0)
    
    print(f"\n提示信息:")
    if data.get('canRegister'):
        print(f"  ✅ 您的机构还可以报名 {remaining} 个项目")
        if remaining <= 2:
            print(f"  ⚠️  注意：报名名额即将用完，请尽快提交")
    else:
        print(f"  ❌ 您的机构报名数量已达上限（{max_count}个项目）")
        print(f"  💡 如需增加名额，请联系管理员")
    
    # 5. 显示完整响应
    print("\n" + "=" * 80)
    print("完整API响应")
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 6. 前端使用示例
    print("\n" + "=" * 80)
    print("前端使用示例")
    print("=" * 80)
    print("""
// 1. 在报名页面加载时查询配额
const checkQuota = async (competitionId, institutionId) => {
  const response = await fetch(
    `/api/registrations/institution-quota?competitionId=${competitionId}&institutionId=${institutionId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  const result = await response.json();
  return result.data;
};

// 2. 显示提示信息
const quota = await checkQuota(21, 1);
if (!quota.canRegister) {
  message.error(`您的机构报名数量已达上限（${quota.maxCount}个项目）`);
  // 禁用"创建报名"按钮
  setCanCreate(false);
} else if (quota.remainingCount <= 2) {
  message.warning(`您的机构还可以报名 ${quota.remainingCount} 个项目，名额即将用完`);
}

// 3. 在页面上显示配额信息
<Alert
  message={`报名配额：已报名 ${quota.currentCount}/${quota.maxCount} 个项目，剩余 ${quota.remainingCount} 个名额`}
  type={quota.canRegister ? 'info' : 'error'}
  showIcon
/>
    """)
    
    print("=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_quota_api()
