#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评审任务API功能测试
测试场景：
1. 书审环节 - 查看已分配任务
2. 面谈环节 - 查看已分配任务
"""

import requests
import json
from typing import Optional

# 配置
BASE_URL = "http://localhost:6031"
API_PREFIX = "/api/admin/reviews"

# 测试账号（管理员）
ADMIN_PHONE = "13800000041"
ADMIN_NAME = "CommitteeAdmin A"

class ReviewTaskAPITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    
    def login(self, phone: str, name: str) -> bool:
        """登录获取token"""
        url = f"{BASE_URL}/api/auth/login"
        payload = {
            "phone": phone,
            "name": name,
            "role": "COMMITTEE_ADMIN"
        }
        
        print(f"\n{'='*60}")
        print(f"登录测试")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"手机: {phone}")
        print(f"姓名: {name}")
        
        try:
            response = self.session.post(url, json=payload)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('data', {}).get('token')
                    print(f"✓ 登录成功")
                    print(f"Token: {self.token[:50]}..." if self.token else "无Token")
                    return True
                else:
                    print(f"✗ 登录失败: {data.get('message')}")
                    return False
            else:
                print(f"✗ 请求失败: {response.text}")
                return False
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def list_review_tasks(self, competition_id: int = 21,
                         stage: Optional[str] = None, 
                         status: Optional[str] = None,
                         page: int = 1, 
                         size: int = 20) -> dict:
        """查询评审任务列表"""
        url = f"{BASE_URL}{API_PREFIX}/tasks"
        
        params = {
            "competitionId": competition_id,
            "page": page,
            "size": size
        }
        if stage:
            params["stage"] = stage
        if status:
            params["status"] = status
        
        stage_name = {
            "BOOK": "书审",
            "INTERVIEW": "面谈",
            None: "全部"
        }.get(stage, stage)
        
        status_name = {
            "PENDING": "待确认",
            "CONFIRMED": "已确认",
            "SCORED": "已评分",
            "RETURNED": "已退回",
            None: "全部"
        }.get(status, status)
        
        print(f"\n{'='*60}")
        print(f"查询评审任务 - {stage_name}环节 - {status_name}状态")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        try:
            response = self.session.get(url, params=params, headers=self.get_headers())
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                if data.get('success'):
                    result = data.get('data', {})
                    items = result.get('items', [])
                    total = result.get('total', 0)
                    
                    print(f"\n✓ 查询成功")
                    print(f"总数: {total}")
                    print(f"当前页数据: {len(items)} 条")
                    
                    if items:
                        print(f"\n任务详情:")
                        for idx, task in enumerate(items[:5], 1):  # 只显示前5条
                            print(f"\n  [{idx}] 任务ID: {task.get('id')}")
                            print(f"      项目: {task.get('projectName')}")
                            print(f"      机构: {task.get('institutionName')}")
                            print(f"      组别: {task.get('groupType')} - {task.get('groupCode')}")
                            print(f"      评委: {task.get('reviewerName')} ({task.get('reviewerTitle')})")
                            print(f"      评委机构: {task.get('reviewerInstitutionName')}")
                            print(f"      专业背景: {task.get('expertBackground')}")
                            print(f"      环节: {task.get('stage')}")
                            print(f"      状态: {task.get('status')}")
                            print(f"      创建时间: {task.get('createdAt')}")
                        
                        if len(items) > 5:
                            print(f"\n  ... 还有 {len(items) - 5} 条数据")
                    
                    return data
                else:
                    print(f"✗ 查询失败: {data.get('message')}")
                    return data
            else:
                print(f"✗ 请求失败: {response.text}")
                return {"code": response.status_code, "message": response.text}
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            return {"code": -1, "message": str(e)}
    
    def test_book_review_tasks(self):
        """测试书审环节任务查询"""
        print(f"\n{'#'*60}")
        print(f"# 场景1: 书审环节任务查询")
        print(f"{'#'*60}")
        
        # 1. 查询所有书审任务
        self.list_review_tasks(stage="BOOK")
        
        # 2. 查询待确认的书审任务
        self.list_review_tasks(stage="BOOK", status="PENDING")
        
        # 3. 查询已确认的书审任务
        self.list_review_tasks(stage="BOOK", status="CONFIRMED")
        
        # 4. 查询已评分的书审任务
        self.list_review_tasks(stage="BOOK", status="SCORED")
    
    def test_interview_review_tasks(self):
        """测试面谈环节任务查询"""
        print(f"\n{'#'*60}")
        print(f"# 场景2: 面谈环节任务查询")
        print(f"{'#'*60}")
        
        # 1. 查询所有面谈任务
        self.list_review_tasks(stage="INTERVIEW")
        
        # 2. 查询待确认的面谈任务
        self.list_review_tasks(stage="INTERVIEW", status="PENDING")
        
        # 3. 查询已确认的面谈任务
        self.list_review_tasks(stage="INTERVIEW", status="CONFIRMED")
        
        # 4. 查询已评分的面谈任务
        self.list_review_tasks(stage="INTERVIEW", status="SCORED")
    
    def test_all_tasks(self):
        """测试查询所有任务（不限环节）"""
        print(f"\n{'#'*60}")
        print(f"# 场景3: 查询所有任务（不限环节）")
        print(f"{'#'*60}")
        
        # 查询所有任务
        self.list_review_tasks()
        
        # 查询所有待确认任务
        self.list_review_tasks(status="PENDING")
    
    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'*'*60}")
        print(f"* 评审任务API功能测试")
        print(f"{'*'*60}")
        
        # 登录
        if not self.login(ADMIN_PHONE, ADMIN_NAME):
            print("\n✗ 登录失败，测试终止")
            return
        
        # 测试书审环节
        self.test_book_review_tasks()
        
        # 测试面谈环节
        self.test_interview_review_tasks()
        
        # 测试查询所有任务
        self.test_all_tasks()
        
        print(f"\n{'*'*60}")
        print(f"* 测试完成")
        print(f"{'*'*60}")


def main():
    tester = ReviewTaskAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
