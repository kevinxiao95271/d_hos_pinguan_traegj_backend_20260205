import bcrypt, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

digits = [str(d) for d in range(10) if d not in (4, 7)]
pwd = ''.join(random.choices(digits, k=6))
hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=10)).decode()
print(f"陈晓红 明文密码: {pwd}")
print(f"陈晓红 BCrypt:   {hashed}")
