"""
从 insert_experts.sql 中提取 phone + password_hash，
生成 UPDATE user_accounts SET password=... WHERE phone=... 语句
"""
import re, json, csv

INSERT_SQL = 'scripts/insert_experts.sql'
PASSWORDS_JSON = 'scripts/expert_passwords.json'
OUTPUT_SQL = 'scripts/update_reviewer_passwords.sql'
OUTPUT_CSV = 'scripts/expert_passwords.csv'

# 从 INSERT SQL 中提取 (phone, hash)
with open(INSERT_SQL, encoding='utf-8') as f:
    content = f.read()

# 每行一条 INSERT，格式：VALUES ('name', 'phone', 'hash', ...)
pattern = re.compile(r"VALUES\s*\('([^']+)',\s*'(\d{11})',\s*'(\$2a\$[^']+)'", re.MULTILINE)
matches = pattern.findall(content)

phone_to_hash = {phone: h for name, phone, h in matches}
print(f'从 INSERT SQL 提取到 {len(phone_to_hash)} 条记录')

# 生成 UPDATE SQL
lines = [
    "-- update_reviewer_passwords.sql",
    "-- 更新已存在的 REVIEWER 账号密码（$2a$ 前缀，与 jBCrypt 兼容）",
    "",
]
for phone, h in phone_to_hash.items():
    lines.append(f"UPDATE `user_accounts` SET `password` = '{h}' WHERE `phone` = '{phone}';")

with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'已生成 {OUTPUT_SQL}，共 {len(phone_to_hash)} 条 UPDATE')

# 同步重建 CSV（关闭 Excel 后才能写）
with open(PASSWORDS_JSON, encoding='utf-8') as f:
    pwd_data = json.load(f)

with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'phone', 'password'])
    writer.writeheader()
    writer.writerows(pwd_data)
print(f'已重建 {OUTPUT_CSV}，共 {len(pwd_data)} 条')
