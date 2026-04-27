import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:6031"

r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13972433235", "password": "test1234"})
d = r.json()
print("登录:", d.get("success"), d.get("message", ""))
if not d.get("success"):
    sys.exit(1)

token = d["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

r2 = requests.get(f"{BASE}/api/registrations/count-by-institution?competitionId=1", headers=headers)
print("count-by-institution:", r2.json())
