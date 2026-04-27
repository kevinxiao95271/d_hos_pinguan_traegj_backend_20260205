import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:6031"


def post(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        BASE + path, data=json.dumps(data).encode("utf-8"), headers=headers
    )
    return json.loads(urllib.request.urlopen(req, timeout=8).read())


def put(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="PUT",
    )
    return json.loads(urllib.request.urlopen(req, timeout=8).read())


def get(path, token):
    req = urllib.request.Request(
        BASE + path, headers={"Authorization": "Bearer " + token}
    )
    return json.loads(urllib.request.urlopen(req, timeout=8).read())


login = post(
    "/api/auth/login-with-password", {"phone": "13800000005", "password": "ops2026"}
)
token = login["data"]["token"]
reviewers = get("/api/admin/reviewers/list", token)["data"]
reviewer_id = reviewers[0]["id"]
print("reviewer_id=", reviewer_id)

print("\nGET before")
print(
    json.dumps(
        get(f"/api/admin/reviewers/{reviewer_id}/profile", token),
        ensure_ascii=False,
        indent=2,
    )[:600]
)

payload = {
    "gender": "FEMALE",
    "position": "护理部副主任",
    "idNumber": "330102198901011234",
    "idNumberMasked": "330102********1234",
    "idCardFrontUrl": "reviewer-profiles/123/front.jpg",
    "idCardBackUrl": "reviewer-profiles/123/back.jpg",
    "bankName": "中国工商银行杭州武林支行",
    "bankCardNo": "6222001234567890123",
    "bankCardNoMasked": "6222***********0123",
    "backgroundsJson": "[\"NURSING\",\"QUALITY_MANAGEMENT\"]",
    "toolsJson": "[\"PDCA\",\"QFD\",\"RCA\"]",
    "topicsJson": "[\"PATIENT_CARE\",\"MEDICAL_QUALITY_SAFETY\"]",
}

print("\nPUT")
print(
    json.dumps(
        put(f"/api/admin/reviewers/{reviewer_id}/profile", payload, token),
        ensure_ascii=False,
        indent=2,
    )[:800]
)

print("\nGET after")
print(
    json.dumps(
        get(f"/api/admin/reviewers/{reviewer_id}/profile", token),
        ensure_ascii=False,
        indent=2,
    )[:800]
)
