-- ================================================================================
-- 舟山医院参赛数据导入SQL脚本
-- 1. 更新机构名称
-- 2. 创建7个参赛者账号
-- 3. 创建7个报名项目及完整信息
-- ================================================================================

USE pinguan_db;

-- ================================================================================
-- 1. 更新机构名称
-- ================================================================================
UPDATE institutions 
SET name = '舟山医院'
WHERE id = 17;

-- ================================================================================
-- 2. 创建7个参赛者账号
-- ================================================================================

-- 参赛者1: 陈蔚莉
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000001', '陈蔚莉', '护理部主任', 'CONTESTANT', 17, NOW());

-- 参赛者2: 汪君燕
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000002', '汪君燕', '急诊科主任', 'CONTESTANT', 17, NOW());

-- 参赛者3: 刘一宁
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000003', '刘一宁', '静脉治疗专科护士', 'CONTESTANT', 17, NOW());

-- 参赛者4: 杨芳
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000004', '杨芳', 'ICU护士长', 'CONTESTANT', 17, NOW());

-- 参赛者5: 张依妮
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000005', '张依妮', '呼吸治疗师', 'CONTESTANT', 17, NOW());

-- 参赛者6: 夏舟备
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000006', '夏舟备', '输血科主任', 'CONTESTANT', 17, NOW());

-- 参赛者7: 李利群
INSERT INTO user_accounts (phone, name, title, role, institution_id, created_at)
VALUES ('19925000007', '李利群', '康复科主任', 'CONTESTANT', 17, NOW());

-- ================================================================================
-- 3. 创建7个报名项目
-- ================================================================================

-- 项目1: 陈蔚莉 - 基于信息交互的适老化院内转运实践系统
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000001'), 
        '基于信息交互的适老化院内转运实践系统的构建与应用', 'ADVANCED', 'A1', 'APPROVED', NOW(), NOW());

-- 项目2: 汪君燕 - 提高严重创伤患者送急诊手术60min达标率
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000002'), 
        '提高严重创伤患者送急诊手术60min达标率', 'COMPREHENSIVE', 'B21', 'APPROVED', NOW(), NOW());

-- 项目3: 刘一宁 - 提高住院患者静脉输液规范使用率
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000003'), 
        '提高住院患者静脉输液规范使用率', 'COMPREHENSIVE', 'B2', 'APPROVED', NOW(), NOW());

-- 项目4: 杨芳 - 提高全院感染性休克集束化治疗完成率
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000004'), 
        '提高全院感染性休克集束化治疗完成率', 'COMPREHENSIVE', 'B2', 'APPROVED', NOW(), NOW());

-- 项目5: 张依妮 - 基于多学科的全病程呼吸治疗管理体系
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000005'), 
        '基于多学科的全病程呼吸治疗管理体系的构建与应用', 'ADVANCED', 'A1', 'APPROVED', NOW(), NOW());

-- 项目6: 夏舟备 - 提高手术患者自体输血率
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000006'), 
        '提高手术患者自体输血率', 'COMPREHENSIVE', 'B6', 'APPROVED', NOW(), NOW());

-- 项目7: 李利群 - 基于海岛特色的AECOPD患者早期肺康复模式构建
INSERT INTO registrations (competition_id, institution_id, applicant_id, project_name, group_type, group_code, status, submitted_at, created_at)
VALUES (21, 17, (SELECT id FROM user_accounts WHERE phone = '19925000007'), 
        '基于海岛特色的AECOPD患者早期肺康复模式构建', 'COMPREHENSIVE', 'B14', 'APPROVED', NOW(), NOW());

-- ================================================================================
-- 4. 添加活动信息 (activity_infos)
-- ================================================================================

-- 项目1活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '适老化院内转运实践系统', '信息交互,适老化,院内转运', 'system_construct', 'subject_type_8', 'quality_topic_5', 'experience_1', 35, 10, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000001';

-- 项目2活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '严重创伤患者快速救治', '创伤,急诊手术,达标率', 'qcc', 'subject_type_1', 'quality_topic_1', 'experience_1', 32, 8, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000002';

-- 项目3活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '静脉输液规范化管理', '静脉输液,规范使用,用药安全', 'qcc', 'subject_type_2', 'quality_topic_2', 'experience_2', 30, 7, 0
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000003';

-- 项目4活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '感染性休克集束化治疗', '感染性休克,集束化,治疗完成率', 'qcc', 'subject_type_1', 'quality_topic_1', 'experience_1', 33, 9, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000004';

-- 项目5活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '全病程呼吸治疗管理', '呼吸治疗,多学科,全病程管理', 'system_construct', 'subject_type_1', 'quality_topic_5', 'experience_1', 31, 8, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000005';

-- 项目6活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, '推广自体输血技术', '自体输血,手术患者,血液安全', 'qcc', 'subject_type_4', 'quality_topic_3', 'experience_1', 34, 10, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000006';

-- 项目7活动信息
INSERT INTO activity_infos (registration_id, theme, keywords, method_code, subject_type_code, quality_topic_code, experience_improve_code, avg_age, avg_work_years, cross_department)
SELECT r.id, 'AECOPD早期肺康复', 'AECOPD,肺康复,海岛特色', 'system_construct', 'subject_type_1', 'quality_topic_5', 'experience_3', 36, 11, 1
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000007';

-- ================================================================================
-- 5. 添加项目总结 (project_summaries)
-- ================================================================================

-- 项目1总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '构建适老化院内转运系统',
       '老年患者院内转运存在安全隐患和效率问题',
       '设计基于信息交互的智能转运系统，包括实时定位、智能调度等功能',
       '开发系统平台，培训人员，试点运行，逐步推广',
       '转运效率提升30%，老年患者满意度提高至95%',
       '系统化管理显著提升了转运安全性和效率'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000001';

-- 项目2总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '优化创伤患者救治流程',
       '严重创伤患者从急诊到手术时间过长，影响救治效果',
       '建立绿色通道，优化流程，加强团队协作',
       '成立创伤救治小组，制定标准流程，开展培训演练',
       '60分钟达标率从65%提升至92%',
       '多学科协作和流程优化是关键'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000002';

-- 项目3总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '规范静脉输液使用',
       '静脉输液使用不规范，存在安全隐患',
       '制定规范标准，加强培训，实施监督检查',
       '建立评估体系，开展全员培训，定期考核',
       '规范使用率从78%提升至96%',
       '标准化和持续培训显著提升了用药安全'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000003';

-- 项目4总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '推广感染性休克集束化治疗',
       '集束化治疗执行不到位，完成率低',
       '制定标准流程，加强培训，建立监测系统',
       '成立质控小组，开展全员培训，实施实时监控',
       '集束化治疗完成率从68%提升至90%',
       '标准化流程和实时监控是提高完成率的关键'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000004';

-- 项目5总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '构建呼吸治疗管理体系',
       '呼吸治疗缺乏系统化管理，各科室协作不足',
       '建立多学科协作机制，制定全病程管理流程',
       '组建MDT团队，设计管理流程，开展培训，试点推广',
       '呼吸治疗有效率提升25%，住院天数缩短2.5天',
       '多学科协作显著提升了呼吸治疗效果'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000005';

-- 项目6总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '提升自体输血应用率',
       '自体输血技术应用率低，异体输血风险高',
       '加强宣教，完善流程，提升技术能力',
       '培训医护人员，改进设备，建立标准流程',
       '自体输血率从15%提升至42%',
       '自体输血显著降低了异体输血相关风险'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000006';

-- 项目7总结
INSERT INTO project_summaries (registration_id, theme, problem, plan, action, success, discussion)
SELECT r.id, '构建海岛特色肺康复模式',
       'AECOPD患者缺乏早期康复，复发率高',
       '结合海岛环境特点，建立早期康复模式',
       '设计康复方案，培训人员，建立随访机制',
       '再入院率下降35%，患者生活质量显著提升',
       '早期康复干预对AECOPD患者预后改善明显'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000007';

-- ================================================================================
-- 6. 添加团队成员 (registration_members)
-- ================================================================================

-- 项目1团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '陈蔚莉', '护理部主任', '护理部'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000001';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '李明', '主管护师', '信息科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000001';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '王芳', '护师', '外科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000001';

-- 项目2团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '汪君燕', '急诊科主任', '急诊科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000002';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '张强', '主治医师', '急诊科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000002';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '刘洋', '护师', '手术室'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000002';

-- 项目3团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '刘一宁', '静脉治疗专科护士', '护理部'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000003';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '赵敏', '主管护师', '内科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000003';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '孙丽', '护师', '外科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000003';

-- 项目4团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '杨芳', 'ICU护士长', 'ICU'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000004';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '周杰', '主治医师', 'ICU'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000004';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '吴静', '护师', 'ICU'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000004';

-- 项目5团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '张依妮', '呼吸治疗师', '呼吸科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000005';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '陈涛', '主治医师', '呼吸科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000005';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '林美', '护师', 'ICU'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000005';

-- 项目6团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '夏舟备', '输血科主任', '输血科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000006';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '郑华', '主治医师', '麻醉科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000006';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '黄丽', '技师', '输血科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000006';

-- 项目7团队成员
INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'MENTOR', '李利群', '康复科主任', '康复科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000007';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '徐刚', '主治医师', '呼吸科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000007';

INSERT INTO registration_members (registration_id, role, name, title, department)
SELECT r.id, 'PARTICIPANT', '朱红', '康复治疗师', '康复科'
FROM registrations r 
INNER JOIN user_accounts u ON r.applicant_id = u.id
WHERE u.phone = '19925000007';

-- ================================================================================
-- 验证导入结果
-- ================================================================================

SELECT '========== 导入完成统计 ==========' AS '';

SELECT '机构更新:' AS '', COUNT(*) AS count FROM institutions WHERE name = '舟山医院';
SELECT '用户创建:' AS '', COUNT(*) AS count FROM user_accounts WHERE phone LIKE '19925%';
SELECT '项目创建:' AS '', COUNT(*) AS count FROM registrations WHERE institution_id = 17 AND applicant_id IN (SELECT id FROM user_accounts WHERE phone LIKE '19925%');
SELECT '活动信息:' AS '', COUNT(*) AS count FROM activity_infos WHERE registration_id IN (SELECT r.id FROM registrations r INNER JOIN user_accounts u ON r.applicant_id = u.id WHERE u.phone LIKE '19925%');
SELECT '项目总结:' AS '', COUNT(*) AS count FROM project_summaries WHERE registration_id IN (SELECT r.id FROM registrations r INNER JOIN user_accounts u ON r.applicant_id = u.id WHERE u.phone LIKE '19925%');
SELECT '团队成员:' AS '', COUNT(*) AS count FROM registration_members WHERE registration_id IN (SELECT r.id FROM registrations r INNER JOIN user_accounts u ON r.applicant_id = u.id WHERE u.phone LIKE '19925%');

-- 显示参赛者登录信息
SELECT '========== 参赛者登录信息 ==========' AS '';
SELECT 
    u.name AS 姓名,
    u.phone AS 手机号,
    u.title AS 职称,
    r.project_name AS 项目名称,
    r.group_type AS 组别,
    r.group_code AS 分组
FROM user_accounts u
INNER JOIN registrations r ON r.applicant_id = u.id
WHERE u.phone LIKE '19925%'
ORDER BY u.id;
