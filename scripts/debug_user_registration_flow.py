# -*- coding: utf-8 -*-
"""
调试用户报名流程
"""
import pymysql
import time

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

def debug_user():
    """调试用户数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("调试用户报名流程")
    print("=" * 80)
    
    # 1. 查找"王可心"用户
    print("\n【查找用户】")
    cursor.execute("SELECT * FROM user_accounts WHERE name = '王可心'")
    user = cursor.fetchone()
    
    if not user:
        print("  [ERROR] 未找到用户'王可心'")
        
        # 列出所有用户
        cursor.execute("SELECT id, name, phone, role, institution_id, enabled FROM user_accounts ORDER BY id DESC LIMIT 10")
        users = cursor.fetchall()
        print(f"\n  最近注册的用户 (共{len(users)}个):")
        for u in users:
            print(f"    ID:{u[0]:3d} 姓名:{u[1]:10s} 手机:{u[2]:15s} 角色:{u[3]:10s} 机构ID:{u[4]} 启用:{u[5]}")
        
        cursor.close()
        conn.close()
        return
    
    print(f"  [OK] 找到用户")
    print(f"    ID: {user[0]}")
    print(f"    姓名: {user[6]}")
    print(f"    手机: {user[7]}")
    print(f"    角色: {user[10]}")
    print(f"    机构ID: {user[12]}")
    print(f"    启用: {user[4]}")
    print(f"    创建时间: {user[1]}")
    
    user_id = user[0]
    institution_id = user[12]
    
    # 2. 测试查询用户的机构信息（这可能是卡点）
    print("\n【测试查询用户机构】")
    if institution_id:
        start = time.time()
        cursor.execute("SELECT * FROM institutions WHERE id = %s", (institution_id,))
        inst = cursor.fetchone()
        elapsed = (time.time() - start) * 1000
        
        if inst:
            print(f"  [OK] 查询成功 ({elapsed:.2f}ms)")
            print(f"    机构名称: {inst[3]}")
            print(f"    地区: {inst[4]}")
            print(f"    等级: {inst[6]}")
        else:
            print(f"  [ERROR] 机构ID {institution_id} 不存在")
    else:
        print(f"  [WARN] 用户未关联机构")
    
    # 3. 测试查询用户的报名记录
    print("\n【测试查询用户报名】")
    start = time.time()
    cursor.execute("SELECT * FROM registrations WHERE applicant_id = %s", (user_id,))
    regs = cursor.fetchall()
    elapsed = (time.time() - start) * 1000
    
    print(f"  [OK] 查询完成 ({elapsed:.2f}ms)")
    print(f"    报名记录数: {len(regs)}")
    
    # 4. 模拟前端可能的查询
    print("\n【模拟前端查询】")
    
    # 4.1 查询所有机构（这可能是问题！）
    print("\n  测试1: 查询所有机构列表")
    start = time.time()
    cursor.execute("SELECT id, name, region, level FROM institutions LIMIT 100")
    insts = cursor.fetchall()
    elapsed = (time.time() - start) * 1000
    print(f"    查询100条 ({elapsed:.2f}ms)")
    
    # 4.2 查询所有机构（不带LIMIT）
    print("\n  测试2: 查询所有机构（无LIMIT）")
    start = time.time()
    cursor.execute("SELECT id, name, region, level FROM institutions")
    all_insts = cursor.fetchall()
    elapsed = (time.time() - start) * 1000
    print(f"    查询{len(all_insts):,}条 ({elapsed:.2f}ms)")
    if elapsed > 1000:
        print(f"    [WARNING] 查询超过1秒！这可能是卡顿原因！")
    
    # 4.3 统计查询
    print("\n  测试3: 按地区统计机构数")
    start = time.time()
    cursor.execute("SELECT region, COUNT(*) FROM institutions GROUP BY region")
    stats = cursor.fetchall()
    elapsed = (time.time() - start) * 1000
    print(f"    统计{len(stats)}个地区 ({elapsed:.2f}ms)")
    
    # 5. 检查EXPLAIN
    print("\n【查询执行计划】")
    
    print("\n  EXPLAIN SELECT * FROM institutions WHERE id = ?")
    cursor.execute("EXPLAIN SELECT * FROM institutions WHERE id = 1")
    explain = cursor.fetchall()
    for row in explain:
        print(f"    type:{row[3]:10s} key:{row[5]} rows:{row[8]}")
    
    print("\n  EXPLAIN SELECT * FROM registrations WHERE applicant_id = ?")
    cursor.execute("EXPLAIN SELECT * FROM registrations WHERE applicant_id = 1")
    explain = cursor.fetchall()
    for row in explain:
        print(f"    type:{row[3]:10s} key:{row[5]} rows:{row[8]}")
    
    # 6. 检查慢查询
    print("\n" + "=" * 80)
    print("可能的问题")
    print("=" * 80)
    
    print("\n1. 如果前端在加载所有机构列表（36,076条）:")
    print("   - 解决方案: 改用分页或搜索API")
    print("   - 相关API: POST /api/institutions/search")
    
    print("\n2. 如果前端在做大量计算:")
    print("   - 检查浏览器开发者工具Console")
    print("   - 检查Network面板，看哪个请求慢")
    
    print("\n3. 建议的前端优化:")
    print("   - 使用虚拟滚动（如果显示大列表）")
    print("   - 使用防抖的搜索（而非全量加载）")
    print("   - 分页加载数据")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        debug_user()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
