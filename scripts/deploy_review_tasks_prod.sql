-- ==============================================================
-- 书审任务分配 review_tasks  (stage=BOOK, status=PENDING)
-- 共 70 位专家，每人对应其组内所有 SUBMITTED 项目
-- INSERT IGNORE 防重复执行
-- ==============================================================

-- 如需重新分配，先清空：
-- DELETE FROM review_tasks WHERE stage = 'BOOK';

-- ── C1 ───────────────────────────────────────────────
-- 秦刚  15868899348
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15868899348' AND ua.name = '秦刚'
WHERE r.group_code = 'C1' AND r.status = 'SUBMITTED';

-- 朱玲凤  13586116171
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13586116171' AND ua.name = '朱玲凤'
WHERE r.group_code = 'C1' AND r.status = 'SUBMITTED';

-- 李盈  13867481815
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13867481815' AND ua.name = '李盈'
WHERE r.group_code = 'C1' AND r.status = 'SUBMITTED';

-- ── C2 ───────────────────────────────────────────────
-- 王临润  13606507266
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13606507266' AND ua.name = '王临润'
WHERE r.group_code = 'C2' AND r.status = 'SUBMITTED';

-- 蔡斌  13957159415
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13957159415' AND ua.name = '蔡斌'
WHERE r.group_code = 'C2' AND r.status = 'SUBMITTED';

-- 冯志仙  13867452301
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13867452301' AND ua.name = '冯志仙'
WHERE r.group_code = 'C2' AND r.status = 'SUBMITTED';

-- ── C3 ───────────────────────────────────────────────
-- 李瑾  15068103880
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15068103880' AND ua.name = '李瑾'
WHERE r.group_code = 'C3' AND r.status = 'SUBMITTED';

-- 胡斌春  13906537115
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13906537115' AND ua.name = '胡斌春'
WHERE r.group_code = 'C3' AND r.status = 'SUBMITTED';

-- 周权  13588758501
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588758501' AND ua.name = '周权'
WHERE r.group_code = 'C3' AND r.status = 'SUBMITTED';

-- ── C4 ───────────────────────────────────────────────
-- 王跃胜  13505899996
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13505899996' AND ua.name = '王跃胜'
WHERE r.group_code = 'C4' AND r.status = 'SUBMITTED';

-- 黄丽华  13867129329
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13867129329' AND ua.name = '黄丽华'
WHERE r.group_code = 'C4' AND r.status = 'SUBMITTED';

-- 李伟  13958009748
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13958009748' AND ua.name = '李伟'
WHERE r.group_code = 'C4' AND r.status = 'SUBMITTED';

-- ── B1 ───────────────────────────────────────────────
-- 卢芳燕  13505817318
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13505817318' AND ua.name = '卢芳燕'
WHERE r.group_code = 'B1' AND r.status = 'SUBMITTED';

-- 卜智斌  18958167819
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '18958167819' AND ua.name = '卜智斌'
WHERE r.group_code = 'B1' AND r.status = 'SUBMITTED';

-- ── B2 ───────────────────────────────────────────────
-- 谭明明  13588092636
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588092636' AND ua.name = '谭明明'
WHERE r.group_code = 'B2' AND r.status = 'SUBMITTED';

-- 戴金华  13605887912
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13605887912' AND ua.name = '戴金华'
WHERE r.group_code = 'B2' AND r.status = 'SUBMITTED';

-- ── B3 ───────────────────────────────────────────────
-- 潘胜东  13666669123
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13666669123' AND ua.name = '潘胜东'
WHERE r.group_code = 'B3' AND r.status = 'SUBMITTED';

-- 蔡晓芳  15990162166
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15990162166' AND ua.name = '蔡晓芳'
WHERE r.group_code = 'B3' AND r.status = 'SUBMITTED';

-- ── B4 ───────────────────────────────────────────────
-- 洪理泉  13606700679
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13606700679' AND ua.name = '洪理泉'
WHERE r.group_code = 'B4' AND r.status = 'SUBMITTED';

-- 刘彩霞  18072963066
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '18072963066' AND ua.name = '刘彩霞'
WHERE r.group_code = 'B4' AND r.status = 'SUBMITTED';

-- ── B5 ───────────────────────────────────────────────
-- 杨永挺  13754322649
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13754322649' AND ua.name = '杨永挺'
WHERE r.group_code = 'B5' AND r.status = 'SUBMITTED';

-- 俞雪芬  13067987798
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13067987798' AND ua.name = '俞雪芬'
WHERE r.group_code = 'B5' AND r.status = 'SUBMITTED';

-- ── B6 ───────────────────────────────────────────────
-- 宋剑平  13757119617
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13757119617' AND ua.name = '宋剑平'
WHERE r.group_code = 'B6' AND r.status = 'SUBMITTED';

-- 方英  15657036200
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15657036200' AND ua.name = '方英'
WHERE r.group_code = 'B6' AND r.status = 'SUBMITTED';

-- ── B7 ───────────────────────────────────────────────
-- 陈美芬  13567618608
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13567618608' AND ua.name = '陈美芬'
WHERE r.group_code = 'B7' AND r.status = 'SUBMITTED';

-- 陈昌贵  13757119185
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13757119185' AND ua.name = '陈昌贵'
WHERE r.group_code = 'B7' AND r.status = 'SUBMITTED';

-- ── B8 ───────────────────────────────────────────────
-- 李益民  13777887810
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13777887810' AND ua.name = '李益民'
WHERE r.group_code = 'B8' AND r.status = 'SUBMITTED';

-- 周莹  13626530377
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13626530377' AND ua.name = '周莹'
WHERE r.group_code = 'B8' AND r.status = 'SUBMITTED';

-- ── B9 ───────────────────────────────────────────────
-- 钱莎莎  13738141961
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13738141961' AND ua.name = '钱莎莎'
WHERE r.group_code = 'B9' AND r.status = 'SUBMITTED';

-- 朱胜春  13511332938
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13511332938' AND ua.name = '朱胜春'
WHERE r.group_code = 'B9' AND r.status = 'SUBMITTED';

-- ── B10 ───────────────────────────────────────────────
-- 赵彩莲  13958061766
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13958061766' AND ua.name = '赵彩莲'
WHERE r.group_code = 'B10' AND r.status = 'SUBMITTED';

-- 徐敏慧  15957921677
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15957921677' AND ua.name = '徐敏慧'
WHERE r.group_code = 'B10' AND r.status = 'SUBMITTED';

-- ── B11 ───────────────────────────────────────────────
-- 方玢茹  13616555849
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13616555849' AND ua.name = '方玢茹'
WHERE r.group_code = 'B11' AND r.status = 'SUBMITTED';

-- 张春梅  15957716111
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15957716111' AND ua.name = '张春梅'
WHERE r.group_code = 'B11' AND r.status = 'SUBMITTED';

-- ── B12 ───────────────────────────────────────────────
-- 陈飞波  13989818108
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13989818108' AND ua.name = '陈飞波'
WHERE r.group_code = 'B12' AND r.status = 'SUBMITTED';

-- 吕娜  13588426741
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588426741' AND ua.name = '吕娜'
WHERE r.group_code = 'B12' AND r.status = 'SUBMITTED';

-- ── B13 ───────────────────────────────────────────────
-- 宁丽  13750848040
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13750848040' AND ua.name = '宁丽'
WHERE r.group_code = 'B13' AND r.status = 'SUBMITTED';

-- 杨军  18072963988
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '18072963988' AND ua.name = '杨军'
WHERE r.group_code = 'B13' AND r.status = 'SUBMITTED';

-- ── B14 ───────────────────────────────────────────────
-- 姚智萍  15857353615
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '15857353615' AND ua.name = '姚智萍'
WHERE r.group_code = 'B14' AND r.status = 'SUBMITTED';

-- 庄一渝  13588708076
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588708076' AND ua.name = '庄一渝'
WHERE r.group_code = 'B14' AND r.status = 'SUBMITTED';

-- ── B15 ───────────────────────────────────────────────
-- 郭佳奕  13566781071
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13566781071' AND ua.name = '郭佳奕'
WHERE r.group_code = 'B15' AND r.status = 'SUBMITTED';

-- 程晓英  13666650508
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13666650508' AND ua.name = '程晓英'
WHERE r.group_code = 'B15' AND r.status = 'SUBMITTED';

-- ── B16 ───────────────────────────────────────────────
-- 朱文俊  13606515730
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13606515730' AND ua.name = '朱文俊'
WHERE r.group_code = 'B16' AND r.status = 'SUBMITTED';

-- 徐辉  13758490818
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13758490818' AND ua.name = '徐辉'
WHERE r.group_code = 'B16' AND r.status = 'SUBMITTED';

-- ── B17 ───────────────────────────────────────────────
-- 蔡雪黎  13857771605
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13857771605' AND ua.name = '蔡雪黎'
WHERE r.group_code = 'B17' AND r.status = 'SUBMITTED';

-- 封亚萍  13867134906
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13867134906' AND ua.name = '封亚萍'
WHERE r.group_code = 'B17' AND r.status = 'SUBMITTED';

-- ── B18 ───────────────────────────────────────────────
-- 陈志良  13567534846
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13567534846' AND ua.name = '陈志良'
WHERE r.group_code = 'B18' AND r.status = 'SUBMITTED';

-- 潘红英  13587179166
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13587179166' AND ua.name = '潘红英'
WHERE r.group_code = 'B18' AND r.status = 'SUBMITTED';

-- ── B19 ───────────────────────────────────────────────
-- 张国兵  13675851802
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13675851802' AND ua.name = '张国兵'
WHERE r.group_code = 'B19' AND r.status = 'SUBMITTED';

-- 兰美娟  13757119537
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13757119537' AND ua.name = '兰美娟'
WHERE r.group_code = 'B19' AND r.status = 'SUBMITTED';

-- ── B20 ───────────────────────────────────────────────
-- 马楠  13958111928
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13958111928' AND ua.name = '马楠'
WHERE r.group_code = 'B20' AND r.status = 'SUBMITTED';

-- 潘红英  13857188922
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13857188922' AND ua.name = '潘红英'
WHERE r.group_code = 'B20' AND r.status = 'SUBMITTED';

-- ── B21 ───────────────────────────────────────────────
-- 郑叶平  13732586305
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13732586305' AND ua.name = '郑叶平'
WHERE r.group_code = 'B21' AND r.status = 'SUBMITTED';

-- 冯济业  13958202082
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13958202082' AND ua.name = '冯济业'
WHERE r.group_code = 'B21' AND r.status = 'SUBMITTED';

-- ── B22 ───────────────────────────────────────────────
-- 王建平  13588887369
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588887369' AND ua.name = '王建平'
WHERE r.group_code = 'B22' AND r.status = 'SUBMITTED';

-- 李雅岑  13777466804
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13777466804' AND ua.name = '李雅岑'
WHERE r.group_code = 'B22' AND r.status = 'SUBMITTED';

-- ── A1 ───────────────────────────────────────────────
-- 周琳  13857211964
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13857211964' AND ua.name = '周琳'
WHERE r.group_code = 'A1' AND r.status = 'SUBMITTED';

-- 叶小云  13605818530
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13605818530' AND ua.name = '叶小云'
WHERE r.group_code = 'A1' AND r.status = 'SUBMITTED';

-- ── A2 ───────────────────────────────────────────────
-- 钱玮  13588330061
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588330061' AND ua.name = '钱玮'
WHERE r.group_code = 'A2' AND r.status = 'SUBMITTED';

-- 朱良枫  13586464989
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13586464989' AND ua.name = '朱良枫'
WHERE r.group_code = 'A2' AND r.status = 'SUBMITTED';

-- ── A3 ───────────────────────────────────────────────
-- 蔡建利  13735192050
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13735192050' AND ua.name = '蔡建利'
WHERE r.group_code = 'A3' AND r.status = 'SUBMITTED';

-- 沈杨  13957883107
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13957883107' AND ua.name = '沈杨'
WHERE r.group_code = 'A3' AND r.status = 'SUBMITTED';

-- ── A4 ───────────────────────────────────────────────
-- 周尧英  13615758052
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13615758052' AND ua.name = '周尧英'
WHERE r.group_code = 'A4' AND r.status = 'SUBMITTED';

-- 严志瑜  13958365721
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13958365721' AND ua.name = '严志瑜'
WHERE r.group_code = 'A4' AND r.status = 'SUBMITTED';

-- ── A5 ───────────────────────────────────────────────
-- 严涓  13588216288
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13588216288' AND ua.name = '严涓'
WHERE r.group_code = 'A5' AND r.status = 'SUBMITTED';

-- 陈雪琴  13957832316
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13957832316' AND ua.name = '陈雪琴'
WHERE r.group_code = 'A5' AND r.status = 'SUBMITTED';

-- ── A6 ───────────────────────────────────────────────
-- 楼尉  13516743880
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13516743880' AND ua.name = '楼尉'
WHERE r.group_code = 'A6' AND r.status = 'SUBMITTED';

-- 袁惠萍  13957228318
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13957228318' AND ua.name = '袁惠萍'
WHERE r.group_code = 'A6' AND r.status = 'SUBMITTED';

-- ── A7 ───────────────────────────────────────────────
-- 朱健倩  13516800991
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13516800991' AND ua.name = '朱健倩'
WHERE r.group_code = 'A7' AND r.status = 'SUBMITTED';

-- 吴海英  13758953542
INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at, updated_at)
SELECT 'BOOK', r.id, ua.id, 'PENDING', NOW(), NOW()
FROM registrations r
JOIN user_accounts ua ON ua.phone = '13758953542' AND ua.name = '吴海英'
WHERE r.group_code = 'A7' AND r.status = 'SUBMITTED';

-- ── 验证 ─────────────────────────────────────────────────────────
SELECT r.group_code,
       COUNT(DISTINCT rt.reviewer_id)     AS reviewer_cnt,
       COUNT(DISTINCT rt.registration_id) AS project_cnt,
       COUNT(*)                           AS task_cnt
FROM review_tasks rt
JOIN registrations r ON r.id = rt.registration_id
WHERE rt.stage = 'BOOK'
GROUP BY r.group_code
ORDER BY r.group_code;