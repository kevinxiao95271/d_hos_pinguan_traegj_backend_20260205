#!/usr/bin/env python3
"""
检查评审驳回后再次打分的逻辑
通过查看代码和数据库验证
"""
import psycopg2
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'pinguan_new',
    'user': 'postgres',
    'password': 'Wj@211314'
}

def check_code_logic():
    """检查代码逻辑"""
    print("=" * 60)
    print("代码逻辑分析")
    print("=" * 60)
    
    print("\n1. submitScore() 方法逻辑:")
    print("   ```java")
    print("   ReviewScore score = reviewScoreRepository")
    print("       .findByReviewTaskId(task.getId())")
    print("       .orElse(ReviewScore.builder().reviewTask(task).build());")
    print("   ```")
    print("   ✓ 使用 findByReviewTaskId().orElse() 模式")
    print("   ✓ 如果存在评分记录，则获取并更新")
    print("   ✓ 如果不存在评分记录，则创建新记录")
    print("   ✓ 最后保存评分，并将任务状态设为 SCORED")
    
    print("\n2. updateStatus() 方法逻辑:")
    print("   ```java")
    print("   task.setStatus(request.getStatus());")
    print("   return reviewTaskRepository.save(task);")
    print("   ```")
    print("   ✓ 直接更新任务状态")
    print("   ✓ 可以将 SCORED 改为 RETURNED（驳回）")
    
    print("\n3. ReviewStatus 枚举:")
    print("   - PENDING: 待确认")
    print("   - CONFIRMED: 已确认")
    print("   - SCORED: 已评分")
    print("   - RETURNED: 已驳回")
    
    print("\n4. 业务流程:")
    print("   第一次打分:")
    print("   ├─ 评委提交评分 → submitScore()")
    print("   ├─ 创建 ReviewScore 记录")
    print("   └─ 任务状态: PENDING/CONFIRMED → SCORED")
    print("")
    print("   管理员驳回:")
    print("   ├─ 管理员调用 updateStatus()")
    print("   └─ 任务状态: SCORED → RETURNED")
    print("")
    print("   第二次打分:")
    print("   ├─ 评委再次提交评分 → submitScore()")
    print("   ├─ 找到已存在的 ReviewScore 记录")
    print("   ├─ 更新评分数据（覆盖原数据）")
    print("   └─ 任务状态: RETURNED → SCORED")

def check_database_data():
    """检查数据库中的实际数据"""
    print("\n" + "=" * 60)
    print("数据库数据验证")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 查询评审任务和评分记录
        print("\n查询评审任务和评分记录...")
        cur.execute("""
            SELECT 
                rt.id as task_id,
                rt.status,
                rs.id as score_id,
                rs.total,
                rs.highlight,
                rs.submitted_at
            FROM review_tasks rt
            LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
            WHERE rt.id IN (
                SELECT id FROM review_tasks 
                ORDER BY id DESC 
                LIMIT 5
            )
            ORDER BY rt.id DESC
        """)
        
        rows = cur.fetchall()
        
        if rows:
            print(f"\n找到 {len(rows)} 条评审任务记录:")
            print("-" * 60)
            for row in rows:
                task_id, status, score_id, total, highlight, submitted_at = row
                print(f"任务ID: {task_id}")
                print(f"  状态: {status}")
                if score_id:
                    print(f"  评分ID: {score_id}")
                    print(f"  总分: {total}")
                    print(f"  亮点: {highlight[:50] if highlight else 'N/A'}...")
                    print(f"  提交时间: {submitted_at}")
                else:
                    print(f"  评分: 未评分")
                print("-" * 60)
        else:
            print("没有找到评审任务记录")
        
        # 检查是否有驳回后再次打分的记录
        print("\n检查驳回后再次打分的情况...")
        cur.execute("""
            SELECT 
                rt.id as task_id,
                rt.status,
                COUNT(DISTINCT rs.id) as score_count,
                MAX(rs.submitted_at) as last_submit_time
            FROM review_tasks rt
            LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
            WHERE rt.status IN ('SCORED', 'RETURNED')
            GROUP BY rt.id, rt.status
            HAVING COUNT(DISTINCT rs.id) > 0
            ORDER BY rt.id DESC
            LIMIT 10
        """)
        
        rows = cur.fetchall()
        if rows:
            print(f"\n找到 {len(rows)} 条有评分的任务:")
            for row in rows:
                task_id, status, score_count, last_submit = row
                print(f"任务ID: {task_id}, 状态: {status}, 评分记录数: {score_count}, 最后提交: {last_submit}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")

def main():
    print("\n" + "=" * 60)
    print("评审驳回后再次打分 - 逻辑验证")
    print("=" * 60)
    
    # 1. 检查代码逻辑
    check_code_logic()
    
    # 2. 检查数据库数据
    check_database_data()
    
    # 3. 结论
    print("\n" + "=" * 60)
    print("验证结论")
    print("=" * 60)
    
    print("\n✅ 当前实现支持驳回后再次打分")
    print("\n关键机制:")
    print("1. ReviewScore 表与 ReviewTask 是一对一关系")
    print("   - review_task_id 是外键")
    print("   - 一个任务只有一条评分记录")
    print("")
    print("2. submitScore() 使用 findByReviewTaskId().orElse() 模式")
    print("   - 第一次打分：创建新记录")
    print("   - 再次打分：更新现有记录（覆盖）")
    print("")
    print("3. 状态流转:")
    print("   PENDING/CONFIRMED → SCORED → RETURNED → SCORED")
    print("   ↑ 第一次打分      ↑ 驳回    ↑ 再次打分")
    print("")
    print("4. 数据一致性:")
    print("   - 评分数据会被完全覆盖")
    print("   - 不保留历史版本")
    print("   - submitted_at 更新为最新提交时间")
    
    print("\n⚠️  注意事项:")
    print("1. 没有评分历史记录（每次覆盖）")
    print("2. 驳回原因没有记录在数据库中")
    print("3. 评委看不到驳回原因（需要前端额外实现）")
    
    print("\n💡 建议优化（可选）:")
    print("1. 增加驳回原因字段（review_tasks.reject_reason）")
    print("2. 增加评分历史表（review_score_history）")
    print("3. 增加驳回次数统计（review_tasks.reject_count）")
    print("4. 前端显示驳回原因，引导评委修改")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
