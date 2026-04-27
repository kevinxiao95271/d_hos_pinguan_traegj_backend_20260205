import json
import urllib.request
import urllib.error
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:6031"
TARGET_REVIEWER_ID = 5


def request(method, path, token=None, payload=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read().decode("utf-8")
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return e.code, body


def login(phone, password):
    code, body = request(
        "POST",
        "/api/auth/login-with-password",
        payload={"phone": phone, "password": password},
    )
    if code != 200:
        return None, code, body
    obj = json.loads(body)
    data = obj.get("data") or {}
    return data.get("token"), 200, obj


accounts = [
    ("OPS", "13800000005", "ops2026"),
    ("COMMITTEE_ADMIN", "13800000127", "ops2026"),
    ("REVIEWER", "13886509429", "review2026"),
]

payload = {
    "gender": "MALE",
    "position": "测试修改",
    "backgroundsJson": "[\"MEDICAL\"]",
    "toolsJson": "[\"PDCA\"]",
    "topicsJson": "[\"PATIENT_CARE\"]",
}

for role, phone, pwd in accounts:
    token, code, resp = login(phone, pwd)
    print(f"\n=== {role} {phone} 登录结果 ===")
    if not token:
        print(f"登录失败 http={code} body={str(resp)[:200]}")
        continue
    print("登录成功")
    c1, b1 = request("GET", f"/api/admin/reviewers/{TARGET_REVIEWER_ID}/profile", token=token)
    print(f"GET /api/admin/reviewers/{{id}}/profile -> {c1}")
    c2, b2 = request("PUT", f"/api/admin/reviewers/{TARGET_REVIEWER_ID}/profile", token=token, payload=payload)
    print(f"PUT /api/admin/reviewers/{{id}}/profile -> {c2}")
    if c2 != 200:
        print(f"PUT body: {b2[:200]}")
