import random
import time
import requests

BASE = "http://localhost:6031"


def ok(resp, name):
    if resp.status_code != 200:
        raise RuntimeError(f"{name} http={resp.status_code} body={resp.text[:300]}")
    j = resp.json()
    if j.get("success") is False:
        raise RuntimeError(f"{name} biz_fail={j}")
    return j


def main():
    # 1) pick level 2/3 institution
    body = {"keyword": "", "region": None, "level": random.choice(["二级", "三级"]), "page": 0, "size": 20}
    j = ok(requests.post(f"{BASE}/api/institutions/search", json=body, timeout=20), "institution_search")
    inst = (j["data"].get("content") or [])[0]
    inst_id = inst["id"]
    inst_name = inst["name"]

    # 2) register contestant
    phone = "139" + str(int(time.time()))[-8:]
    reg_payload = {
        "phone": phone,
        "password": "Test@2026",
        "confirmPassword": "Test@2026",
        "name": "探测用户" + phone[-4:],
        "title": "主管护师",
        "role": "CONTESTANT",
        "institutionId": inst_id,
    }
    ok(requests.post(f"{BASE}/api/auth/register", json=reg_payload, timeout=20), "auth_register")

    # 3) login
    j_login = ok(
        requests.post(
            f"{BASE}/api/auth/login-with-password",
            json={"phone": phone, "password": "Test@2026"},
            timeout=20,
        ),
        "auth_login",
    )
    token = j_login["data"]["token"]
    comp_id = j_login["data"].get("currentCompetitionId") or 1
    h = {"Authorization": f"Bearer {token}"}

    # 4) create registration
    pname = f"API探测_{int(time.time())}"
    j_create = ok(
        requests.post(
            f"{BASE}/api/registrations",
            json={"competitionId": comp_id, "projectName": pname, "groupType": "BASIC"},
            headers=h,
            timeout=20,
        ),
        "registration_create",
    )
    rid = j_create["data"]["id"]

    # 5) /my
    ok(requests.get(f"{BASE}/api/registrations/my", headers=h, timeout=20), "registrations_my")

    # 6) /{id}
    ok(requests.get(f"{BASE}/api/registrations/{rid}", headers=h, timeout=20), "registrations_detail")

    # 7) upload payment proof twice
    files = {"file": ("proof.png", b"\x89PNG\r\n\x1a\nproof-a", "image/png")}
    j_up1 = ok(
        requests.post(
            f"{BASE}/api/registrations/{rid}/materials",
            headers=h,
            data={"type": "payment_proof"},
            files=files,
            timeout=20,
        ),
        "upload_1",
    )
    j_up2 = ok(
        requests.post(
            f"{BASE}/api/registrations/{rid}/materials",
            headers=h,
            data={"type": "payment_proof"},
            files=files,
            timeout=20,
        ),
        "upload_2_dup",
    )

    # 8) submit
    ok(requests.post(f"{BASE}/api/registrations/{rid}/submit", headers=h, timeout=20), "registration_submit")

    # 9) admin filter
    j_ops = ok(
        requests.post(
            f"{BASE}/api/auth/login-with-password",
            json={"phone": "13800000005", "password": "ops2026"},
            timeout=20,
        ),
        "ops_login",
    )
    ops_h = {"Authorization": f"Bearer {j_ops['data']['token']}"}
    j_filter = ok(
        requests.get(
            f"{BASE}/api/admin/registrations/filter",
            params={"competitionId": 1, "page": 1, "size": 20, "projectName": pname},
            headers=ops_h,
            timeout=30,
        ),
        "admin_filter",
    )
    item = (j_filter["data"].get("content") or [{}])[0]
    mats = item.get("materials") or []
    payment = [m for m in mats if str(m.get("type", "")).lower() == "payment_proof"]
    has_uploaded_at = all("uploadedAt" in m for m in payment) if payment else False

    print("OK")
    print(f"institution={inst_name}({inst_id})")
    print(f"contestant_phone={phone}")
    print(f"registration_id={rid}")
    print(f"upload_dedup_same_id={j_up1['data']['id'] == j_up2['data']['id']}")
    print(f"admin_payment_count={len(payment)} uploadedAt_present={has_uploaded_at}")


if __name__ == "__main__":
    main()
