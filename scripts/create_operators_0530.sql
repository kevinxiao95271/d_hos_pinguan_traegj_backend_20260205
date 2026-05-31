-- ============================================================
-- OPERATOR 账号创建 + 会场分配（密码 opt123）
-- 生成时间: 2026-05-30
-- ============================================================
-- 密码哈希: $2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G

-- 1. 创建工作人员账号（OPERATOR 角色）
-- 沈佩儿 13588040680 负责: 综合组-问题解决型专场1（三楼开元A厅） / 综合组-问题解决型专场2（三楼开元A厅） / 综合组-问题解决型专场4(三楼开元A厅)
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('沈佩儿', '13588040680', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 钱丽华 15825502873 负责: 综合组-课题达成及QFD专场2改1（三楼开元B厅） / 综合组-课题达成及QFD专场2（三楼开元B厅） / 综合组-课题达成及QFD专场3（三楼开元B厅）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('钱丽华', '15825502873', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 周桉 18057127990 负责: 进阶组1组（三楼萧然厅） / 进阶组 2组（三楼萧然厅） / 进阶组3组（三楼萧然厅）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('周桉', '18057127990', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 华佳宁 18868634981 负责: 基层组2组（锦绣厅） / 综合组-十大安全目标专场1（三楼锦绣厅） / 综合组-十大安全目标专场2（三楼锦绣厅）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('华佳宁', '18868634981', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 汪洋 15996257167 负责: 综合组-综合工具专场1（三楼锦兰厅） / 综合组-综合工具专场2（三楼锦兰厅） / 综合组-问题解决型专场3（三楼锦兰厅）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('汪洋', '15996257167', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 江玲 18858161236 负责: 综合组-PDCA专场1（二楼名仕厅） / 综合组-PDCA专场2（二楼名仕厅） / 综合组-PDCA专场3（二楼名仕厅）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('江玲', '18858161236', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');
-- 田阳帆 18258881995 负责: 基层组1组（一楼活动中心） / 基层组3组（一楼活动中心） / 基层组4组（一楼活动中心）
INSERT INTO user_accounts (name, phone, `password`, role, enabled, created_at)
  VALUES ('田阳帆', '18258881995', '$2a$10$0SyCHo/YWNgwcv4M/ttR.eDg5ZIwnKtAqRzSv8OYnqMu5WrunvG3G', 'OPERATOR', 1, '2026-05-30 00:00:00');

-- 2. 分配会场（用子查询根据手机号获取 id）
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-问题解决型专场1（三楼开元A厅）' FROM user_accounts WHERE phone='13588040680' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-问题解决型专场2（三楼开元A厅）' FROM user_accounts WHERE phone='13588040680' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-问题解决型专场4(三楼开元A厅)' FROM user_accounts WHERE phone='13588040680' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-课题达成及QFD专场2改1（三楼开元B厅）' FROM user_accounts WHERE phone='15825502873' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-课题达成及QFD专场2（三楼开元B厅）' FROM user_accounts WHERE phone='15825502873' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-课题达成及QFD专场3（三楼开元B厅）' FROM user_accounts WHERE phone='15825502873' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '进阶组1组（三楼萧然厅）' FROM user_accounts WHERE phone='18057127990' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '进阶组 2组（三楼萧然厅）' FROM user_accounts WHERE phone='18057127990' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '进阶组3组（三楼萧然厅）' FROM user_accounts WHERE phone='18057127990' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '基层组2组（锦绣厅）' FROM user_accounts WHERE phone='18868634981' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-十大安全目标专场1（三楼锦绣厅）' FROM user_accounts WHERE phone='18868634981' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-十大安全目标专场2（三楼锦绣厅）' FROM user_accounts WHERE phone='18868634981' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-综合工具专场1（三楼锦兰厅）' FROM user_accounts WHERE phone='15996257167' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-综合工具专场2（三楼锦兰厅）' FROM user_accounts WHERE phone='15996257167' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-问题解决型专场3（三楼锦兰厅）' FROM user_accounts WHERE phone='15996257167' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-PDCA专场1（二楼名仕厅）' FROM user_accounts WHERE phone='18858161236' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-PDCA专场2（二楼名仕厅）' FROM user_accounts WHERE phone='18858161236' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '综合组-PDCA专场3（二楼名仕厅）' FROM user_accounts WHERE phone='18858161236' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '基层组1组（一楼活动中心）' FROM user_accounts WHERE phone='18258881995' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '基层组3组（一楼活动中心）' FROM user_accounts WHERE phone='18258881995' LIMIT 1;
INSERT INTO staff_session_assignments (staff_id, session_code)
  SELECT id, '基层组4组（一楼活动中心）' FROM user_accounts WHERE phone='18258881995' LIMIT 1;

-- 3. 验证结果
SELECT ua.name, ua.phone, ssa.session_code
FROM staff_session_assignments ssa
JOIN user_accounts ua ON ua.id = ssa.staff_id
ORDER BY ua.name, ssa.session_code;