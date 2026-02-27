# -*- coding: utf-8 -*-
"""
调试组委会账号登录问题
"""
import pymysql
import bcrypt

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

print("=" * 100)
print("调试组委会账号登录问题")
print("=" * 100)

phone = '13800000127'
expected_password = 'committee2026'

# 1. 查询账号详细信息
print(f"\n[1] 查询账号信息...")
cursor.execute("""
    SELECT id, name, phone, role, password, enabled, created_at, last_login_at
    FROM user_accounts
    WHERE phone = %s
""", (phone,))

account = cursor.fetchone()

if not account:
    print(f"  错误: 未找到手机号为 {phone} 的账号")
    cursor.close()
    conn.close()
    exit(1)

print(f"  ID: {account[0]}")
print(f"  姓名: {account[1]}")
print(f"  手机: {account[2]}")
print(f"  角色: {account[3]}")
print(f"  密码哈希: {account[4][:60] if account[4] else 'NULL'}...")
print(f"  启用状态: {account[5]}")
print(f"  创建时间: {account[6]}")
print(f"  最后登录: {account[7]}")

password_hash = account[4]

# 2. 检查密码字段是否为空
if not password_hash:
    print(f"\n[错误] 密码字段为空！")
    print(f"  该账号没有设置密码")
    cursor.close()
    conn.close()
    exit(1)

# 3. 验证密码哈希
print(f"\n[2] 验证密码...")
print(f"  预期密码: {expected_password}")
print(f"  密码哈希长度: {len(password_hash)}")
print(f"  密码哈希前缀: {password_hash[:10]}")

try:
    # bcrypt验证
    is_valid = bcrypt.checkpw(expected_password.encode('utf-8'), password_hash.encode('utf-8'))
    
    if is_valid:
        print(f"  验证结果: 密码匹配 [OK]")
    else:
        print(f"  验证结果: 密码不匹配 [FAIL]")
        print(f"\n  问题: bcrypt验证失败")
        print(f"  可能原因:")
        print(f"    1. 密码重置脚本执行失败（但没有报错）")
        print(f"    2. 数据库事务未提交")
        print(f"    3. 密码哈希格式不正确")
        
except Exception as e:
    print(f"  验证异常: {str(e)}")
    print(f"  密码哈希可能格式不正确")

# 4. 重新生成正确的密码哈希
print(f"\n[3] 生成新的密码哈希...")
new_hash = bcrypt.hashpw(expected_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"  新哈希: {new_hash}")

# 验证新哈希
verify_new = bcrypt.checkpw(expected_password.encode('utf-8'), new_hash.encode('utf-8'))
print(f"  新哈希验证: {'通过' if verify_new else '失败'}")

# 5. 更新密码
print(f"\n[4] 更新密码...")
cursor.execute("""
    UPDATE user_accounts
    SET password = %s
    WHERE phone = %s
""", (new_hash, phone))

conn.commit()
print(f"  数据库已更新")

# 6. 再次验证
print(f"\n[5] 再次验证...")
cursor.execute("SELECT password FROM user_accounts WHERE phone = %s", (phone,))
updated_hash = cursor.fetchone()[0]

final_check = bcrypt.checkpw(expected_password.encode('utf-8'), updated_hash.encode('utf-8'))
print(f"  最终验证: {'通过' if final_check else '失败'}")

if final_check:
    print(f"\n[成功] 密码已正确设置！")
    print(f"  手机号: {phone}")
    print(f"  密码: {expected_password}")
else:
    print(f"\n[失败] 密码验证仍然失败")

cursor.close()
conn.close()

print("\n" + "=" * 100)
