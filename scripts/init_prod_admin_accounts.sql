-- 初始化管理账号（仅 OPS + COMMITTEE_ADMIN）
-- 说明：
-- 1) 本脚本不创建 COMMITTEE
-- 2) 账号按手机号唯一键 upsert
-- 3) institution_id 置空（管理账号）
-- 4) 初始明文密码（请首登后立即修改）：
--    OPS: ops2026
--    COMMITTEE_ADMIN: committee2026

START TRANSACTION;

INSERT INTO user_accounts (
  phone, password, name, title, role, institution_id, enabled, created_at
) VALUES
  ('13800010001', '$2b$10$pE/Zq1Tp5z0Y9f5VEwwN5uX.Hho8OqQIF7QMkNaYMGv.5ftbHVVyW', '系统运营1', NULL, 'OPS', NULL, 1, NOW()),
  ('13800010002', '$2b$10$83U1gzTSa5D/F8vY2vcOf.1LnUJy8HLjKbg.MImppo0NhWAGD8OKW', '系统运营2', NULL, 'OPS', NULL, 1, NOW()),
  ('13800010003', '$2b$10$MCNSa.NOvKMhMdojxb44hOlDXGk3xcwoqNRd.C7vMbKX4yP8kCNAy', '系统运营3', NULL, 'OPS', NULL, 1, NOW()),
  ('13800020001', '$2b$10$lqlCj.S.zQNSeXa8O3J.zOcrxVYZ5L6L76miN1GgAnlbAH449pRgO', '组委会管理员1', NULL, 'COMMITTEE_ADMIN', NULL, 1, NOW()),
  ('13800020002', '$2b$10$T2148zT7QQrWShQZLJgBeeM/F7080i3C5Z/YQFIEKLIAAox9LDPkq', '组委会管理员2', NULL, 'COMMITTEE_ADMIN', NULL, 1, NOW()),
  ('13800020003', '$2b$10$KtBNj0feqUUKIK8jlv07NOL.iogZJzFbr.rYr5ujcuEC00BcIhAOq', '组委会管理员3', NULL, 'COMMITTEE_ADMIN', NULL, 1, NOW())
ON DUPLICATE KEY UPDATE
  password = VALUES(password),
  name = VALUES(name),
  role = VALUES(role),
  institution_id = NULL,
  enabled = VALUES(enabled);

COMMIT;
