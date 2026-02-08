-- 插入字典数据：改善就医环境和医疗质量安全相关主题
-- 执行前请确认数据库连接

USE pinguan_competition_23;

-- ============================================
-- 1. 改善就医环境选项 (experience_improve)
-- ============================================

INSERT INTO dictionary_items (type, code, label, active, sort_order) VALUES
('experience_improve', 'appointment_service', '预约诊疗服务更加便捷', TRUE, 1),
('experience_improve', 'outpatient_process', '门诊就诊更加优化', TRUE, 2),
('experience_improve', 'inpatient_experience', '患者住院体验更加舒适', TRUE, 3),
('experience_improve', 'post_hospital_service', '院后医疗服务更加连续', TRUE, 4),
('experience_improve', 'pre_inpatient_connection', '院前院内衔接更加高效', TRUE, 5),
('experience_improve', 'comfortable_environment', '舒心就医环境更加温馨', TRUE, 6),
('experience_improve', 'internet_diagnosis', '互联网诊疗更加便捷', TRUE, 7),
('experience_improve', 'other', '其他', TRUE, 8);

-- ============================================
-- 2. 医疗质量安全相关主题 (quality_topic)
-- ============================================

INSERT INTO dictionary_items (type, code, label, active, sort_order) VALUES
('quality_topic', 'stemi_reperfusion', '提高急性ST段抬高型心肌梗死再灌注治疗率', TRUE, 1),
('quality_topic', 'stroke_reperfusion', '提高急性脑梗死再灌注治疗率', TRUE, 2),
('quality_topic', 'tumor_tnm_staging', '提高肿瘤治疗前临床TNM分期评估率', TRUE, 3),
('quality_topic', 'antibiotic_pathogen_test', '提高住院患者抗菌药物治疗前病原学送检率', TRUE, 4),
('quality_topic', 'perioperative_mortality', '降低住院患者围手术期死亡率', TRUE, 5),
('quality_topic', 'vte_prevention', '提高静脉血栓栓塞症规范预防率', TRUE, 6),
('quality_topic', 'septic_shock_bundle', '提高感染性休克集束化治疗完成率', TRUE, 7),
('quality_topic', 'adverse_event_report', '提高医疗质量安全不良事件报告率', TRUE, 8),
('quality_topic', 'iv_infusion_standard', '降低住院患者静脉输液规范使用率', TRUE, 9),
('quality_topic', 'level4_surgery_mdt', '提高四级手术术前多学科讨论完成率', TRUE, 10),
('quality_topic', 'vaginal_delivery_complication', '降低阴道分娩并发症发生率', TRUE, 11),
('quality_topic', 'unplanned_reoperation', '降低非计划重返手术室再手术率', TRUE, 12),
('quality_topic', 'key_diagnosis_record', '提高关键诊疗行为相关记录完整率', TRUE, 13),
('quality_topic', 'other', '其他', TRUE, 14);

-- ============================================
-- 验证插入结果
-- ============================================

-- 查看改善就医环境选项
SELECT * FROM dictionary_items WHERE type = 'experience_improve' ORDER BY sort_order;

-- 查看医疗质量安全相关主题选项
SELECT * FROM dictionary_items WHERE type = 'quality_topic' ORDER BY sort_order;

-- 统计
SELECT type, COUNT(*) as count FROM dictionary_items WHERE type IN ('experience_improve', 'quality_topic') GROUP BY type;
