import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql
from collections import Counter

conn = pymysql.connect(
    host='43.139.18.26', port=3306,
    user='pinguan', password='pinguan2026',
    database='pinguan', charset='utf8mb4',
    connect_timeout=10
)
cur = conn.cursor()

# 取所有评审专家手机号
cur.execute("SELECT id, name, phone, role FROM user_accounts WHERE role='REVIEWER'")
reviewers = cur.fetchall()
print(f'评审专家总数: {len(reviewers)}\n')

def mask(phone):
    if phone and len(phone) == 11 and phone.isdigit():
        return phone[:3] + '0000' + phone[7:]
    return None  # 无法掩码

phones = [(uid, name, phone) for uid, name, phone, _ in reviewers]

# 统计非标准号
non_standard = [(uid, name, phone) for uid, name, phone in phones
                if not (phone and len(phone) == 11 and phone.isdigit())]
print(f'非标准11位手机号（无法套用掩码规则）: {len(non_standard)} 个')
for uid, name, phone in non_standard[:10]:
    print(f'  id={uid}  {name}  phone={phone!r}')

# 可掩码的号
maskable = [(uid, name, phone) for uid, name, phone in phones
            if phone and len(phone) == 11 and phone.isdigit()]
masked_list = [mask(phone) for _, _, phone in maskable]

# 检查掩码后唯一性冲突
dup = {m: cnt for m, cnt in Counter(masked_list).items() if cnt > 1}
print(f'\n可掩码号码数: {len(maskable)}')
if dup:
    print(f'⚠️  掩码后重复（unique冲突）: {len(dup)} 组')
    for m, cnt in list(dup.items())[:10]:
        originals = [(uid, name, phone) for uid, name, phone in maskable if mask(phone) == m]
        print(f'  掩码后={m}  原始号:')
        for uid, name, phone in originals:
            print(f'    id={uid}  {name}  {phone}')
else:
    print('✓ 掩码后无重复，无 unique 约束冲突')

# 检查 OPS/admin 类账号是否混入
cur.execute("SELECT id, name, phone, role FROM user_accounts WHERE role != 'REVIEWER'")
others = cur.fetchall()
reviewer_phones = {phone for _, _, phone in phones}
overlap = [(uid, name, phone, role) for uid, name, phone, role in others
           if phone in reviewer_phones]
if overlap:
    print(f'\n⚠️  非评委账号与评委手机号相同: {overlap}')
else:
    print('✓ 无非评委账号与评委手机重叠')

# 确认全局 unique 约束（掩码后是否与其他角色冲突）
cur.execute("SELECT phone FROM user_accounts WHERE role != 'REVIEWER'")
other_phones = {row[0] for row in cur.fetchall()}
mask_conflict_with_others = [
    (uid, name, phone, mask(phone))
    for uid, name, phone in maskable
    if mask(phone) in other_phones
]
if mask_conflict_with_others:
    print(f'\n⚠️  掩码后与其他角色手机号冲突: {len(mask_conflict_with_others)} 个')
    for uid, name, phone, m in mask_conflict_with_others[:5]:
        print(f'  id={uid}  {name}  {phone} -> {m}（与其他账号冲突）')
else:
    print('✓ 掩码后与其他角色无手机号冲突')

cur.close()
conn.close()
print('\n=== 结论见下方 ===')
