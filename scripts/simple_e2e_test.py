#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的端到端测试
统一使用UTF-8编码
"""

# 首先设置UTF-8编码
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:6031"

class SimpleE2ETest:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        
    def log(self, message, success=None):
        """记录测试日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = ""
        if success is True:
            status = "[成功]"
        elif success is False:
            status = "[失败]"
        
        log_msg = f"[{timestamp}] {status} {message}"
        print(log_msg)
        self.test_results.append(log_msg)
    
    def api_call(self, method, path, token=None, data=None, params=None):
        """调用API"""
        url = f"{BASE_URL}{path}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                resp = requests.put(url, headers=headers, json=data, timeout=10)
            else:
                return None
            
            if resp.status_code == 200:
                return resp.json()
            else:
                self.log(f"API错误 {method} {path}: {resp.status_code}", False)
                return None
        except Exception as e:
            self.log(f"API异常 {method} {path}: {e}", False)
            return None
    
    def test_login(self, phone, name, role, institution_id=None):
        """测试登录"""
        self.log(f"登录测试: {name} ({role})")
        
        result = self.api_call("POST", "/api/auth/login", data={
            "phone": phone,
            "name": name,
            "title": "测试",
            "role": role,
            "institutionId": institution_id
        })
        
        if result and result.get("success"):
            token = result["data"]["token"]
            user_id = result["data"]["id"]
            self.tokens[role] = token
            self.log(f"  用户ID: {user_id}, 角色: {role}", True)
            return token, user_id
        else:
            self.log(f"  登录失败", False)
            return None, None
    
    def test_query(self, endpoint, description, token, params=None):
        """测试查询接口"""
        self.log(f"查询测试: {description}")
        
        result = self.api_call("GET", endpoint, token=token, params=params)
        
        if result and result.get("success"):
            data = result.get("data")
            if isinstance(data, list):
                self.log(f"  返回 {len(data)} 条数据", True)
                return data
            else:
                self.log(f"  返回数据成功", True)
                return data
        else:
            self.log(f"  查询失败", False)
            return None
    
    def test_update_competition_stage(self, competition_id, stage, token):
        """测试更新赛事阶段"""
        self.log(f"更新赛事阶段: 赛事{competition_id} -> {stage}")
        
        result = self.api_call("PUT", f"/api/competitions/{competition_id}/stage",
                              token=token, data={"stage": stage})
        
        if result and result.get("success"):
            self.log(f"  阶段更新成功", True)
            return True
        else:
            self.log(f"  阶段更新失败", False)
            return False
    
    def test_assign_review_task(self, registration_id, reviewer_id, stage, token):
        """测试分配评审任务"""
        self.log(f"分配评审任务: 报名{registration_id} -> 评审{reviewer_id} ({stage})")
        
        result = self.api_call("POST", "/api/admin/reviews/tasks",
                              token=token, data={
                                  "registrationId": registration_id,
                                  "reviewerId": reviewer_id,
                                  "stage": stage
                              })
        
        if result and result.get("success"):
            task_id = result["data"]["id"]
            self.log(f"  任务ID: {task_id}", True)
            return task_id
        else:
            self.log(f"  任务分配失败", False)
            return None
    
    def test_confirm_task(self, task_id, token):
        """测试确认评审任务"""
        self.log(f"确认评审任务: {task_id}")
        
        result = self.api_call("PUT", "/api/reviews/tasks/status",
                              token=token, data={
                                  "reviewTaskId": task_id,
                                  "status": "CONFIRMED"
                              })
        
        if result and result.get("success"):
            self.log(f"  任务确认成功", True)
            return True
        else:
            self.log(f"  任务确认失败", False)
            return False
    
    def test_submit_score(self, task_id, token):
        """测试提交评分"""
        self.log(f"提交评分: 任务{task_id}")
        
        result = self.api_call("POST", "/api/reviews/scores",
                              token=token, data={
                                  "reviewTaskId": task_id,
                                  "plan": 18,
                                  "problem": 17,
                                  "action": 19,
                                  "success": 16,
                                  "review": 14,
                                  "operation": 11,
                                  "presentation": 8,
                                  "highlight": "项目设计合理，数据真实",
                                  "weakness": "展示方式可以更生动"
                              })
        
        if result and result.get("success"):
            self.log(f"  评分提交成功", True)
            return True
        else:
            self.log(f"  评分提交失败", False)
            return False
    
    def test_view_results(self, registration_id, token):
        """测试查看评审结果"""
        self.log(f"查看评审结果: 报名{registration_id}")
        
        result = self.api_call("GET", f"/api/registrations/{registration_id}/review-details",
                              token=token)
        
        if result and result.get("success"):
            details = result.get("data", [])
            self.log(f"  返回 {len(details)} 个阶段的评审结果", True)
            for stage_result in details:
                stage = stage_result.get("stage", "未知")
                avg_total = stage_result.get("avgTotal", 0)
                self.log(f"    {stage}: 平均分 {avg_total}")
            return details
        else:
            self.log(f"  查看结果失败", False)
            return None
    
    def run_simple_test(self):
        """运行简化测试"""
        print("="*80)
        print("开始简化端到端测试")
        print("="*80)
        
        # 1. 登录测试
        print("\n" + "="*80)
        print("第1步：登录测试")
        print("="*80)
        
        ops_token, ops_id = self.test_login("13800000051", "运维管理员", "OPS")
        if not ops_token:
            print("\n测试终止：无法登录")
            return
        
        reviewer_token, reviewer_id = self.test_login("13800000021", "评审专家A", "REVIEWER")
        contestant_token, contestant_id = self.test_login("13966000001", "参赛者1", "CONTESTANT", 1)
        
        # 2. 查询数据
        print("\n" + "="*80)
        print("第2步：查询数据")
        print("="*80)
        
        institutions = self.test_query("/api/institutions", "机构列表", ops_token)
        competitions = self.test_query("/api/competitions", "赛事列表", ops_token)
        registrations = self.test_query("/api/admin/registrations/filter", "报名列表", 
                                       ops_token, params={"competitionId": 21})
        
        if not registrations or len(registrations) == 0:
            print("\n测试终止：没有报名数据")
            return
        
        # 3. 更新赛事阶段
        print("\n" + "="*80)
        print("第3步：更新赛事阶段")
        print("="*80)
        
        self.test_update_competition_stage(21, "BOOK_REVIEW", ops_token)
        
        # 4. 分配评审任务
        print("\n" + "="*80)
        print("第4步：分配评审任务")
        print("="*80)
        
        # 为前3个报名分配任务
        task_ids = []
        for i, reg in enumerate(registrations[:3]):
            task_id = self.test_assign_review_task(
                reg["registrationId"], 
                reviewer_id, 
                "BOOK", 
                ops_token
            )
            if task_id:
                task_ids.append(task_id)
        
        if len(task_ids) == 0:
            print("\n测试终止：无法分配任务")
            return
        
        # 5. 评审专家评分
        print("\n" + "="*80)
        print("第5步：评审专家评分")
        print("="*80)
        
        for task_id in task_ids:
            if self.test_confirm_task(task_id, reviewer_token):
                self.test_submit_score(task_id, reviewer_token)
        
        # 6. 查看评审结果
        print("\n" + "="*80)
        print("第6步：查看评审结果")
        print("="*80)
        
        if registrations:
            first_reg_id = registrations[0]["registrationId"]
            self.test_view_results(first_reg_id, contestant_token)
        
        # 7. 查看汇总和排名
        print("\n" + "="*80)
        print("第7步：查看汇总和排名")
        print("="*80)
        
        self.test_query("/api/admin/reviews/summary", "书审汇总", 
                       ops_token, params={"competitionId": 21, "stage": "BOOK"})
        self.test_query("/api/admin/reviews/rankings", "书审排名", 
                       ops_token, params={"competitionId": 21, "stage": "BOOK"})
        
        print("\n" + "="*80)
        print("测试完成")
        print("="*80)
        
        # 保存结果
        with open("data/exports/simple_e2e_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.test_results))
        
        print(f"\n测试结果已保存到: data/exports/simple_e2e_results.txt")

if __name__ == "__main__":
    tester = SimpleE2ETest()
    try:
        tester.run_simple_test()
    except Exception as e:
        print(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()
