SET NAMES utf8mb4;
DROP TABLE IF EXISTS `activity_infos`;
CREATE TABLE `activity_infos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `avg_age` int NOT NULL,
  `avg_work_years` int NOT NULL,
  `cross_department` bit(1) NOT NULL,
  `experience_improve_code` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `experience_improve_other` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `keywords` varchar(120) COLLATE utf8mb4_general_ci NOT NULL,
  `method_code` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `method_other` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `quality_topic_code` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `quality_topic_other` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `subject_type_code` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `subject_type_other` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `theme` varchar(120) COLLATE utf8mb4_general_ci NOT NULL,
  `registration_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_t940duon9kyq6i7pr45voslgv` (`registration_id`),
  CONSTRAINT `FKmip17q0n7gpsrge4uyn36f9uw` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `activity_templates`;
CREATE TABLE `activity_templates` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `file_url` varchar(300) COLLATE utf8mb4_general_ci NOT NULL,
  `type` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `competition_templates`;
CREATE TABLE `competition_templates` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `file_url` varchar(300) COLLATE utf8mb4_general_ci NOT NULL,
  `type` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `competition_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK4oe4ai1vbnis8o2lcmmduvcs8` (`competition_id`),
  CONSTRAINT `FK4oe4ai1vbnis8o2lcmmduvcs8` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `competitions`;
CREATE TABLE `competitions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `book_review_end` datetime(6) DEFAULT NULL,
  `book_review_start` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `final_end` datetime(6) DEFAULT NULL,
  `final_start` datetime(6) DEFAULT NULL,
  `interview_end` datetime(6) DEFAULT NULL,
  `interview_start` datetime(6) DEFAULT NULL,
  `name` varchar(120) COLLATE utf8mb4_general_ci NOT NULL,
  `register_end` datetime(6) DEFAULT NULL,
  `register_start` datetime(6) DEFAULT NULL,
  `stage` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `dictionary_items`;
CREATE TABLE `dictionary_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `type` varchar(64) NOT NULL,
  `code` varchar(64) NOT NULL,
  `label` varchar(128) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dict_type_code` (`type`,`code`),
  KEY `idx_dict_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `institution_update_requests`;
CREATE TABLE `institution_update_requests` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `new_code` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `new_name` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `new_uscc` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `status` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `institution_id` bigint DEFAULT NULL,
  `submitter_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK7uqtyhb77ovidw0elwrk7iwae` (`institution_id`),
  KEY `FK7wwai6qawudus9p7aw076qxet` (`submitter_id`),
  CONSTRAINT `FK7uqtyhb77ovidw0elwrk7iwae` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`),
  CONSTRAINT `FK7wwai6qawudus9p7aw076qxet` FOREIGN KEY (`submitter_id`) REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `institutions`;
CREATE TABLE `institutions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `code` varchar(64) NOT NULL,
  `uscc` varchar(32) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_institutions_uscc` (`uscc`),
  UNIQUE KEY `uk_institutions_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `material_files`;
CREATE TABLE `material_files` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `file_url` varchar(300) COLLATE utf8mb4_general_ci NOT NULL,
  `type` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `registration_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK5ala7yc1jdcqdbj8vda0kmfw9` (`registration_id`),
  CONSTRAINT `FK5ala7yc1jdcqdbj8vda0kmfw9` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `project_summaries`;
CREATE TABLE `project_summaries` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `discussion` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `plan` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `problem` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `success` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `theme` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `registration_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_oeknxufryd0g6cykxmbfybqkd` (`registration_id`),
  CONSTRAINT `FKi7du0ehl372gfqfl0a88236v4` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `registration_members`;
CREATE TABLE `registration_members` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `department` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `role` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `title` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `registration_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK55lq2g09jdjrwqq2y8loxpw58` (`registration_id`),
  CONSTRAINT `FK55lq2g09jdjrwqq2y8loxpw58` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `registrations`;
CREATE TABLE `registrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `group_code` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `group_type` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `project_name` varchar(120) COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `applicant_id` bigint DEFAULT NULL,
  `competition_id` bigint DEFAULT NULL,
  `institution_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKdercratfq5evkm8d7yh13ku9p` (`applicant_id`),
  KEY `FKj2yh1bfcq390r89211vytkwk1` (`competition_id`),
  KEY `FKglq8j7uimay1gi4y6a8mu29h0` (`institution_id`),
  CONSTRAINT `FKdercratfq5evkm8d7yh13ku9p` FOREIGN KEY (`applicant_id`) REFERENCES `user_accounts` (`id`),
  CONSTRAINT `FKglq8j7uimay1gi4y6a8mu29h0` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`),
  CONSTRAINT `FKj2yh1bfcq390r89211vytkwk1` FOREIGN KEY (`competition_id`) REFERENCES `competitions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `review_scores`;
CREATE TABLE `review_scores` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` int NOT NULL,
  `highlight` varchar(500) COLLATE utf8mb4_general_ci NOT NULL,
  `operation` int NOT NULL,
  `plan` int NOT NULL,
  `presentation` int NOT NULL,
  `problem` int NOT NULL,
  `review` int NOT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `success` int NOT NULL,
  `total` int NOT NULL,
  `weakness` varchar(500) COLLATE utf8mb4_general_ci NOT NULL,
  `review_task_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_e3b9r6w52qch45rtb3l6dj6nl` (`review_task_id`),
  CONSTRAINT `FK7oj8jiikagymmqwmcxh2njc61` FOREIGN KEY (`review_task_id`) REFERENCES `review_tasks` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `review_tasks`;
CREATE TABLE `review_tasks` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `stage` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `registration_id` bigint DEFAULT NULL,
  `reviewer_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKiop4llp8pr0q5ycbyelr9yjmu` (`registration_id`),
  KEY `FK9m64yocnbljqw7aohayievsdc` (`reviewer_id`),
  CONSTRAINT `FK9m64yocnbljqw7aohayievsdc` FOREIGN KEY (`reviewer_id`) REFERENCES `user_accounts` (`id`),
  CONSTRAINT `FKiop4llp8pr0q5ycbyelr9yjmu` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `system_settings`;
CREATE TABLE `system_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `setting_value` varchar(300) COLLATE utf8mb4_general_ci NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_nm18l4pyovtvd8y3b3x0l2y64` (`setting_key`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `user_accounts`;
CREATE TABLE `user_accounts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `name` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `phone` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `role` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `title` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `institution_id` bigint DEFAULT NULL,
  `interview_group_code` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `reviewer_group_code` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_d1kjq3fgvql3tpx3uxykw62ka` (`phone`),
  KEY `FKdto7da4srpbv7xoqfxc0p6spg` (`institution_id`),
  CONSTRAINT `FKdto7da4srpbv7xoqfxc0p6spg` FOREIGN KEY (`institution_id`) REFERENCES `institutions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

