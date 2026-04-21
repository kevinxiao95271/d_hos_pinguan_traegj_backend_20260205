-- =============================================================
-- DDL：多须知确认支持（reviewer_integrity_notices）
-- 生成日期：2026-04-21
-- 对应需求：移动端页面 / pendingIntegrityNoticeKeys
-- =============================================================

-- ---------------------------------------------------------------
-- 1. 新表：reviewer_integrity_notices
--    记录每位评审专家对每条须知的确认状态
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviewer_integrity_notices (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    user_id     BIGINT       NOT NULL COMMENT '评审专家 user_accounts.id',
    notice_key  VARCHAR(32)  NOT NULL COMMENT '须知标识，如 BOOK / INTERVIEW',
    confirmed_at DATETIME(6) NOT NULL COMMENT '确认时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_rin_user_key (user_id, notice_key),
    INDEX  idx_rin_user   (user_id),
    CONSTRAINT fk_rin_user FOREIGN KEY (user_id) REFERENCES user_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='评审专家多须知确认记录';


-- ---------------------------------------------------------------
-- 2. 历史数据迁移
--    将 notice_confirmed_at 非空的专家，补写一条 BOOK 确认记录
--    幂等（INSERT IGNORE），可重复执行
-- ---------------------------------------------------------------
INSERT IGNORE INTO reviewer_integrity_notices (user_id, notice_key, confirmed_at)
SELECT id, 'BOOK', notice_confirmed_at
FROM   user_accounts
WHERE  notice_confirmed_at IS NOT NULL
  AND  role = 'REVIEWER';


-- ---------------------------------------------------------------
-- 3. 旧列保留说明
--    user_accounts.notice_confirmed_at 列不删除；
--    新版确认逻辑在写 reviewer_integrity_notices 时，
--    若 notice_key = 'BOOK'，同步写 notice_confirmed_at 保持兼容。
-- ---------------------------------------------------------------

-- =============================================================
-- 须知 key 说明（与前端 src/config/integrityNotices.js 对齐）
-- =============================================================
-- BOOK      : 诚信须知（书面，原有唯一须知）
-- INTERVIEW : 面谈须知（面谈阶段展示）
-- （后续如需新增须知，只需在前后端配置里增加 key，
--   数据库无需改结构，直接插新行即可。）
