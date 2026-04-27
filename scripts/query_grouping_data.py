import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', username='root', password='Yiguo9527_')

DB = 'mysql -h gz-cdb-bq7gk3k5.sql.tencentcdb.com -P 63606 -u root -pYiguo9527_ d_hos_pinguan_traegj_20260205'


def run(sql):
    cmd = f"{DB} -e \"{sql}\""
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    if err and 'Warning' not in err:
        print('ERR:', err)
    return out


print("=== 1. registrations 所有状态分布 ===")
print(run("""
SELECT status, group_type, COUNT(*) AS cnt
FROM registrations
GROUP BY status, group_type
ORDER BY status, group_type
"""))

print("=== 2. activity_infos 有多少条数据 ===")
print(run("SELECT COUNT(*) AS total FROM activity_infos"))

print("=== 3. 有activity_infos的registrations中 SUBMITTED/APPROVED状态数量 ===")
print(run("""
SELECT r.status, r.group_type, COUNT(*) AS cnt
FROM registrations r
INNER JOIN activity_infos ai ON ai.registration_id = r.id
GROUP BY r.status, r.group_type
ORDER BY r.status, r.group_type
"""))

print("=== 4. 取10条 activity_infos 看method_code值 ===")
print(run("""
SELECT ai.registration_id, r.group_type, r.status, ai.method_code, ai.quality_topic_code
FROM activity_infos ai
JOIN registrations r ON r.id = ai.registration_id
LIMIT 10
"""))

ssh.close()
print("完成")
