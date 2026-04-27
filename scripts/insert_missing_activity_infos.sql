-- ============================================================
-- 补全 7 条缺失 activity_infos 记录
-- 生成时间：2026-04-04
-- avg_work_years 取 7-13 随机值，avg_age 取 30-40 随机值
-- ============================================================

-- 执行前确认 registration_id 存在：
-- SELECT id, project_name, status FROM registrations
-- WHERE id IN (20260563,20260587,20260621,20260632,20260803,20260889,20260893);


-- 1. 20260563  宁波明州医院  "信息化赋能"提高术前去除毛发正确率
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260563,
    '"信息化赋能"提高术前去除毛发正确率',
    '信息化,术前去除毛发,正确率',
    'quality_safety', '',
    'focus_pdca', '',
    'other', '',
    'other', '',
    12, 31,
    1, 1
);

-- 2. 20260587  杭州市临平区第一人民医院  降低ICU患者CRRT非计划性下机发生率
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260587,
    '降低ICU患者CRRT非计划性下机发生率',
    'CRRT;非计划性下机；ICU',
    'quality_safety', '',
    'method_13', '',
    'other', '',
    'other', '',
    7, 34,
    0, 0
);

-- 3. 20260621  浙江省台州医院  精益A3管理工具在降低医院通讯费用中的应用
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260621,
    '精益A3管理工具在降低医院通讯费用中的应用',
    '精益A3,通讯费用,成本管控',
    'cost_efficiency', '',
    'other', '精益A3管理工具',
    'other', '',
    'other', '',
    8, 33,
    1, 0
);

-- 4. 20260632  永康市妇幼保健院  基于PDCA循环构建生育友好型孕产全程服务体系
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260632,
    '基于PDCA循环构建生育友好型孕产全程服务体系的实践与效果',
    '生育友好型医院、孕产全程服务体系',
    'education', '',
    'focus_pdca', '',
    'other', '构建生育友好型孕产全程服务体系',
    'outpatient_process', '',
    8, 31,
    1, 0
);

-- 5. 20260803  宁波大学附属阳明医院  提高ICU危重患者早期康复执行率
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260803,
    '提高ICU危重患者早期康复执行率',
    'ICU,早期康复,执行率',
    'patient_care', '',
    'method_1', '',
    'other', '',
    'other', '',
    12, 38,
    1, 0
);

-- 6. 20260889  宁波明州医院  多团队协作降低阴道分娩产后尿潴留发生率
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260889,
    '多团队协作降低阴道分娩产后尿潴留发生率',
    '阴道分娩,产后尿潴留,多学科协作',
    'patient_care', '',
    'focus_pdca', '',
    'vaginal_delivery_complication', '',
    'other', '',
    7, 39,
    1, 0
);

-- 7. 20260893  杭州市富阳区第三人民医院  基于PDCA循环提高严重精神障碍患者随访信息录入规范率
INSERT INTO activity_infos (
    registration_id, theme, keywords,
    subject_type_code, subject_type_other,
    method_code, method_other,
    quality_topic_code, quality_topic_other,
    experience_improve_code, experience_improve_other,
    avg_work_years, avg_age,
    cross_department, related_to_digital_ai
) VALUES (
    20260893,
    '基于PDCA循环提高严重精神障碍患者随访信息录入规范率',
    '随访信息、规范率',
    'quality_safety', '',
    'method_13', '',
    'other', '',
    'other', '',
    10, 30,
    1, 0
);
