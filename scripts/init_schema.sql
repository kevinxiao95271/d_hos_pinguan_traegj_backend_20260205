-- ================================================================
-- 品管大赛系统 - 最终建表 DDL + 初始数据
-- 数据库名称请按实际环境替换 YOUR_DATABASE_NAME
-- ================================================================

CREATE DATABASE IF NOT EXISTS `YOUR_DATABASE_NAME`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `YOUR_DATABASE_NAME`;

-- ----------------------------------------------------------------
-- 1. competitions 赛事
-- ----------------------------------------------------------------
CREATE TABLE `competitions` (
  `id`                BIGINT       NOT NULL AUTO_INCREMENT,
  `name`              VARCHAR(120) NOT NULL,
  `stage`             VARCHAR(32)  NOT NULL COMMENT 'REGISTER|BOOK_REVIEW|INTERVIEW|FINAL',
  `register_start`    DATETIME(6),
  `register_end`      DATETIME(6),
  `book_review_start` DATETIME(6),
  `book_review_end`   DATETIME(6),
  `interview_start`   DATETIME(6),
  `interview_end`     DATETIME(6),
  `final_start`       DATETIME(6),
  `final_end`         DATETIME(6),
  `created_at`        DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 2. institutions 参赛/评审机构
-- ----------------------------------------------------------------
CREATE TABLE `institutions` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT,
  `name`       VARCHAR(200) NOT NULL,
  `code`       VARCHAR(64)  NOT NULL,
  `uscc`       VARCHAR(32)  NOT NULL,
  `region`     VARCHAR(64),
  `city`       VARCHAR(50),
  `level`      VARCHAR(32),
  `is_ext`     TINYINT      NOT NULL DEFAULT 0 COMMENT '0-医院 1-外部机构',
  `created_at` DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  UNIQUE KEY `uk_uscc` (`uscc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 3. user_accounts 用户账号
-- ----------------------------------------------------------------
CREATE TABLE `user_accounts` (
  `id`                   BIGINT       NOT NULL AUTO_INCREMENT,
  `phone`                VARCHAR(32)  NOT NULL,
  `password`             VARCHAR(128),
  `name`                 VARCHAR(64)  NOT NULL,
  `title`                VARCHAR(64),
  `role`                 VARCHAR(32)  NOT NULL COMMENT 'CONTESTANT|REVIEWER|COMMITTEE|COMMITTEE_ADMIN|OPS',
  `institution_id`       BIGINT,
  `reviewer_group_code`  VARCHAR(32),
  `interview_group_code` VARCHAR(32),
  `expert_background`    VARCHAR(32),
  `enabled`              TINYINT      NOT NULL DEFAULT 1,
  `created_at`           DATETIME(6)  NOT NULL,
  `last_login_at`        DATETIME(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_institution_id` (`institution_id`),
  KEY `idx_role` (`role`),
  KEY `idx_enabled` (`enabled`),
  CONSTRAINT `fk_user_institution` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 4. registrations 参赛报名
-- ----------------------------------------------------------------
CREATE TABLE `registrations` (
  `id`             BIGINT       NOT NULL AUTO_INCREMENT,
  `competition_id` BIGINT,
  `institution_id` BIGINT,
  `applicant_id`   BIGINT,
  `project_name`   VARCHAR(120) NOT NULL,
  `group_type`     VARCHAR(32)  NOT NULL COMMENT 'BASIC|COMPREHENSIVE|ADVANCED',
  `group_code`     VARCHAR(64),
  `status`         VARCHAR(32)  NOT NULL COMMENT 'DRAFT|SUBMITTED|RETURNED|APPROVED',
  `submitted_at`   DATETIME(6),
  `created_at`     DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_competition_id` (`competition_id`),
  KEY `idx_institution_id` (`institution_id`),
  KEY `idx_applicant_id` (`applicant_id`),
  KEY `idx_status` (`status`),
  KEY `idx_group_code` (`group_code`),
  CONSTRAINT `fk_reg_competition` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`),
  CONSTRAINT `fk_reg_institution` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`),
  CONSTRAINT `fk_reg_applicant`   FOREIGN KEY (`applicant_id`)   REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 5. registration_members 报名团队成员
-- ----------------------------------------------------------------
CREATE TABLE `registration_members` (
  `id`              BIGINT      NOT NULL AUTO_INCREMENT,
  `registration_id` BIGINT      NOT NULL,
  `role`            VARCHAR(32) NOT NULL COMMENT 'PARTICIPANT|MENTOR',
  `name`            VARCHAR(64) NOT NULL,
  `title`           VARCHAR(64) NOT NULL,
  `department`      VARCHAR(64),
  PRIMARY KEY (`id`),
  KEY `idx_registration_id` (`registration_id`),
  CONSTRAINT `fk_member_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 6. activity_infos 活动信息
-- ----------------------------------------------------------------
CREATE TABLE `activity_infos` (
  `id`                        BIGINT       NOT NULL AUTO_INCREMENT,
  `registration_id`           BIGINT       NOT NULL,
  `theme`                     VARCHAR(120) NOT NULL,
  `keywords`                  VARCHAR(120) NOT NULL,
  `subject_type_code`         VARCHAR(64)  NOT NULL,
  `subject_type_other`        VARCHAR(200),
  `method_code`               VARCHAR(64)  NOT NULL,
  `method_other`              VARCHAR(200),
  `experience_improve_code`   VARCHAR(64)  NOT NULL,
  `experience_improve_other`  VARCHAR(200),
  `quality_topic_code`        VARCHAR(64)  NOT NULL,
  `quality_topic_other`       VARCHAR(200),
  `avg_work_years`            INT          NOT NULL,
  `avg_age`                   INT          NOT NULL,
  `cross_department`          TINYINT      NOT NULL,
  `related_to_digital_ai`     TINYINT      NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_registration_id` (`registration_id`),
  CONSTRAINT `fk_activity_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 7. project_summaries 项目摘要
-- ----------------------------------------------------------------
CREATE TABLE `project_summaries` (
  `id`              BIGINT        NOT NULL AUTO_INCREMENT,
  `registration_id` BIGINT        NOT NULL,
  `theme`           VARCHAR(200)  NOT NULL,
  `plan`            VARCHAR(1000) NOT NULL,
  `problem`         VARCHAR(1000) NOT NULL,
  `action`          VARCHAR(1000) NOT NULL,
  `success`         VARCHAR(1000) NOT NULL,
  `discussion`      VARCHAR(1000) NOT NULL,
  `operation`       VARCHAR(1000),
  `presentation`    VARCHAR(1000),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_registration_id` (`registration_id`),
  CONSTRAINT `fk_summary_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 8. material_files 上传材料文件
-- ----------------------------------------------------------------
CREATE TABLE `material_files` (
  `id`              BIGINT       NOT NULL AUTO_INCREMENT,
  `registration_id` BIGINT       NOT NULL,
  `type`            VARCHAR(64)  NOT NULL,
  `file_name`       VARCHAR(200) NOT NULL,
  `file_url`        VARCHAR(300) NOT NULL,
  `uploaded_at`     DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_registration_type` (`registration_id`, `type`),
  CONSTRAINT `fk_material_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 9. review_tasks 评审任务
-- ----------------------------------------------------------------
CREATE TABLE `review_tasks` (
  `id`              BIGINT      NOT NULL AUTO_INCREMENT,
  `stage`           VARCHAR(32) NOT NULL COMMENT 'BOOK|INTERVIEW|FINAL',
  `registration_id` BIGINT,
  `reviewer_id`     BIGINT,
  `status`          VARCHAR(32) NOT NULL COMMENT 'PENDING|CONFIRMED|SCORED|RETURNED',
  `created_at`      DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_stage` (`stage`),
  KEY `idx_registration_id` (`registration_id`),
  KEY `idx_reviewer_id` (`reviewer_id`),
  CONSTRAINT `fk_task_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`),
  CONSTRAINT `fk_task_reviewer`     FOREIGN KEY (`reviewer_id`)     REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 10. review_scores 评审打分
-- ----------------------------------------------------------------
CREATE TABLE `review_scores` (
  `id`             BIGINT        NOT NULL AUTO_INCREMENT,
  `review_task_id` BIGINT        NOT NULL,
  `plan`           DECIMAL(4,1)  NOT NULL,
  `problem`        DECIMAL(4,1)  NOT NULL,
  `action`         DECIMAL(4,1)  NOT NULL,
  `success`        DECIMAL(4,1)  NOT NULL,
  `review`         DECIMAL(4,1)  NOT NULL,
  `operation`      DECIMAL(4,1)  NOT NULL,
  `presentation`   DECIMAL(4,1)  NOT NULL,
  `total`          DECIMAL(5,1)  NOT NULL,
  `highlight`      VARCHAR(500)  NOT NULL,
  `weakness`       VARCHAR(500)  NOT NULL,
  `submitted_at`   DATETIME(6)   NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_review_task_id` (`review_task_id`),
  CONSTRAINT `fk_score_task` FOREIGN KEY (`review_task_id`) REFERENCES `review_tasks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 11. institution_update_requests 机构信息修改申请
-- ----------------------------------------------------------------
CREATE TABLE `institution_update_requests` (
  `id`             BIGINT       NOT NULL AUTO_INCREMENT,
  `institution_id` BIGINT,
  `submitter_id`   BIGINT,
  `new_name`       VARCHAR(200),
  `new_code`       VARCHAR(64),
  `new_uscc`       VARCHAR(32),
  `status`         VARCHAR(32)  NOT NULL COMMENT 'PENDING|APPROVED|REJECTED',
  `created_at`     DATETIME(6)  NOT NULL,
  `reviewed_at`    DATETIME(6),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_req_institution` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`),
  CONSTRAINT `fk_req_submitter`   FOREIGN KEY (`submitter_id`)   REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 12. dictionary_items 字典项
-- ----------------------------------------------------------------
CREATE TABLE `dictionary_items` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT,
  `type`       VARCHAR(64)  NOT NULL,
  `code`       VARCHAR(64)  NOT NULL,
  `label`      VARCHAR(128) NOT NULL,
  `active`     TINYINT      NOT NULL DEFAULT 1,
  `sort_order` INT          NOT NULL DEFAULT 0,
  `created_at` DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 13. system_settings 系统配置
-- ----------------------------------------------------------------
CREATE TABLE `system_settings` (
  `id`            BIGINT       NOT NULL AUTO_INCREMENT,
  `setting_key`   VARCHAR(64)  NOT NULL,
  `setting_value` VARCHAR(300) NOT NULL,
  `updated_at`    DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_setting_key` (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 14. activity_templates 通用活动模板文件
-- ----------------------------------------------------------------
CREATE TABLE `activity_templates` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT,
  `type`        VARCHAR(64)  NOT NULL,
  `file_name`   VARCHAR(200) NOT NULL,
  `file_url`    VARCHAR(300) NOT NULL,
  `uploaded_at` DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 15. competition_templates 赛事绑定模板文件
-- ----------------------------------------------------------------
CREATE TABLE `competition_templates` (
  `id`             BIGINT       NOT NULL AUTO_INCREMENT,
  `competition_id` BIGINT,
  `type`           VARCHAR(64)  NOT NULL,
  `file_name`      VARCHAR(200) NOT NULL,
  `file_url`       VARCHAR(300) NOT NULL,
  `uploaded_at`    DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_competition_id` (`competition_id`),
  CONSTRAINT `fk_comp_template_competition` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 16. system_template_files 系统模板文件（版本管理）
-- ----------------------------------------------------------------
CREATE TABLE `system_template_files` (
  `id`                 BIGINT       NOT NULL AUTO_INCREMENT,
  `template_type`      VARCHAR(64)  NOT NULL COMMENT 'registration_form|result_report',
  `file_name`          VARCHAR(200) NOT NULL,
  `minio_object_name`  VARCHAR(300) NOT NULL,
  `file_size`          BIGINT       NOT NULL,
  `version`            INT          NOT NULL DEFAULT 1,
  `is_active`          TINYINT      NOT NULL DEFAULT 1,
  `uploaded_by`        BIGINT,
  `uploaded_at`        DATETIME(6)  NOT NULL,
  `description`        VARCHAR(500),
  PRIMARY KEY (`id`),
  KEY `idx_template_type` (`template_type`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `fk_sys_template_uploader` FOREIGN KEY (`uploaded_by`) REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------
-- 17. const_init_institutions 机构常量库（36K+，仅用于注册搜索）
-- 数据量大，需单独导入（见 const_init_institutions 数据文件）
-- ----------------------------------------------------------------
CREATE TABLE `const_init_institutions` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT,
  `code`       VARCHAR(64)  NOT NULL,
  `uscc`       VARCHAR(32)  NOT NULL,
  `name`       VARCHAR(200) NOT NULL,
  `region`     VARCHAR(64),
  `city`       VARCHAR(50),
  `level`      VARCHAR(32),
  `category`   VARCHAR(64),
  `created_at` DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  UNIQUE KEY `uk_uscc` (`uscc`),
  KEY `idx_name` (`name`),
  KEY `idx_region` (`region`),
  KEY `idx_city` (`city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机构常量库（36K+，仅用于注册时搜索）';

-- ----------------------------------------------------------------
-- 18. pinguan_his_data 历史数据（导入用）
-- ----------------------------------------------------------------
CREATE TABLE `pinguan_his_data` (
  `id`                     INT  NOT NULL AUTO_INCREMENT,
  `data_status`            TEXT,
  `input_person`           TEXT,
  `input_date`             TEXT,
  `year`                   TEXT,
  `group_name`             TEXT,
  `project_code`           TEXT,
  `competition_group`      TEXT,
  `project_name`           TEXT,
  `institution_name`       TEXT,
  `institution_level`      TEXT,
  `institution_address`    TEXT,
  `total_beds`             TEXT,
  `hospital_contact_name`  TEXT,
  `hospital_contact_title` TEXT,
  `hospital_contact_phone` TEXT,
  `hospital_contact_email` TEXT,
  `project_leader_name`    TEXT,
  `project_leader_title`   TEXT,
  `project_leader_phone`   TEXT,
  `project_leader_email`   TEXT,
  `circle_name`            TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================================
-- 初始数据
-- ================================================================

-- ----------------------------------------------------------------
-- 数据1: 字典项（改善就医环境 + 医疗质量安全主题）
-- ----------------------------------------------------------------
INSERT INTO `dictionary_items` (`type`, `code`, `label`, `active`, `sort_order`, `created_at`) VALUES
('experience_improve', 'appointment_service',      '预约诊疗服务更加便捷',                    1,  1, NOW()),
('experience_improve', 'outpatient_process',        '门诊就诊更加优化',                        1,  2, NOW()),
('experience_improve', 'inpatient_experience',      '患者住院体验更加舒适',                    1,  3, NOW()),
('experience_improve', 'post_hospital_service',     '院后医疗服务更加连续',                    1,  4, NOW()),
('experience_improve', 'pre_inpatient_connection',  '院前院内衔接更加高效',                    1,  5, NOW()),
('experience_improve', 'comfortable_environment',   '舒心就医环境更加温馨',                    1,  6, NOW()),
('experience_improve', 'internet_diagnosis',        '互联网诊疗更加便捷',                      1,  7, NOW()),
('experience_improve', 'other',                     '其他',                                    1,  8, NOW()),
('quality_topic', 'stemi_reperfusion',              '提高急性ST段抬高型心肌梗死再灌注治疗率',  1,  1, NOW()),
('quality_topic', 'stroke_reperfusion',             '提高急性脑梗死再灌注治疗率',              1,  2, NOW()),
('quality_topic', 'tumor_tnm_staging',              '提高肿瘤治疗前临床TNM分期评估率',        1,  3, NOW()),
('quality_topic', 'antibiotic_pathogen_test',       '提高住院患者抗菌药物治疗前病原学送检率',  1,  4, NOW()),
('quality_topic', 'perioperative_mortality',        '降低住院患者围手术期死亡率',              1,  5, NOW()),
('quality_topic', 'vte_prevention',                 '提高静脉血栓栓塞症规范预防率',            1,  6, NOW()),
('quality_topic', 'septic_shock_bundle',            '提高感染性休克集束化治疗完成率',          1,  7, NOW()),
('quality_topic', 'adverse_event_report',           '提高医疗质量安全不良事件报告率',          1,  8, NOW()),
('quality_topic', 'iv_infusion_standard',           '降低住院患者静脉输液规范使用率',          1,  9, NOW()),
('quality_topic', 'level4_surgery_mdt',             '提高四级手术术前多学科讨论完成率',        1, 10, NOW()),
('quality_topic', 'vaginal_delivery_complication',  '降低阴道分娩并发症发生率',                1, 11, NOW()),
('quality_topic', 'unplanned_reoperation',          '降低非计划重返手术室再手术率',            1, 12, NOW()),
('quality_topic', 'key_diagnosis_record',           '提高关键诊疗行为相关记录完整率',          1, 13, NOW()),
('quality_topic', 'other',                          '其他',                                    1, 14, NOW());

-- ----------------------------------------------------------------
-- 数据2: 外部机构（评审专家所在的非医院机构）
-- ----------------------------------------------------------------
INSERT INTO `institutions` (`name`, `code`, `uscc`, `region`, `level`, `is_ext`, `created_at`) VALUES
('卡内基',                        'EXT_CARNEGIE',      'EXT000000001', '外部',   '外部机构', 1, NOW()),
('浙江省护理质控中心',            'EXT_NURSING_QC',    'EXT000000002', '浙江省', '外部机构', 1, NOW()),
('浙江省质量协会',                'EXT_QUALITY_ASSOC', 'EXT000000003', '浙江省', '外部机构', 1, NOW()),
('浙江省医疗服务管理评价中心',    'EXT_MEDICAL_EVAL',  'EXT000000004', '浙江省', '外部机构', 1, NOW());

-- ----------------------------------------------------------------
-- 数据3: 初始账号
-- 密码须用 BCrypt 哈希后填入，可在启动前用如下命令生成：
--   python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt(10)).decode())"
-- 或通过 /api/admin/accounts 接口由 OPS 角色创建
-- ----------------------------------------------------------------
-- 示例（请替换密码哈希）：
-- INSERT INTO `user_accounts` (`phone`, `password`, `name`, `role`, `enabled`, `created_at`) VALUES
-- ('13800000001', '$2a$10$REPLACE_WITH_REAL_BCRYPT_HASH', '系统运营', 'OPS', 1, NOW());
