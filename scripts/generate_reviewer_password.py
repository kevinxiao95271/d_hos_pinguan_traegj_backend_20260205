# -*- coding: utf-8 -*-
"""
生成评审专家默认密码的bcrypt hash (兼容Java jbcrypt 0.4)
"""
import bcrypt

# 默认密码：reviewer2026
password = "reviewer2026"

# 生成bcrypt hash
hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
hash_str = hash_bytes.decode('utf-8')

# 转换为Java兼容格式 ($2b$ -> $2a$)
if hash_str.startswith('$2b$'):
    hash_str = '$2a$' + hash_str[4:]

print(f"密码: {password}")
print(f"Hash: {hash_str}")
print(f"\n使用此hash更新脚本...")
