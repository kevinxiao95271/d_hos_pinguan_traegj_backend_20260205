import bcrypt, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

digits = '012356890'
pwd = ''.join(random.choice(digits) for _ in range(6))
while pwd[0] == '0':
    pwd = ''.join(random.choice(digits) for _ in range(6))

raw_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(10)).decode()
h2a = raw_hash[:2] + 'a' + raw_hash[3:]

print(f'明文密码: {pwd}')
print(f'BCrypt密文: {h2a}')
print()
sql = "UPDATE user_accounts SET password = '{}' WHERE id = 742 AND name = '诸建武' AND phone = '13758106153' AND role = 'REVIEWER';".format(h2a)
print('SQL:')
print(sql)
