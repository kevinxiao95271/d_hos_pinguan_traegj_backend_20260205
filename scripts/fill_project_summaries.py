#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为所有报名记录填充项目摘要数据"""

import pymysql
from db_config import DB_CONFIG
import random

# DB_CONFIG imported from db_config.py

# 示例数据模板
PLAN_TEMPLATES = [
    "制定详细的项目实施计划，明确目标、时间节点和责任人",
    "设计科学的改进方案，包括流程优化、制度完善和技术支持",
    "建立系统化的管理体系，确保项目顺利推进和持续改进",
    "制定可行的实施策略，整合资源，协调各方力量共同推进",
    "规划完整的项目路线图，分阶段实施，逐步达成预期目标"
]

PROBLEM_TEMPLATES = [
    "现有流程存在效率低下、环节繁琐等问题，影响服务质量",
    "管理制度不够完善，缺乏标准化操作规范，导致执行不统一",
    "资源配置不合理，人员培训不足，影响工作效果",
    "信息沟通不畅，部门协作存在障碍，影响整体效率",
    "质量控制体系不健全，缺乏有效的监督和反馈机制"
]

ACTION_TEMPLATES = [
    "组织专项培训，优化工作流程，建立标准化操作规范",
    "成立项目小组，制定实施方案，分步骤推进各项改进措施",
    "引入信息化手段，提升管理效率，加强过程监控和质量控制",
    "开展全员动员，统一思想认识，形成全员参与的良好氛围",
    "建立长效机制，持续改进优化，确保项目成果得到巩固"
]

SUCCESS_TEMPLATES = [
    "项目实施后，相关指标显著提升，服务质量明显改善，获得广泛好评",
    "通过系统化改进，工作效率提高30%以上，患者满意度达到95%以上",
    "建立了完善的管理体系，形成了可复制推广的经验模式",
    "实现了预期目标，各项指标均达到或超过计划要求",
    "取得了显著成效，为医院高质量发展提供了有力支撑"
]

DISCUSSION_TEMPLATES = [
    "项目实施过程中积累了宝贵经验，为今后类似工作提供了参考",
    "通过持续改进，形成了良性循环机制，确保成果长期保持",
    "项目成功的关键在于全员参与、科学管理和持续优化",
    "实践证明，系统化的质量改进方法能够有效提升管理水平",
    "项目经验具有推广价值，可为其他单位提供借鉴"
]

def fill_summaries():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("填充项目摘要数据")
        print("=" * 80)
        
        # 获取所有报名记录
        cursor.execute("""
            SELECT r.id, r.project_name
            FROM registrations r
            WHERE r.id NOT IN (SELECT registration_id FROM project_summaries)
            ORDER BY r.id
        """)
        
        registrations = cursor.fetchall()
        
        if not registrations:
            print("\n✅ 所有报名记录都已有项目摘要数据")
            return
        
        print(f"\n找到 {len(registrations)} 条需要填充的报名记录")
        print("-" * 80)
        
        for reg_id, project_name in registrations:
            # 随机选择模板
            plan = random.choice(PLAN_TEMPLATES)
            problem = random.choice(PROBLEM_TEMPLATES)
            action = random.choice(ACTION_TEMPLATES)
            success = random.choice(SUCCESS_TEMPLATES)
            discussion = random.choice(DISCUSSION_TEMPLATES)
            
            # 插入项目摘要
            cursor.execute("""
                INSERT INTO project_summaries 
                (registration_id, theme, plan, problem, action, success, discussion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (reg_id, project_name or "项目主题", plan, problem, action, success, discussion))
            
            print(f"✅ 报名ID {reg_id:3d}: {project_name[:30] if project_name else '项目主题'}")
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ 成功填充 {len(registrations)} 条项目摘要数据")
        print("=" * 80)
        
        # 验证结果
        cursor.execute("SELECT COUNT(*) FROM project_summaries")
        total = cursor.fetchone()[0]
        print(f"\n当前项目摘要总数: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM registrations")
        reg_total = cursor.fetchone()[0]
        print(f"报名记录总数: {reg_total}")
        
        if total == reg_total:
            print("\n✅ 所有报名记录都已有项目摘要数据")
        else:
            print(f"\n⚠️  还有 {reg_total - total} 条报名记录没有项目摘要")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fill_summaries()
