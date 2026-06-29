-- ============================================================
-- 迁移 final_session_code 为标准组别格式
-- 1. 新增 final_session_code_desc 保留原值
-- 2. 更新 final_session_code 为 Excel 组别标准格式
-- 3. 同步 staff_session_assignments
-- 生成时间: 2026-05-31
-- ============================================================

-- Step 1: 新增描述列（保留原值）
ALTER TABLE registrations
  ADD COLUMN final_session_code_desc VARCHAR(128) DEFAULT NULL
  COMMENT '现场场次原始描述（含场地名）'
  AFTER final_session_code;

-- Step 2: 备份原值
UPDATE registrations
SET final_session_code_desc = final_session_code
WHERE final_session_code IS NOT NULL;

-- Step 3: 更新 final_session_code 为标准格式（21 个场次）

-- 基层组
UPDATE registrations SET final_session_code = '2026基层组1组' WHERE final_session_code = '基层组1组（一楼活动中心）';
UPDATE registrations SET final_session_code = '2026基层组2组' WHERE final_session_code = '基层组2组（锦绣厅）';
UPDATE registrations SET final_session_code = '2026基层组3组' WHERE final_session_code = '基层组3组（一楼活动中心）';
UPDATE registrations SET final_session_code = '2026基层组4组' WHERE final_session_code = '基层组4组（一楼活动中心）';

-- 进阶组（注意"进阶组 2组"原值含空格）
UPDATE registrations SET final_session_code = '2026进阶组1组' WHERE final_session_code = '进阶组1组（三楼萧然厅）';
UPDATE registrations SET final_session_code = '2026进阶组2组' WHERE final_session_code = '进阶组 2组（三楼萧然厅）';
UPDATE registrations SET final_session_code = '2026进阶组3组' WHERE final_session_code = '进阶组3组（三楼萧然厅）';

-- 综合组 PDCA
UPDATE registrations SET final_session_code = '2026综合组PDCA专场1' WHERE final_session_code = '综合组-PDCA专场1（二楼名仕厅）';
UPDATE registrations SET final_session_code = '2026综合组PDCA专场2' WHERE final_session_code = '综合组-PDCA专场2（二楼名仕厅）';
UPDATE registrations SET final_session_code = '2026综合组PDCA专场3' WHERE final_session_code = '综合组-PDCA专场3（二楼名仕厅）';

-- 综合组 综合工具
UPDATE registrations SET final_session_code = '2026综合组综合工具专场1' WHERE final_session_code = '综合组-综合工具专场1（三楼锦兰厅）';
UPDATE registrations SET final_session_code = '2026综合组综合工具专场2' WHERE final_session_code = '综合组-综合工具专场2（三楼锦兰厅）';

-- 综合组 十大安全目标
UPDATE registrations SET final_session_code = '2026综合组十大安全目标专场1' WHERE final_session_code = '综合组-十大安全目标专场1（三楼锦绣厅）';
UPDATE registrations SET final_session_code = '2026综合组十大安全目标专场2' WHERE final_session_code = '综合组-十大安全目标专场2（三楼锦绣厅）';

-- 综合组 问题解决型（注意专场4括号无空格）
UPDATE registrations SET final_session_code = '2026综合组问题解决型专场1' WHERE final_session_code = '综合组-问题解决型专场1（三楼开元A厅）';
UPDATE registrations SET final_session_code = '2026综合组问题解决型专场2' WHERE final_session_code = '综合组-问题解决型专场2（三楼开元A厅）';
UPDATE registrations SET final_session_code = '2026综合组问题解决型专场3' WHERE final_session_code = '综合组-问题解决型专场3（三楼锦兰厅）';
UPDATE registrations SET final_session_code = '2026综合组问题解决型专场4' WHERE final_session_code = '综合组-问题解决型专场4(三楼开元A厅)';

-- 综合组 QFD课题达成（"专场2改1"是第1场，"专场2"是第2场）
UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场1' WHERE final_session_code = '综合组-课题达成及QFD专场2改1（三楼开元B厅）';
UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场2' WHERE final_session_code = '综合组-课题达成及QFD专场2（三楼开元B厅）';
UPDATE registrations SET final_session_code = '2026综合组QFD、课题达成型专场3' WHERE final_session_code = '综合组-课题达成及QFD专场3（三楼开元B厅）';

-- Step 4: 同步 staff_session_assignments（OPERATOR 可见范围）
UPDATE staff_session_assignments SET session_code = '2026基层组1组'              WHERE session_code = '基层组1组（一楼活动中心）';
UPDATE staff_session_assignments SET session_code = '2026基层组2组'              WHERE session_code = '基层组2组（锦绣厅）';
UPDATE staff_session_assignments SET session_code = '2026基层组3组'              WHERE session_code = '基层组3组（一楼活动中心）';
UPDATE staff_session_assignments SET session_code = '2026基层组4组'              WHERE session_code = '基层组4组（一楼活动中心）';
UPDATE staff_session_assignments SET session_code = '2026进阶组1组'              WHERE session_code = '进阶组1组（三楼萧然厅）';
UPDATE staff_session_assignments SET session_code = '2026进阶组2组'              WHERE session_code = '进阶组 2组（三楼萧然厅）';
UPDATE staff_session_assignments SET session_code = '2026进阶组3组'              WHERE session_code = '进阶组3组（三楼萧然厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组PDCA专场1'        WHERE session_code = '综合组-PDCA专场1（二楼名仕厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组PDCA专场2'        WHERE session_code = '综合组-PDCA专场2（二楼名仕厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组PDCA专场3'        WHERE session_code = '综合组-PDCA专场3（二楼名仕厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组综合工具专场1'    WHERE session_code = '综合组-综合工具专场1（三楼锦兰厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组综合工具专场2'    WHERE session_code = '综合组-综合工具专场2（三楼锦兰厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组十大安全目标专场1' WHERE session_code = '综合组-十大安全目标专场1（三楼锦绣厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组十大安全目标专场2' WHERE session_code = '综合组-十大安全目标专场2（三楼锦绣厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组问题解决型专场1'  WHERE session_code = '综合组-问题解决型专场1（三楼开元A厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组问题解决型专场2'  WHERE session_code = '综合组-问题解决型专场2（三楼开元A厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组问题解决型专场3'  WHERE session_code = '综合组-问题解决型专场3（三楼锦兰厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组问题解决型专场4'  WHERE session_code = '综合组-问题解决型专场4(三楼开元A厅)';
UPDATE staff_session_assignments SET session_code = '2026综合组QFD、课题达成型专场1' WHERE session_code = '综合组-课题达成及QFD专场2改1（三楼开元B厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组QFD、课题达成型专场2' WHERE session_code = '综合组-课题达成及QFD专场2（三楼开元B厅）';
UPDATE staff_session_assignments SET session_code = '2026综合组QFD、课题达成型专场3' WHERE session_code = '综合组-课题达成及QFD专场3（三楼开元B厅）';

-- 验证（执行后运行）
-- SELECT DISTINCT final_session_code, final_session_code_desc FROM registrations WHERE final_session_code IS NOT NULL ORDER BY final_session_code;
-- SELECT * FROM staff_session_assignments ORDER BY staff_id, session_code;
