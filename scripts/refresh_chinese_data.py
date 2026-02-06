import os
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
    cur.execute("UPDATE competitions SET name=%s WHERE id=21", ("2026浙江品管大赛",))
    cur.execute("SELECT id FROM institutions ORDER BY id")
    inst_ids = [row[0] for row in cur.fetchall()]
    inst_names = [
        "浙江大学医学院附属第一医院",
        "浙江大学医学院附属第二医院",
        "浙江省人民医院",
        "浙江省中医院",
        "杭州市第一人民医院",
        "杭州市中医院",
        "宁波市第一医院",
        "宁波市第二医院",
        "温州市人民医院",
        "温州市中医院",
        "嘉兴市第一医院",
        "嘉兴市第二医院",
        "湖州市中心医院",
        "绍兴市人民医院",
        "金华市中心医院",
        "衢州市人民医院",
        "舟山市人民医院",
        "台州市中心医院",
        "丽水市人民医院",
        "湖州市中医院",
        "绍兴市中医院",
        "金华市中医院",
        "衢州市中医院",
        "舟山市中医院",
        "台州市中医院",
        "丽水市中医院",
        "杭州师范大学附属医院",
        "浙江省肿瘤医院",
        "浙江省妇幼保健院",
        "浙江省立同德医院",
        "浙江省立同德医院下沙院区",
        "宁波大学附属医院",
        "浙江大学医学院附属邵逸夫医院",
    ]
    while len(inst_names) < len(inst_ids):
        inst_names.append(f"浙江省综合医院{len(inst_names) + 1}")
    for inst_id, name in zip(inst_ids, inst_names):
        cur.execute("UPDATE institutions SET name=%s WHERE id=%s", (name, inst_id))

    cur.execute("SELECT id, applicant_id FROM registrations WHERE competition_id=21 ORDER BY id")
    reg_rows = cur.fetchall()
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
    for index, (reg_id, applicant_id) in enumerate(reg_rows):
        project_name = f"{project_names[index % len(project_names)]}-{index + 1}"
        cur.execute("UPDATE registrations SET project_name=%s WHERE id=%s", (project_name, reg_id))
        cur.execute("UPDATE user_accounts SET name=%s WHERE id=%s", (f"参赛者{index + 1}", applicant_id))

    conn.commit()
    conn.close()
    print("ok")


if __name__ == "__main__":
    main()
