-- ============================================================
-- 生产部署：OPERATOR 功能所需 DDL + 数据
-- 前提：migrate_session_code_0531.sql Step1-3 已执行
-- 生成时间: 2026-05-31
-- ============================================================

-- Step 1: 建表 staff_session_assignments
CREATE TABLE IF NOT EXISTS staff_session_assignments (
  id        BIGINT      NOT NULL AUTO_INCREMENT,
  staff_id  BIGINT      NOT NULL,
  session_code VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_staff_session (staff_id, session_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作人员会场权限';

-- Step 2: 插入/更新 7 个 OPERATOR 账号（密码 opt123）
-- BCrypt hash for opt123 ($2a$)
INSERT INTO user_accounts (phone, name, password, role, created_at)
VALUES
  ('13588040680', '沈佩儿', '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('15825502873', '钱丽华', '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('18057127990', '周桉',   '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('18868634981', '华佳宁', '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('15996257167', '汪洋',   '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('18858161236', '江玲',   '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW()),
  ('18258881995', '田阳帆', '$2a$10$iVH6UCy0ySCvsNJwVulabeVKWFxyFh692cI4JwaGFJyLE8S8yezqe', 'OPERATOR', NOW())
ON DUPLICATE KEY UPDATE
  name     = VALUES(name),
  password = VALUES(password),
  role     = VALUES(role);

-- Step 3: 插入会场权限（使用 2026xxx 新格式）
-- 先清旧数据（幂等）
DELETE ssa FROM staff_session_assignments ssa
JOIN user_accounts ua ON ua.id = ssa.staff_id
WHERE ua.phone IN ('13588040680','15825502873','18057127990','18868634981','15996257167','18858161236','18258881995');

-- 沈佩儿 - 问题解决型 1/2/4
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026综合组问题解决型专场1' FROM user_accounts WHERE phone = '13588040680'
UNION ALL
SELECT id, '2026综合组问题解决型专场2' FROM user_accounts WHERE phone = '13588040680'
UNION ALL
SELECT id, '2026综合组问题解决型专场4' FROM user_accounts WHERE phone = '13588040680';

-- 钱丽华 - QFD课题达成 1/2/3
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026综合组QFD、课题达成型专场1' FROM user_accounts WHERE phone = '15825502873'
UNION ALL
SELECT id, '2026综合组QFD、课题达成型专场2' FROM user_accounts WHERE phone = '15825502873'
UNION ALL
SELECT id, '2026综合组QFD、课题达成型专场3' FROM user_accounts WHERE phone = '15825502873';

-- 周桉 - 进阶组 1/2/3
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026进阶组1组' FROM user_accounts WHERE phone = '18057127990'
UNION ALL
SELECT id, '2026进阶组2组' FROM user_accounts WHERE phone = '18057127990'
UNION ALL
SELECT id, '2026进阶组3组' FROM user_accounts WHERE phone = '18057127990';

-- 华佳宁 - 基层组2 / 十大安全目标1/2
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026基层组2组'              FROM user_accounts WHERE phone = '18868634981'
UNION ALL
SELECT id, '2026综合组十大安全目标专场1' FROM user_accounts WHERE phone = '18868634981'
UNION ALL
SELECT id, '2026综合组十大安全目标专场2' FROM user_accounts WHERE phone = '18868634981';

-- 汪洋 - 综合工具1/2 / 问题解决型3
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026综合组综合工具专场1'   FROM user_accounts WHERE phone = '15996257167'
UNION ALL
SELECT id, '2026综合组综合工具专场2'   FROM user_accounts WHERE phone = '15996257167'
UNION ALL
SELECT id, '2026综合组问题解决型专场3' FROM user_accounts WHERE phone = '15996257167';

-- 江玲 - PDCA 1/2/3
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026综合组PDCA专场1' FROM user_accounts WHERE phone = '18858161236'
UNION ALL
SELECT id, '2026综合组PDCA专场2' FROM user_accounts WHERE phone = '18858161236'
UNION ALL
SELECT id, '2026综合组PDCA专场3' FROM user_accounts WHERE phone = '18858161236';

-- 田阳帆 - 基层组 1/3/4
INSERT INTO staff_session_assignments (staff_id, session_code)
SELECT id, '2026基层组1组' FROM user_accounts WHERE phone = '18258881995'
UNION ALL
SELECT id, '2026基层组3组' FROM user_accounts WHERE phone = '18258881995'
UNION ALL
SELECT id, '2026基层组4组' FROM user_accounts WHERE phone = '18258881995';

-- 验证
SELECT ua.phone, ua.name, ssa.session_code
FROM staff_session_assignments ssa
JOIN user_accounts ua ON ua.id = ssa.staff_id
ORDER BY ua.phone, ssa.session_code;
