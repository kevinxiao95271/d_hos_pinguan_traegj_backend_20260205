#!/usr/bin/env python3
import io, sys, paramiko

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=15)

def run(cmd):
    _, out, err = ssh.exec_command(cmd, timeout=20)
    o = out.read().decode('utf-8', 'replace').strip()
    e = err.read().decode('utf-8', 'replace').strip()
    if o: print(o)
    if e: print('ERR:', e)

# 1. 全局 nginx.conf 的 http 块加 100m（没有才加）
run("grep -q 'client_max_body_size' /etc/nginx/nginx.conf || sed -i '/http {/a\\    client_max_body_size 100m;' /etc/nginx/nginx.conf && echo global_done")

# 2. conf.d 里所有已有的改成 100m
run("sed -i 's/client_max_body_size [0-9]*[mMgGkK];/client_max_body_size 100m;/g' /etc/nginx/conf.d/*.conf && echo updated_existing")

# 3. conf.d 里没有的，在第一个 server { 后插入
run("for f in /etc/nginx/conf.d/*.conf; do grep -q 'client_max_body_size' \"$f\" || sed -i '/server {/a\\    client_max_body_size 100m;' \"$f\"; done && echo added_missing")

# 验证
run("grep -rn 'client_max_body_size' /etc/nginx/")
run("nginx -t && nginx -s reload && echo 'nginx 重载完成 ✅'")

ssh.close()
