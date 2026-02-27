# -*- coding: utf-8 -*-
"""
详细检查组委会账号密码
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
print("详细检查组委会账号")
print("=" * 100)

phone = '13800000127'
expected_password = 'committee2026'

# 查询账号所有信息
cursor.execute("SELECT * FROM user_accounts WHERE phone = %s", (phone,))
result = cursor.fetchone()

if not result:
    print(f"未找到账号")
    cursor.close()
    conn.close()
    exit(1)

# 获取列名
cursor.execute("DESC user_accounts")
columns = [col[0] for col in cursor.fetchall()]

print(f"\n账号完整信息:")
for i, col_name in enumerate(columns):
    value = result[i]
    if col_name == 'password' and value:
        print(f"  {col_name}: {value[:80]}")
        print(f"    长度: {len(value)}")
        print(f"    前缀: {value[:7]}")
    else:
        print(f"  {col_name}: {value}")

# 获取password字段
password_hash = None
for i, col_name in enumerate(columns):
    if col_name == 'password':
        password_hash = result[i]
        break

if not password_hash:
    print(f"\n[错误] 密码字段为空或不存在")
    cursor.close()
    conn.close()
    exit(1)

print(f"\n密码哈希详情:")
print(f"  完整哈希: {password_hash}")
print(f"  长度: {len(password_hash)}")
print(f"  算法标识: {password_hash[:4] if len(password_hash) >= 4 else 'N/A'}")

# 尝试用不同方式验证
print(f"\n验证测试:")

# 方式1: 直接bcrypt验证
try:
    result1 = bcrypt.checkpw(expected_password.encode('utf-8'), password_hash.encode('utf-8'))
    print(f"  bcrypt.checkpw: {result1}")
except Exception as e:
    print(f"  bcrypt.checkpw: 失败 - {str(e)}")

# 方式2: 不同编码
try:
    result2 = bcrypt.checkpw(expected_password.encode('utf-8'), password_hash.encode('latin-1'))
    print(f"  bcrypt (latin-1): {result2}")
except Exception as e:
    print(f"  bcrypt (latin-1): 失败 - {str(e)}")

# 生成一个测试hash并验证
print(f"\n生成测试哈希:")
test_hash = bcrypt.hashpw(expected_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"  新哈希: {test_hash}")

test_verify = bcrypt.checkpw(expected_password.encode('utf-8'), test_hash.encode('utf-8'))
print(f"  新哈希验证: {test_verify}")

# 对比两个hash
print(f"\n哈希对比:")
print(f"  数据库中: {password_hash[:30]}...")
print(f"  新生成的: {test_hash[:30]}...")
print(f"  前缀相同: {password_hash[:7] == test_hash[:7]}")

# 尝试手动更新为新hash
print(f"\n是否更新密码? (新生成的hash)")
cursor.execute("UPDATE user_accounts SET password = %s WHERE phone = %s", (test_hash, phone))
conn.commit()
print(f"  已更新")

# 再次验证
cursor.execute("SELECT password FROM user_accounts WHERE phone = %s", (phone,))
updated_hash = cursor.fetchone()[0]

final_verify = bcrypt.checkpw(expected_password.encode('utf-8'), updated_hash.encode('utf-8'))
print(f"  更新后验证: {final_verify}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
print(f"组委会账号密码调试完成")
print(f"  手机号: {phone}")
print(f"  密码: {expected_password}")
print(f"  验证状态: {'通过' if final_verify else '失败'}")
print("=" * 100)
