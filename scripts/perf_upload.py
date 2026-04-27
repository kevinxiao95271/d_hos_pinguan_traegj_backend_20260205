import requests
import time
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:6031"

# login
r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13972433235", "password": "test1234"})
token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# 测 MinIO RTT（直接 ping MinIO 健康接口）
import socket
minio_host = "119.167.165.27"
minio_port = 58010

def tcp_rtt(host, port, n=5):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            s = socket.create_connection((host, port), timeout=5)
            t1 = time.perf_counter()
            s.close()
            times.append((t1 - t0) * 1000)
        except Exception as e:
            times.append(None)
    return times

print("=== MinIO TCP RTT ===")
rtts = tcp_rtt(minio_host, minio_port)
valid = [x for x in rtts if x]
for i, v in enumerate(rtts):
    print(f"  {i+1}: {v:.1f} ms" if v else f"  {i+1}: 超时")
if valid:
    print(f"  平均: {sum(valid)/len(valid):.1f} ms")

# 测 MySQL RTT
mysql_host = "gz-cdb-bq7gk3k5.sql.tencentcdb.com"
mysql_port = 63606
print("\n=== MySQL TCP RTT ===")
rtts2 = tcp_rtt(mysql_host, mysql_port)
valid2 = [x for x in rtts2 if x]
for i, v in enumerate(rtts2):
    print(f"  {i+1}: {v:.1f} ms" if v else f"  {i+1}: 超时")
if valid2:
    print(f"  平均: {sum(valid2)/len(valid2):.1f} ms")

# 用真实文件模拟上传（创建临时文件）
reg_id = 50  # 找一个存在的草稿报名id

def make_dummy_file(size_kb, suffix):
    path = f"scripts/tmp_perf_file.{suffix}"
    with open(path, "wb") as f:
        f.write(b"A" * size_kb * 1024)
    return path

print("\n=== 上传性能（模拟文件）===")
for label, size_kb, suffix, ftype in [
    ("22KB docx", 22, "docx", "registration_form_doc"),
    ("679KB pdf", 679, "pdf",  "registration_form_pdf"),
]:
    path = make_dummy_file(size_kb, suffix)
    times = []
    for i in range(5):
        with open(path, "rb") as f:
            t0 = time.perf_counter()
            resp = requests.post(
                f"{BASE}/api/registrations/{reg_id}/materials",
                headers=headers,
                data={"type": ftype},
                files={"file": (f"test.{suffix}", f, "application/octet-stream")}
            )
            t1 = time.perf_counter()
        ms = (t1 - t0) * 1000
        times.append(ms)
        ok = resp.json().get("success", False)
        print(f"  {label} 第{i+1}次: {ms:.0f}ms  {'OK' if ok else 'FAIL: '+str(resp.json().get('message',''))}")
    print(f"  → 平均: {sum(times)/len(times):.0f}ms  最小: {min(times):.0f}ms  最大: {max(times):.0f}ms\n")
    os.remove(path)
