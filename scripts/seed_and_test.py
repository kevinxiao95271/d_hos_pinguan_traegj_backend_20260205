import os
import json
import time
import random
import datetime
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


def api_headers(token):
    return {"Authorization": f"Bearer {token}"}


def api_post(path, token, payload):
    resp = requests.post(BASE_URL + path, headers=api_headers(token), json=payload, timeout=30)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message") or f"request failed: {path}")
    return data["data"]


def api_get(path, token):
    resp = requests.get(BASE_URL + path, headers=api_headers(token), timeout=30)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message") or f"request failed: {path}")
    return data["data"]


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
        raise RuntimeError(resp.get("message") or "login failed")
    return resp["data"]


institutions = [
    ("浙江大学医学院附属第二医院（浙二医院）", "1233000047053349XG"),
    ("浙江省中医院", "1233000047053325XJ"),
    ("杭州市中医院", "12330100470533734G"),
    ("浙江大学医学院附属邵逸夫医院（邵逸夫医院）", "12330000470533579W"),
    ("浙江大学医学院附属妇产科医院（浙江省妇保医院）", "12330000470533578B"),
    ("浙江省立同德医院", "12330000470533388X"),
    ("浙江医院", "12330000470533331W"),
    ("浙江大学医学院附属第一医院（浙一医院）", "12330000470533435J"),
    ("浙江省人民医院", "12330000470533390P"),
    ("杭州市第一人民医院", "12330100470533733L"),
    ("浙江大学医学院附属儿童医院（浙江省儿童医院）", "12330000470533493L"),
    ("浙江省中西医结合医院（杭州市红十字会医院）", "12330100470533735E"),
    ("浙江省肿瘤医院", "1233000047053330XK"),
    ("浙江大学医学院附属口腔医院（浙江省口腔医院）", "12330000470533490Q"),
    ("杭州市肝病研究所（杭州市西溪医院）", "12330100470533732N"),
    ("宁波市第一医院", "12330200470536094X"),
    ("宁波市第二医院（中国科学院大学宁波华美医院）", "12330200470536093Y"),
    ("宁波市医疗中心李惠利医院", "12330200470536096W"),
    ("温州医科大学附属第二医院（温医二院）", "1233030047053070XK"),
    ("绍兴市人民医院", "12330600470677541L"),
    ("嘉兴市第一医院", "1233040047067683XG"),
    ("湖州市中心医院", "12330500470676917R"),
    ("金华市中心医院", "12330700470677134D"),
    ("衢州市人民医院", "12330800470677252B"),
    ("台州医院", "12331000470677532X"),
    ("丽水市中心医院", "1233110047067736X9"),
    ("舟山医院", "1233090047067743X4"),
    ("杭州师范大学附属医院", "12330100470533736C"),
    ("浙江中医药大学附属第二医院（新华医院）", "12330000470533262H"),
    ("浙江中医药大学附属第三医院（中山医院）", "12330000470533261J"),
    ("温州医科大学附属眼视光医院", "12330300470530711L"),
    ("宁波大学医学院附属医院", "12330200470536095W"),
    ("绍兴文理学院附属医院", "12330600470677542J"),
]


subject_types = [
    ("patient_care", "病人照护"),
    ("case_quality", "病历质量"),
    ("time_efficiency", "时间效率"),
    ("cost_efficiency", "成本效益"),
    ("safety_env", "安全环境"),
    ("satisfaction", "满意度"),
    ("education", "教育训练"),
    ("info", "医疗信息"),
    ("quality_safety", "医疗质量与安全"),
    ("process", "流程改造"),
]

methods = [
    ("qc_problem", "品管圈-问题解决"),
    ("qc_topic", "品管圈-课题达成"),
    ("project_improve", "专案改善"),
    ("balanced_scorecard", "平衡计分卡"),
    ("root_cause", "根本原因分析"),
    ("fmea", "失效模式与效应分析"),
    ("benchmark", "标竿学习"),
    ("5s", "5S"),
    ("qfd", "QFD"),
    ("quality_report", "品质报告卡"),
    ("six_sigma", "六西格玛管理"),
    ("ebm", "循证医学"),
    ("pdca", "PDCA"),
    ("trm", "TRM"),
    ("process_improve", "流程改造"),
]

experience_improve = [
    ("appointment", "预约诊疗服务更加便捷"),
    ("outpatient_process", "门诊就诊流程更加优化"),
    ("inpatient_experience", "患者住院体验更加舒适"),
    ("post_discharge", "院后医疗服务更加连续"),
    ("pre_in_out", "院前院内衔接更加高效"),
    ("environment", "舒心就医环境更加温馨"),
    ("internet_med", "互联网诊疗更加可及"),
    ("other", "其他（非相关主题）"),
]

quality_topics = [
    ("stemi", "提高急性ST段抬高型心肌梗死再灌注治疗率"),
    ("stroke", "提高急性脑梗死再灌注治疗率"),
    ("tnm", "提高肿瘤治疗前临床TNM分期评估率"),
    ("antibiotic_path", "提高住院患者抗菌药物治疗前病理学送检率"),
    ("surgery_mortality", "降低住院患者围手术期死亡率"),
    ("vte", "提高静脉血栓栓塞症规范预防率"),
    ("sepsis_bundle", "提高感染性休克集束化治疗完成率"),
    ("event_reporting", "提高医疗质量安全不良事件报告率"),
    ("mdt", "提高四级手术术前多学科讨论完成率"),
    ("record_integrity", "提高关键诊疗行为相关记录完整率"),
    ("infusion", "提高住院患者静脉输液规范使用率"),
    ("inspection_sharing", "提高医疗机构检查检验结果互认率"),
]


def ensure_dictionaries(token, dict_type, items):
    existing = api_get(f"/api/dictionaries/{dict_type}", token)
    existing_codes = {item["code"] for item in existing}
    for code, label in items:
        if code in existing_codes:
            continue
        api_post("/api/dictionaries", token, {
            "type": dict_type,
            "code": code,
            "label": label,
            "active": True,
        })


def ensure_institutions(token):
    existing = api_get("/api/institutions", token)
    existing_uscc = {item["uscc"] for item in existing}
    items = []
    for idx, (name, uscc) in enumerate(institutions, start=1):
        if uscc in existing_uscc:
            continue
        items.append({
            "name": name,
            "code": f"INS-{idx:04d}",
            "uscc": uscc,
        })
    if items:
        api_post("/api/institutions/import", token, {"items": items})
    return api_get("/api/institutions", token)


def ensure_competitions(token):
    competitions = api_get("/api/competitions", token)
    names = {c["name"] for c in competitions}
    now = datetime.datetime.now()
    if "2026年省级质量改进赛-1" not in names:
        api_post("/api/competitions", token, {
            "name": "2026年省级质量改进赛-1",
            "registerStart": (now - datetime.timedelta(days=10)).isoformat(),
            "registerEnd": (now + datetime.timedelta(days=10)).isoformat(),
            "bookReviewStart": (now + datetime.timedelta(days=11)).isoformat(),
            "bookReviewEnd": (now + datetime.timedelta(days=20)).isoformat(),
            "interviewStart": (now + datetime.timedelta(days=21)).isoformat(),
            "interviewEnd": (now + datetime.timedelta(days=25)).isoformat(),
            "finalStart": (now + datetime.timedelta(days=26)).isoformat(),
            "finalEnd": (now + datetime.timedelta(days=30)).isoformat(),
        })
    if "2026年省级质量改进赛-2" not in names:
        api_post("/api/competitions", token, {
            "name": "2026年省级质量改进赛-2",
            "registerStart": (now - datetime.timedelta(days=5)).isoformat(),
            "registerEnd": (now + datetime.timedelta(days=20)).isoformat(),
            "bookReviewStart": (now + datetime.timedelta(days=21)).isoformat(),
            "bookReviewEnd": (now + datetime.timedelta(days=30)).isoformat(),
            "interviewStart": (now + datetime.timedelta(days=31)).isoformat(),
            "interviewEnd": (now + datetime.timedelta(days=35)).isoformat(),
            "finalStart": (now + datetime.timedelta(days=36)).isoformat(),
            "finalEnd": (now + datetime.timedelta(days=40)).isoformat(),
        })
    return api_get("/api/competitions", token)


def create_registration(token, competition_id, institution_id, applicant_id, project_name, group_type):
    registration = api_post("/api/registrations", token, {
        "competitionId": competition_id,
        "institutionId": institution_id,
        "applicantId": applicant_id,
        "projectName": project_name,
        "groupType": group_type,
    })
    reg_id = registration["id"]
    api_post(f"/api/registrations/{reg_id}/members", token, {
        "items": [
            {"role": "PARTICIPANT", "name": "成员A", "title": "护士", "department": "护理部"},
            {"role": "PARTICIPANT", "name": "成员B", "title": "医师", "department": "门诊部"},
            {"role": "MENTOR", "name": "辅导员A", "title": "主任", "department": "医务处"},
        ]
    })
    api_post(f"/api/registrations/{reg_id}/activity", token, {
        "theme": f"{project_name}-活动主题",
        "keywords": "质量,改进",
        "subjectTypeCode": subject_types[0][0],
        "methodCode": methods[0][0],
        "experienceImproveCode": experience_improve[0][0],
        "qualityTopicCode": quality_topics[0][0],
        "avgWorkYears": 6,
        "avgAge": 32,
        "crossDepartment": False,
    })
    api_post(f"/api/registrations/{reg_id}/summary", token, {
        "theme": f"{project_name}-摘要主题",
        "plan": "计划内容",
        "problem": "问题结构与对策",
        "action": "对策行动过程",
        "success": "成功表现",
        "discussion": "讨论总结",
    })
    api_post(f"/api/registrations/{reg_id}/submit", token, {})
    return reg_id


def batch_classify(token, registration_ids, group_code):
    if not registration_ids:
        return
    api_post("/api/admin/registrations/batch-classify", token, {
        "registrationIds": registration_ids,
        "groupCode": group_code,
    })


def submit_scores(token, reviewer_id):
    tasks = api_get(f"/api/reviews/tasks?reviewerId={reviewer_id}", token)
    for task in tasks:
        if task["status"] == "SCORED":
            continue
        api_post("/api/reviews/tasks/status", token, {
            "reviewTaskId": task["id"],
            "status": "CONFIRMED",
        })
        api_post("/api/reviews/scores", token, {
            "reviewTaskId": task["id"],
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


def main():
    committee = login("13800000009", "Committee", "COMMITTEE")
    committee_token = committee["token"]

    ensure_dictionaries(committee_token, "subject_type", subject_types)
    ensure_dictionaries(committee_token, "method", methods)
    ensure_dictionaries(committee_token, "experience_improve", experience_improve)
    ensure_dictionaries(committee_token, "quality_topic", quality_topics)

    inst_list = ensure_institutions(committee_token)
    competitions = ensure_competitions(committee_token)
    competition_id = sorted(competitions, key=lambda x: x["id"])[-1]["id"]
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
    )

    reg_ids_by_group = {"BASIC": [], "COMPREHENSIVE": [], "ADVANCED": []}

    for idx, inst in enumerate(inst_list[:20], start=1):
        contestant = login(f"1390000{idx:04d}", f"参赛者{idx}", "CONTESTANT", inst["id"])
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM registrations WHERE applicant_id=%s AND competition_id=%s",
                (contestant["id"], competition_id),
            )
            if cursor.fetchone()[0] > 0:
                continue
        group_type = ["BASIC", "COMPREHENSIVE", "ADVANCED"][idx % 3]
        reg_id = create_registration(contestant["token"], competition_id, inst["id"], contestant["id"],
                                     f"项目-{inst['name']}", group_type)
        api_post(f"/api/registrations/{reg_id}/approve", committee_token, {})
        reg_ids_by_group[group_type].append(reg_id)

    random.shuffle(reg_ids_by_group["BASIC"])
    random.shuffle(reg_ids_by_group["COMPREHENSIVE"])
    random.shuffle(reg_ids_by_group["ADVANCED"])

    batch_classify(committee_token, reg_ids_by_group["BASIC"][::2], "A1")
    batch_classify(committee_token, reg_ids_by_group["BASIC"][1::2], "A2")
    batch_classify(committee_token, reg_ids_by_group["COMPREHENSIVE"][::2], "B1")
    batch_classify(committee_token, reg_ids_by_group["COMPREHENSIVE"][1::2], "B2")
    batch_classify(committee_token, reg_ids_by_group["ADVANCED"][::2], "B1")
    batch_classify(committee_token, reg_ids_by_group["ADVANCED"][1::2], "B2")

    backgrounds = ["MANAGEMENT", "MEDICAL", "NURSING"]
    reviewers = []
    for idx in range(1, 13):
        group = "A1" if idx % 4 == 1 else "A2" if idx % 4 == 2 else "B1" if idx % 4 == 3 else "B2"
        reviewer = login(f"1370000{idx:04d}", f"评审{idx}", "REVIEWER", None, group, group, backgrounds[idx % 3])
        reviewers.append(reviewer)

    api_post("/api/admin/reviews/auto-assign", committee_token, {
        "competitionId": competition_id,
        "stage": "BOOK",
        "reviewersPerRegistration": 2,
    })

    for reviewer in reviewers:
        submit_scores(reviewer["token"], reviewer["id"])

    api_post("/api/admin/reviews/auto-assign", committee_token, {
        "competitionId": competition_id,
        "stage": "INTERVIEW",
        "reviewersPerRegistration": 1,
    })

    for reviewer in reviewers:
        submit_scores(reviewer["token"], reviewer["id"])

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM institutions")
        inst_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registrations")
        reg_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM review_tasks")
        task_count = cursor.fetchone()[0]
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s", (DB_NAME,))
        tables = [row[0] for row in cursor.fetchall()]
        for suffix in ["-2", "-3"]:
            db_name = DB_NAME + suffix
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{db_name}`.`{table}`")
                cursor.execute(f"CREATE TABLE `{db_name}`.`{table}` LIKE `{DB_NAME}`.`{table}`")
    conn.close()
    print(json.dumps({
        "institutions": inst_count,
        "registrations": reg_count,
        "reviewTasks": task_count,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
