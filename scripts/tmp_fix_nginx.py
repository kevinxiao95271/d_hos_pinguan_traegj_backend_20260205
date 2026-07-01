#!/usr/bin/env python3
import io, sys, paramiko

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=15)

def run(cmd):
    _, out, err = ssh.exec_command(cmd, timeout=15)
    o = out.read().decode('utf-8', 'replace').strip()
    e = err.read().decode('utf-8', 'replace').strip()
    if o: print(o)
    if e: print('ERR:', e)

# 恢复原始配置（上次写坏了），直接覆写正确内容
conf = (
    "server {\n"
    "    listen 6039;\n"
    "    server_name _;\n"
    "\n"
    "    client_max_body_size 50m;\n"
    "\n"
    "    access_log /var/log/nginx/mirror_access.log combined;\n"
    "    error_log /var/log/nginx/mirror_error.log;\n"
    "\n"
    "    gzip on;\n"
    "    gzip_vary on;\n"
    "    gzip_min_length 1024;\n"
    "    gzip_types text/plain text/css text/xml text/javascript\n"
    "               application/x-javascript application/xml+rss\n"
    "               application/javascript application/json;\n"
    "\n"
    "    location /pgds {\n"
    "        alias /data/pgds/dist;\n"
    "        index index.html;\n"
    "        try_files $uri $uri/ /pgds/index.html;\n"
    "    }\n"
    "\n"
    "    location /api/ {\n"
    "        proxy_pass http://localhost:6031/api/;\n"
    "        proxy_http_version 1.1;\n"
    '        proxy_set_header Upgrade $http_upgrade;\n'
    '        proxy_set_header Connection "upgrade";\n'
    "        proxy_set_header Host $host;\n"
    "        proxy_set_header X-Real-IP $remote_addr;\n"
    "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
    "        proxy_set_header X-Forwarded-Proto $scheme;\n"
    "        proxy_cache_bypass $http_upgrade;\n"
    "    }\n"
    "\n"
    "    location / {\n"
    "        root /data/pinguan_frontend;\n"
    "        index index.html;\n"
    "        try_files $uri $uri/ /index.html;\n"
    "    }\n"
    "}\n"
)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/conf.d/pinguan.conf', 'w') as f:
    f.write(conf)
sftp.close()
print('配置已写入')

run('nginx -t')
run('nginx -s reload && echo "nginx已重载 ✅"')
ssh.close()
