import json
import urllib.request
import urllib.error
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:6031"


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


# reviewer
token_r, _, _ = login("13886509429", "review2026")
print("=== REVIEWER /me/profile ===")
payload = {
    "gender": "MALE",
    "position": "评委本人自助修改",
    "backgroundsJson": "[\"MEDICAL\"]",
    "toolsJson": "[\"PDCA\"]",
    "topicsJson": "[\"PATIENT_CARE\"]",
}
c1, b1 = request("GET", "/api/reviewers/me/profile", token=token_r)
print("GET /api/reviewers/me/profile ->", c1)
c2, b2 = request("PUT", "/api/reviewers/me/profile", token=token_r, payload=payload)
print("PUT /api/reviewers/me/profile ->", c2)

# ops should be forbidden on /me path
token_o, _, _ = login("13800000005", "ops2026")
print("\n=== OPS /me/profile ===")
c3, b3 = request("GET", "/api/reviewers/me/profile", token=token_o)
print("GET /api/reviewers/me/profile ->", c3)
if c3 != 200:
    print("body:", b3[:180])
