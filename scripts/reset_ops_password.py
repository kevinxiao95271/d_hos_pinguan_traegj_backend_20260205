import paramiko
import bcrypt

phone = "13800000005"
new_password = "ops2026"

hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
print(f"bcrypt hash: {hashed}")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("81.71.44.180", username="root", password="Yiguo9527_")

update_sql = f"UPDATE user_accounts SET password='{hashed}' WHERE phone='{phone}';"
select_sql = f"SELECT id, phone, name, role FROM user_accounts WHERE phone='{phone}';"

cmd = (
    f'mysql -h gz-cdb-bq7gk3k5.sql.tencentcdb.com -P 63606 '
    f'-u root -pYiguo9527_ d_hos_pinguan_traegj_20260205 '
    f'-e "{update_sql} {select_sql}"'
)

stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
ssh.close()

if out:
    print("结果：")
    print(out)
if err and "Warning" not in err:
    print("错误：", err)
else:
    print("密码重置成功")
