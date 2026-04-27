import random
import time
import requests

BASE = "http://localhost:6031"
LEVELS = ["三级", "二级", "一级", "未定级", "无等级"]


def try_one(level):
    body = {"keyword": "", "region": None, "level": level, "page": 0, "size": 20}
    r = requests.post(f"{BASE}/api/institutions/search", json=body, timeout=20)
    if r.status_code != 200:
        return level, False, f"search_http_{r.status_code}"
    j = r.json()
    content = (j.get("data") or {}).get("content") or []
    if not content:
        return level, None, "no_institution_for_level"
    inst = random.choice(content)
    phone = "139" + str(int(time.time() * 1000))[-8:]
    payload = {
        "phone": phone,
        "password": "Test@2026",
        "confirmPassword": "Test@2026",
        "name": "等级冒烟" + phone[-4:],
        "title": "主管护师",
        "role": "CONTESTANT",
        "institutionId": inst["id"],
    }
    rr = requests.post(f"{BASE}/api/auth/register", json=payload, timeout=20)
    if rr.status_code == 200 and rr.json().get("success") is not False:
        return level, True, f"ok institution={inst.get('name')} id={inst.get('id')} phone={phone}"
    return level, False, f"http_{rr.status_code} body={rr.text[:160]}"


if __name__ == "__main__":
    for lv in LEVELS:
        level, ok, msg = try_one(lv)
        print(level, ok, msg)
