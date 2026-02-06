import os
import json
import requests


BASE_URL = os.getenv("PINGUAN_BASE_URL", "http://localhost:6031")


def api_post(path, token, payload):
    resp = requests.post(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    return resp.json()


def api_put(path, token, payload):
    resp = requests.put(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    return resp.json()


def api_get(path, token):
    resp = requests.get(BASE_URL + path, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    return resp.json()


def login(phone, name, role, institution_id=None, reviewer_group=None, interview_group=None, background=None):
    payload = {
        "phone": phone,
        "name": name,
        "title": "Title",
        "role": role,
        "institutionId": institution_id,
        "reviewerGroupCode": reviewer_group,
        "interviewGroupCode": interview_group,
        "expertBackground": background,
    }
    resp = requests.post(BASE_URL + "/api/auth/login", json=payload, timeout=30).json()
    if not resp.get("success"):
        raise RuntimeError(resp)
    return resp["data"]


def main():
    committee = login("13800000009", "Committee", "COMMITTEE")
    committee_token = committee["token"]
    institutions = api_get("/api/institutions", committee_token)["data"]
    institution_id = institutions[0]["id"]

    contestant = login("13999990001", "流程参赛者", "CONTESTANT", institution_id)
    contestant_token = contestant["token"]
    reviewer = login("13799990001", "流程评审", "REVIEWER", None, "B1", "B1", "MEDICAL")
    reviewer_token = reviewer["token"]

    competitions = api_get("/api/competitions", committee_token)["data"]
    competition_id = sorted(competitions, key=lambda x: x["id"])[-1]["id"]

    registration = api_post("/api/registrations", contestant_token, {
        "competitionId": competition_id,
        "institutionId": institution_id,
        "applicantId": contestant["id"],
        "projectName": "流程项目-进阶组",
        "groupType": "ADVANCED",
    })

    reg_id = registration["data"]["id"]

    api_post(f"/api/registrations/{reg_id}/members", contestant_token, {
        "items": [
            {"role": "PARTICIPANT", "name": "成员A", "title": "护士", "department": "护理部"},
            {"role": "MENTOR", "name": "辅导员A", "title": "主任", "department": "医务处"},
        ]
    })

    api_post(f"/api/registrations/{reg_id}/activity", contestant_token, {
        "theme": "流程活动主题",
        "keywords": "质量,改进",
        "subjectTypeCode": "patient_care",
        "methodCode": "qc_problem",
        "experienceImproveCode": "appointment",
        "qualityTopicCode": "stemi",
        "avgWorkYears": 6,
        "avgAge": 32,
        "crossDepartment": False,
    })

    api_post(f"/api/registrations/{reg_id}/summary", contestant_token, {
        "theme": "流程摘要主题",
        "plan": "计划内容",
        "problem": "问题结构与对策",
        "action": "对策行动过程",
        "success": "成功表现",
        "discussion": "讨论总结",
    })

    submit_resp = api_post(f"/api/registrations/{reg_id}/submit", contestant_token, {})
    return_resp = api_post(f"/api/registrations/{reg_id}/return", committee_token, {})
    resubmit_resp = api_post(f"/api/registrations/{reg_id}/submit", contestant_token, {})
    approve_resp = api_post(f"/api/registrations/{reg_id}/approve", committee_token, {})

    batch_resp = api_post("/api/admin/registrations/batch-classify", committee_token, {
        "registrationIds": [reg_id],
        "groupCode": "B1",
    })

    assign_resp = api_post("/api/admin/reviews/tasks", committee_token, {
        "registrationId": reg_id,
        "reviewerId": reviewer["id"],
        "stage": "BOOK",
    })

    status_resp = api_put("/api/reviews/tasks/status", reviewer_token, {
        "reviewTaskId": assign_resp["data"]["id"],
        "status": "CONFIRMED",
    })

    score_resp = api_post("/api/reviews/scores", reviewer_token, {
        "reviewTaskId": assign_resp["data"]["id"],
        "plan": 20,
        "problem": 20,
        "action": 20,
        "success": 15,
        "review": 10,
        "operation": 10,
        "presentation": 5,
        "highlight": "结构清晰",
        "weakness": "细节可加强",
    })

    detail_resp = api_get(f"/api/registrations/{reg_id}/review-details", contestant_token)

    return_score_resp = api_post("/api/admin/reviews/scores/return", committee_token, {
        "reviewTaskId": assign_resp["data"]["id"],
    })

    score_resp2 = api_post("/api/reviews/scores", reviewer_token, {
        "reviewTaskId": assign_resp["data"]["id"],
        "plan": 18,
        "problem": 18,
        "action": 18,
        "success": 14,
        "review": 9,
        "operation": 9,
        "presentation": 4,
        "highlight": "数据扎实",
        "weakness": "表达可提升",
    })

    output = {
        "registration": registration,
        "submit": submit_resp,
        "return": return_resp,
        "resubmit": resubmit_resp,
        "approve": approve_resp,
        "batchClassify": batch_resp,
        "assignReview": assign_resp,
        "confirmTask": status_resp,
        "submitScore": score_resp,
        "reviewDetails": detail_resp,
        "returnScore": return_score_resp,
        "rescore": score_resp2,
    }

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "e2e_api_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(out_path)


if __name__ == "__main__":
    main()
