-- 报名草稿表体系（正式附属表 registration_id 保持 NOT NULL 不变）
-- 草稿期数据存 draft_* 表；submit 时 COPY 到正式表

CREATE TABLE IF NOT EXISTS `registration_drafts` (
  `id`                    BIGINT       NOT NULL AUTO_INCREMENT,
  `competition_id`        BIGINT       NOT NULL,
  `institution_id`        BIGINT       NOT NULL,
  `applicant_id`          BIGINT       NOT NULL,
  `project_name`          VARCHAR(120) NOT NULL,
  `group_type`            VARCHAR(32)  NOT NULL COMMENT 'BASIC|COMPREHENSIVE|ADVANCED',
  `project_leader_name`   VARCHAR(60)  NULL,
  `project_leader_phone`  VARCHAR(20)  NULL,
  `project_leader_title`  VARCHAR(60)  NULL,
  `created_at`            DATETIME(6)  NOT NULL,
  `updated_at`            DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_rd_competition` (`competition_id`),
  KEY `idx_rd_applicant` (`applicant_id`),
  KEY `idx_rd_institution` (`institution_id`),
  CONSTRAINT `fk_rd_competition` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`),
  CONSTRAINT `fk_rd_institution` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`),
  CONSTRAINT `fk_rd_applicant`   FOREIGN KEY (`applicant_id`)   REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `registration_draft_members` (
  `id`       BIGINT      NOT NULL AUTO_INCREMENT,
  `draft_id` BIGINT      NOT NULL,
  `role`     VARCHAR(32) NOT NULL COMMENT 'PARTICIPANT|MENTOR',
  `name`     VARCHAR(64) NOT NULL,
  `title`    VARCHAR(64) NOT NULL,
  `department` VARCHAR(64) NULL,
  PRIMARY KEY (`id`),
  KEY `idx_rdm_draft_id` (`draft_id`),
  CONSTRAINT `fk_rdm_draft` FOREIGN KEY (`draft_id`) REFERENCES `registration_drafts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `registration_draft_activity_infos` (
  `id`                       BIGINT       NOT NULL AUTO_INCREMENT,
  `draft_id`                 BIGINT       NOT NULL,
  `theme`                    VARCHAR(120) NOT NULL,
  `keywords`                 VARCHAR(120) NOT NULL,
  `subject_type_code`        VARCHAR(64)  NOT NULL,
  `subject_type_other`       VARCHAR(200) NULL,
  `method_code`              VARCHAR(64)  NOT NULL,
  `method_other`             VARCHAR(200) NULL,
  `experience_improve_code`  VARCHAR(64)  NOT NULL,
  `experience_improve_other` VARCHAR(200) NULL,
  `quality_topic_code`       VARCHAR(64)  NOT NULL,
  `quality_topic_other`      VARCHAR(200) NULL,
  `avg_work_years`           INT          NOT NULL,
  `avg_age`                  INT          NOT NULL,
  `cross_department`         TINYINT      NOT NULL,
  `related_to_digital_ai`    TINYINT      NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_rda_draft_id` (`draft_id`),
  CONSTRAINT `fk_rda_draft` FOREIGN KEY (`draft_id`) REFERENCES `registration_drafts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `registration_draft_project_summaries` (
  `id`           BIGINT        NOT NULL AUTO_INCREMENT,
  `draft_id`     BIGINT        NOT NULL,
  `theme`        VARCHAR(200)  NOT NULL,
  `plan`         VARCHAR(1000) NOT NULL,
  `problem`      VARCHAR(1000) NOT NULL,
  `action`       VARCHAR(1000) NOT NULL,
  `success`      VARCHAR(1000) NOT NULL,
  `discussion`   VARCHAR(1000) NOT NULL,
  `operation`    VARCHAR(1000) NULL,
  `presentation` VARCHAR(1000) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_rdps_draft_id` (`draft_id`),
  CONSTRAINT `fk_rdps_draft` FOREIGN KEY (`draft_id`) REFERENCES `registration_drafts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `registration_draft_material_files` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT,
  `draft_id`    BIGINT       NOT NULL,
  `type`        VARCHAR(64)  NOT NULL,
  `file_name`   VARCHAR(200) NOT NULL,
  `file_url`    VARCHAR(300) NOT NULL,
  `file_hash`   VARCHAR(64)  NULL,
  `uploaded_at` DATETIME(6)  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_rdmat_draft_type` (`draft_id`, `type`),
  CONSTRAINT `fk_rdmat_draft` FOREIGN KEY (`draft_id`) REFERENCES `registration_drafts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
