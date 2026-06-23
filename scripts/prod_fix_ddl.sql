-- ============================================================
-- 生产库结构修复脚本
-- MySQL 8 兼容，全部幂等（列已存在则跳过，不报错）
-- ============================================================

-- 创建辅助存储过程
DROP PROCEDURE IF EXISTS _add_col;
DELIMITER //
CREATE PROCEDURE _add_col(IN tbl VARCHAR(100), IN col VARCHAR(100), IN col_def TEXT)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = tbl
          AND COLUMN_NAME  = col
    ) THEN
        SET @_sql = CONCAT('ALTER TABLE `', tbl, '` ADD COLUMN `', col, '` ', col_def);
        PREPARE _stmt FROM @_sql;
        EXECUTE _stmt;
        DEALLOCATE PREPARE _stmt;
        SELECT CONCAT('Added: ', tbl, '.', col) AS result;
    ELSE
        SELECT CONCAT('Skip:  ', tbl, '.', col, ' (already exists)') AS result;
    END IF;
END //
DELIMITER ;


-- ============================================================
-- final_ranking_snapshots 补列
-- ============================================================
CALL _add_col('final_ranking_snapshots', 'session_date',        "VARCHAR(8)  NULL COMMENT '比赛日期'");
CALL _add_col('final_ranking_snapshots', 'session_order',       "INT         NULL COMMENT '上台顺序'");
CALL _add_col('final_ranking_snapshots', 'score_form',          "VARCHAR(10) NULL COMMENT '评分表类型'");
CALL _add_col('final_ranking_snapshots', 'judge_score_count',   "INT         NULL COMMENT '参与评委数'");
CALL _add_col('final_ranking_snapshots', 'session_removed_max', "DOUBLE      NULL COMMENT '去极值最高分'");
CALL _add_col('final_ranking_snapshots', 'session_removed_min', "DOUBLE      NULL COMMENT '去极值最低分'");
CALL _add_col('final_ranking_snapshots', 'trimmed_avg',         "DOUBLE      NULL COMMENT '现场均分'");
CALL _add_col('final_ranking_snapshots', 'session_rank',        "INT         NULL COMMENT '专场均分排名'");
CALL _add_col('final_ranking_snapshots', 'book_review_score',   "DOUBLE      NULL COMMENT '书审D值'");
CALL _add_col('final_ranking_snapshots', 'total_score',         "DOUBLE      NULL COMMENT '综合总分'");
CALL _add_col('final_ranking_snapshots', 'total_rank',          "INT         NULL COMMENT '专场总分排名'");
CALL _add_col('final_ranking_snapshots', 'book_score_d',        "DOUBLE      NULL COMMENT '书审独立D值'");
CALL _add_col('final_ranking_snapshots', 'interview_score_d',   "DOUBLE      NULL COMMENT '面谈D值'");
CALL _add_col('final_ranking_snapshots', 'award_level',         "VARCHAR(10) NULL COMMENT '奖项'");
CALL _add_col('final_ranking_snapshots', 'calculated_at',       "DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间'");
CALL _add_col('final_ranking_snapshots', 'group_type',          "VARCHAR(32) NULL COMMENT 'BASIC/COMPREHENSIVE/ADVANCED'");


-- ============================================================
-- registrations 补列
-- ============================================================
CALL _add_col('registrations', 'registration_code',    "INT         NULL COMMENT '项目编号'");
CALL _add_col('registrations', 'project_leader_name',  "VARCHAR(60) NULL COMMENT '负责人姓名'");
CALL _add_col('registrations', 'project_leader_phone', "VARCHAR(20) NULL COMMENT '负责人电话'");
CALL _add_col('registrations', 'project_leader_title', "VARCHAR(60) NULL COMMENT '负责人职称'");


-- ============================================================
-- staff_session_assignments 建表（已存在则跳过）
-- ============================================================
CREATE TABLE IF NOT EXISTS staff_session_assignments (
  id           BIGINT       NOT NULL AUTO_INCREMENT,
  staff_id     BIGINT       NOT NULL,
  session_code VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_staff_session (staff_id, session_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监督员专场分配';


-- 清理辅助过程
DROP PROCEDURE IF EXISTS _add_col;
