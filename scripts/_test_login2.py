# -*- coding: utf-8 -*-
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:6031"
r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13800000005", "password": "ops2026"},
                  timeout=8)
print(f"status: {r.status_code}")
print(r.text[:800])
