import requests
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:6031"

# login
r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13972433235", "password": "test1234"})
token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

url = f"{BASE}/api/registrations/count-by-institution?competitionId=1"

times = []
print(f"{'次数':<6} {'耗时(ms)'}")
print("-" * 20)
for i in range(20):
    t0 = time.perf_counter()
    resp = requests.get(url, headers=headers)
    t1 = time.perf_counter()
    ms = (t1 - t0) * 1000
    times.append(ms)
    print(f"{i+1:<6} {ms:.1f}")

print("-" * 20)
print(f"最小: {min(times):.1f} ms")
print(f"最大: {max(times):.1f} ms")
print(f"平均: {sum(times)/len(times):.1f} ms")
times_sorted = sorted(times)
p50 = times_sorted[len(times_sorted)//2]
p90 = times_sorted[int(len(times_sorted)*0.9)]
print(f"P50:  {p50:.1f} ms")
print(f"P90:  {p90:.1f} ms")
