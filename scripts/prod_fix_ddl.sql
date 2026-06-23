-- ============================================================
-- 第一步：排查 final_ranking_snapshots 缺哪些列
-- （查出来的是已存在的列，没出现的就是缺失的）
-- ============================================================
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'final_ranking_snapshots'
  AND COLUMN_NAME IN (
    'id',
    'competition_id',
    'registration_id',
    'session_date',
    'session_code',
    'session_order',
    'score_form',
    'judge_score_count',
    'session_removed_max',
    'session_removed_min',
    'trimmed_avg',
    'session_rank',
    'book_review_score',
    'total_score',
    'total_rank',
    'book_score_d',
    'interview_score_d',
    'award_level',
    'calculated_at',
    'group_type'
  )
ORDER BY COLUMN_NAME;


-- ============================================================
-- 第二步：按需补列（缺哪条跑哪条，已存在的跳过）
-- ============================================================
ALTER TABLE final_ranking_snapshots ADD COLUMN session_date         VARCHAR(8)   NULL    COMMENT '比赛日期';
ALTER TABLE final_ranking_snapshots ADD COLUMN session_order        INT          NULL    COMMENT '上台顺序';
ALTER TABLE final_ranking_snapshots ADD COLUMN score_form           VARCHAR(10)  NULL    COMMENT '评分表类型';
ALTER TABLE final_ranking_snapshots ADD COLUMN judge_score_count    INT          NULL    COMMENT '参与评委数';
ALTER TABLE final_ranking_snapshots ADD COLUMN session_removed_max  DOUBLE       NULL    COMMENT '去极值最高分';
ALTER TABLE final_ranking_snapshots ADD COLUMN session_removed_min  DOUBLE       NULL    COMMENT '去极值最低分';
ALTER TABLE final_ranking_snapshots ADD COLUMN trimmed_avg          DOUBLE       NULL    COMMENT '现场均分';
ALTER TABLE final_ranking_snapshots ADD COLUMN session_rank         INT          NULL    COMMENT '专场均分排名';
ALTER TABLE final_ranking_snapshots ADD COLUMN book_review_score    DOUBLE       NULL    COMMENT '书审D值';
ALTER TABLE final_ranking_snapshots ADD COLUMN total_score          DOUBLE       NULL    COMMENT '综合总分';
ALTER TABLE final_ranking_snapshots ADD COLUMN total_rank           INT          NULL    COMMENT '专场总分排名';
ALTER TABLE final_ranking_snapshots ADD COLUMN book_score_d         DOUBLE       NULL    COMMENT '书审独立D值';
ALTER TABLE final_ranking_snapshots ADD COLUMN interview_score_d    DOUBLE       NULL    COMMENT '面谈D值';
ALTER TABLE final_ranking_snapshots ADD COLUMN award_level          VARCHAR(10)  NULL    COMMENT '奖项';
ALTER TABLE final_ranking_snapshots ADD COLUMN calculated_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间';
ALTER TABLE final_ranking_snapshots ADD COLUMN group_type           VARCHAR(32)  NULL    COMMENT '组别（BASIC/COMPREHENSIVE/ADVANCED）';


-- ============================================================
-- 第三步：registrations 缺失列补充
-- ============================================================
ALTER TABLE registrations ADD COLUMN registration_code    INT         NULL COMMENT '项目编号';
ALTER TABLE registrations ADD COLUMN project_leader_name  VARCHAR(60) NULL COMMENT '负责人姓名';
ALTER TABLE registrations ADD COLUMN project_leader_phone VARCHAR(20) NULL COMMENT '负责人电话';
ALTER TABLE registrations ADD COLUMN project_leader_title VARCHAR(60) NULL COMMENT '负责人职称';


-- ============================================================
-- 第四步：新建 staff_session_assignments 表
-- ============================================================
CREATE TABLE IF NOT EXISTS staff_session_assignments (
  id           BIGINT       NOT NULL AUTO_INCREMENT,
  staff_id     BIGINT       NOT NULL,
  session_code VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_staff_session (staff_id, session_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监督员专场分配';
