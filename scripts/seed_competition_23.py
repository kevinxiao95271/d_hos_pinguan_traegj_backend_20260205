import os
import datetime
import random
import pymysql
import requests


BASE_URL = os.getenv("PINGUAN_BASE_URL", "http://localhost:6031")


def require_env(name):
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        raise RuntimeError("missing env: PINGUAN_DB_HOST/PORT/USER/PASSWORD/NAME")
    return value


DB_HOST = require_env("PINGUAN_DB_HOST")
DB_PORT = int(require_env("PINGUAN_DB_PORT"))
DB_USER = require_env("PINGUAN_DB_USER")
DB_PASSWORD = require_env("PINGUAN_DB_PASSWORD")
DB_NAME = require_env("PINGUAN_DB_NAME")


def api_post(path, token, payload):
    resp = requests.post(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message") or f"request failed: {path}")
    return data["data"]


def api_put(path, token, payload):
    resp = requests.put(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message") or f"request failed: {path}")
    return data["data"]


def api_get(path, token):
    resp = requests.get(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message") or f"request failed: {path}")
    return data["data"]


def login(phone, name, role, institution_id=None):
    payload = {
        "phone": phone,
        "name": name,
        "title": "Title",
        "role": role,
        "institutionId": institution_id,
    }
    resp = requests.post(BASE_URL + "/api/auth/login", json=payload, timeout=30).json()
    if not resp.get("success"):
        raise RuntimeError(resp.get("message") or "login failed")
    return resp["data"]


def ensure_competition(conn, competition_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM competitions WHERE id=%s", (competition_id,))
        if cursor.fetchone()[0] > 0:
            return
        now = datetime.datetime.now()
        cursor.execute(
            "INSERT INTO competitions (id, name, stage, register_start, register_end, book_review_start, book_review_end, "
            "interview_start, interview_end, final_start, final_end, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                competition_id,
                "2026年省级质量改进赛-测试23",
                "REGISTER",
                now - datetime.timedelta(days=5),
                now + datetime.timedelta(days=15),
                now + datetime.timedelta(days=16),
                now + datetime.timedelta(days=25),
                now + datetime.timedelta(days=26),
                now + datetime.timedelta(days=30),
                now + datetime.timedelta(days=31),
                now + datetime.timedelta(days=35),
                now,
            ),
        )
    conn.commit()


def cleanup_empty_competitions(conn, keep_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT c.id FROM competitions c "
            "LEFT JOIN registrations r ON r.competition_id = c.id "
            "GROUP BY c.id HAVING COUNT(r.id) = 0"
        )
        empty_ids = [row[0] for row in cursor.fetchall() if row[0] != keep_id]
        if not empty_ids:
            return []
        cursor.execute("DELETE FROM competition_templates WHERE competition_id IN (" + ",".join(["%s"] * len(empty_ids)) + ")", empty_ids)
        cursor.execute("DELETE FROM competitions WHERE id IN (" + ",".join(["%s"] * len(empty_ids)) + ")", empty_ids)
    conn.commit()
    return empty_ids


def main():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=False,
    )
    ensure_competition(conn, 23)
    deleted_ids = cleanup_empty_competitions(conn, 23)

    committee = login("13800000009", "Committee", "COMMITTEE")
    committee_token = committee["token"]

    institutions = api_get("/api/institutions", committee_token)
    institutions = institutions[:20]
    competitions = api_get("/api/competitions", committee_token)
    competition_id = 23
    if not any(c["id"] == competition_id for c in competitions):
        raise RuntimeError("competition 23 not found")

    method_list = api_get("/api/dictionaries/method", committee_token)
    method_codes = [item["code"] for item in method_list] or ["qc_problem"]

    group_types = ["BASIC", "COMPREHENSIVE", "ADVANCED"]
    group_codes = ["A1", "A2", "B1", "B2"]

    created_ids = []
    for idx, inst in enumerate(institutions, start=1):
        contestant = login(f"1398888{idx:04d}", f"测试参赛者{idx}", "CONTESTANT", inst["id"])
        registration = api_post("/api/registrations", contestant["token"], {
            "competitionId": competition_id,
            "institutionId": inst["id"],
            "applicantId": contestant["id"],
            "projectName": f"项目-{inst['name']}",
            "groupType": group_types[idx % 3],
        })
        reg_id = registration["id"]
        api_put(f"/api/registrations/{reg_id}/members", contestant["token"], {
            "items": [
                {"role": "PARTICIPANT", "name": "成员A", "title": "护士", "department": "护理部"},
                {"role": "PARTICIPANT", "name": "成员B", "title": "医师", "department": "门诊部"},
                {"role": "MENTOR", "name": "辅导员A", "title": "主任", "department": "医务处"},
            ]
        })
        api_put(f"/api/registrations/{reg_id}/activity", contestant["token"], {
            "theme": f"{inst['name']}-活动主题",
            "keywords": "质量,改进",
            "subjectTypeCode": "patient_care",
            "methodCode": random.choice(method_codes),
            "experienceImproveCode": "appointment",
            "qualityTopicCode": "stemi",
            "avgWorkYears": 6,
            "avgAge": 32,
            "crossDepartment": False,
        })
        api_put(f"/api/registrations/{reg_id}/summary", contestant["token"], {
            "theme": f"{inst['name']}-摘要主题",
            "plan": "计划",
            "problem": "问题结构与对策措施探讨",
            "action": "对策行动过程",
            "success": "成功表现",
            "discussion": "讨论总结",
        })
        api_post(f"/api/registrations/{reg_id}/submit", contestant["token"], {})
        api_post(f"/api/registrations/{reg_id}/approve", committee_token, {})
        created_ids.append(reg_id)

    random.shuffle(created_ids)
    group_map = {code: [] for code in group_codes}
    for idx, reg_id in enumerate(created_ids):
        group_map[group_codes[idx % len(group_codes)]].append(reg_id)

    for code, ids in group_map.items():
        if not ids:
            continue
        api_post("/api/admin/registrations/batch-classify", committee_token, {
            "registrationIds": ids,
            "groupCode": code,
        })

    print({
        "competitionId": competition_id,
        "createdRegistrations": len(created_ids),
        "deletedCompetitions": deleted_ids,
    })


if __name__ == "__main__":
    main()
