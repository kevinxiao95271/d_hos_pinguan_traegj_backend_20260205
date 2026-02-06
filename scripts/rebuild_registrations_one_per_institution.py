import os
import random
import datetime
import pymysql


DB_HOST = os.getenv("PINGUAN_DB_HOST")
DB_PORT = int(os.getenv("PINGUAN_DB_PORT", "0") or 0)
DB_USER = os.getenv("PINGUAN_DB_USER")
DB_PASSWORD = os.getenv("PINGUAN_DB_PASSWORD")
DB_NAME = os.getenv("PINGUAN_DB_NAME")


def main():
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
        raise RuntimeError("missing env: PINGUAN_DB_HOST/PORT/USER/PASSWORD/NAME")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
    )
    cur = conn.cursor()
    competition_id = 21

    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    cur.execute("SELECT id FROM registrations WHERE competition_id=%s", (competition_id,))
    reg_ids = [r[0] for r in cur.fetchall()]
    if reg_ids:
        fmt = ",".join(["%s"] * len(reg_ids))
        cur.execute(f"DELETE FROM review_scores WHERE review_task_id IN (SELECT id FROM review_tasks WHERE registration_id IN ({fmt}))", reg_ids)
        cur.execute(f"DELETE FROM review_tasks WHERE registration_id IN ({fmt})", reg_ids)
        cur.execute(f"DELETE FROM registration_members WHERE registration_id IN ({fmt})", reg_ids)
        cur.execute(f"DELETE FROM activity_infos WHERE registration_id IN ({fmt})", reg_ids)
        cur.execute(f"DELETE FROM project_summaries WHERE registration_id IN ({fmt})", reg_ids)
        cur.execute(f"DELETE FROM material_files WHERE registration_id IN ({fmt})", reg_ids)
        cur.execute(f"DELETE FROM registrations WHERE id IN ({fmt})", reg_ids)
    cur.execute("DELETE FROM user_accounts WHERE role='CONTESTANT'")
    conn.commit()

    cur.execute("SELECT id FROM institutions ORDER BY id")
    institution_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT code FROM dictionary_items WHERE type='subject_type' AND active=1")
    subject_codes = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT code FROM dictionary_items WHERE type='method' AND active=1")
    method_codes = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT code FROM dictionary_items WHERE type='experience_improve' AND active=1")
    experience_codes = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT code FROM dictionary_items WHERE type='quality_topic' AND active=1")
    quality_codes = [r[0] for r in cur.fetchall()]

    project_names = [
        "减少等待时间改善项目",
        "门急诊流程优化",
        "住院服务效率提升",
        "静脉输液安全改进",
        "护理质量提升行动",
        "手术室周转优化",
        "患者满意度提升",
        "抗菌药物规范化",
        "病案质量提升",
        "检验报告时效提升",
        "病区巡查标准化",
        "信息系统提效",
        "急诊分诊优化",
        "康复流程改进",
        "医技检查协调优化",
        "医保结算效率提升",
        "门诊预约体验提升",
        "住院用药安全改进",
        "手卫生依从性提升",
        "疼痛管理规范化",
        "影像检查流程优化",
        "药学服务质量提升",
        "护理交接班规范化",
        "医疗耗材精细化管理",
    ]
    random.shuffle(project_names)
    now = datetime.datetime.now()

    for idx, inst_id in enumerate(institution_ids, start=1):
        phone = f"13966{idx:06d}"
        name = f"参赛者{idx}"
        cur.execute(
            "INSERT INTO user_accounts (phone,name,title,role,institution_id,reviewer_group_code,interview_group_code,expert_background,created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (phone, name, "", "CONTESTANT", inst_id, None, None, None, now),
        )
        applicant_id = cur.lastrowid
        project_name = f"{project_names[(idx - 1) % len(project_names)]}-{idx}"
        group_type = ["BASIC", "COMPREHENSIVE", "ADVANCED"][(idx - 1) % 3]
        group_code = ["A1", "A2", "B1", "B2"][(idx - 1) % 4]
        submitted_at = now - datetime.timedelta(hours=(len(institution_ids) - idx))
        cur.execute(
            "INSERT INTO registrations (competition_id,institution_id,applicant_id,project_name,group_type,status,submitted_at,created_at,group_code) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (competition_id, inst_id, applicant_id, project_name, group_type, "APPROVED", submitted_at, now, group_code),
        )
        reg_id = cur.lastrowid
        cur.execute(
            "INSERT INTO activity_infos (registration_id,theme,keywords,subject_type_code,method_code,experience_improve_code,quality_topic_code,avg_work_years,avg_age,cross_department) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                reg_id,
                f"项目主题{reg_id}",
                "质量,改进",
                random.choice(subject_codes) if subject_codes else "patient_care",
                random.choice(method_codes) if method_codes else "qc_problem",
                random.choice(experience_codes) if experience_codes else "appointment",
                random.choice(quality_codes) if quality_codes else "stemi",
                5 + idx % 6,
                28 + idx % 10,
                1 if idx % 2 == 0 else 0,
            ),
        )

    conn.commit()
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.close()
    print("ok")


if __name__ == "__main__":
    main()
