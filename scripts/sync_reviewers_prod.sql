-- ==============================================================
-- 书审专家生产库最小变更脚本
-- 生成依据：专家数据含机构ID0410.csv（生产库快照）vs 4.13 名单
-- 需更新分组: 70 条
-- 需修正机构: 1 条
-- 需新建账号: 0 条
-- ==============================================================

-- ── A. 更新书审分组 (reviewer_group_code) —— 暂缓，不执行
-- （如需执行，取消下方注释即可）
/*
-- 秦刚  15868899348  (空) → C1
UPDATE user_accounts SET reviewer_group_code = 'C1' WHERE phone = '15868899348' AND role = 'REVIEWER';  -- 秦刚
-- 朱玲凤  13586116171  (空) → C1
UPDATE user_accounts SET reviewer_group_code = 'C1' WHERE phone = '13586116171' AND role = 'REVIEWER';  -- 朱玲凤
-- 李盈  13867481815  (空) → C1
UPDATE user_accounts SET reviewer_group_code = 'C1' WHERE phone = '13867481815' AND role = 'REVIEWER';  -- 李盈
-- 王临润  13606507266  (空) → C2
UPDATE user_accounts SET reviewer_group_code = 'C2' WHERE phone = '13606507266' AND role = 'REVIEWER';  -- 王临润
-- 蔡斌  13957159415  (空) → C2
UPDATE user_accounts SET reviewer_group_code = 'C2' WHERE phone = '13957159415' AND role = 'REVIEWER';  -- 蔡斌
-- 冯志仙  13867452301  (空) → C2
UPDATE user_accounts SET reviewer_group_code = 'C2' WHERE phone = '13867452301' AND role = 'REVIEWER';  -- 冯志仙
-- 李瑾  15068103880  (空) → C3
UPDATE user_accounts SET reviewer_group_code = 'C3' WHERE phone = '15068103880' AND role = 'REVIEWER';  -- 李瑾
-- 胡斌春  13906537115  (空) → C3
UPDATE user_accounts SET reviewer_group_code = 'C3' WHERE phone = '13906537115' AND role = 'REVIEWER';  -- 胡斌春
-- 周权  13588758501  (空) → C3
UPDATE user_accounts SET reviewer_group_code = 'C3' WHERE phone = '13588758501' AND role = 'REVIEWER';  -- 周权
-- 王跃胜  13505899996  (空) → C4
UPDATE user_accounts SET reviewer_group_code = 'C4' WHERE phone = '13505899996' AND role = 'REVIEWER';  -- 王跃胜
-- 黄丽华  13867129329  (空) → C4
UPDATE user_accounts SET reviewer_group_code = 'C4' WHERE phone = '13867129329' AND role = 'REVIEWER';  -- 黄丽华
-- 李伟  13958009748  (空) → C4
UPDATE user_accounts SET reviewer_group_code = 'C4' WHERE phone = '13958009748' AND role = 'REVIEWER';  -- 李伟
-- 卢芳燕  13505817318  (空) → B1
UPDATE user_accounts SET reviewer_group_code = 'B1' WHERE phone = '13505817318' AND role = 'REVIEWER';  -- 卢芳燕
-- 卜智斌  18958167819  (空) → B1
UPDATE user_accounts SET reviewer_group_code = 'B1' WHERE phone = '18958167819' AND role = 'REVIEWER';  -- 卜智斌
-- 谭明明  13588092636  (空) → B2
UPDATE user_accounts SET reviewer_group_code = 'B2' WHERE phone = '13588092636' AND role = 'REVIEWER';  -- 谭明明
-- 戴金华  13605887912  (空) → B2
UPDATE user_accounts SET reviewer_group_code = 'B2' WHERE phone = '13605887912' AND role = 'REVIEWER';  -- 戴金华
-- 潘胜东  13666669123  (空) → B3
UPDATE user_accounts SET reviewer_group_code = 'B3' WHERE phone = '13666669123' AND role = 'REVIEWER';  -- 潘胜东
-- 蔡晓芳  15990162166  (空) → B3
UPDATE user_accounts SET reviewer_group_code = 'B3' WHERE phone = '15990162166' AND role = 'REVIEWER';  -- 蔡晓芳
-- 洪理泉  13606700679  (空) → B4
UPDATE user_accounts SET reviewer_group_code = 'B4' WHERE phone = '13606700679' AND role = 'REVIEWER';  -- 洪理泉
-- 刘彩霞  18072963066  (空) → B4
UPDATE user_accounts SET reviewer_group_code = 'B4' WHERE phone = '18072963066' AND role = 'REVIEWER';  -- 刘彩霞
-- 杨永挺  13754322649  (空) → B5
UPDATE user_accounts SET reviewer_group_code = 'B5' WHERE phone = '13754322649' AND role = 'REVIEWER';  -- 杨永挺
-- 俞雪芬  13067987798  (空) → B5
UPDATE user_accounts SET reviewer_group_code = 'B5' WHERE phone = '13067987798' AND role = 'REVIEWER';  -- 俞雪芬
-- 宋剑平  13757119617  (空) → B6
UPDATE user_accounts SET reviewer_group_code = 'B6' WHERE phone = '13757119617' AND role = 'REVIEWER';  -- 宋剑平
-- 方英  15657036200  (空) → B6
UPDATE user_accounts SET reviewer_group_code = 'B6' WHERE phone = '15657036200' AND role = 'REVIEWER';  -- 方英
-- 陈美芬  13567618608  (空) → B7
UPDATE user_accounts SET reviewer_group_code = 'B7' WHERE phone = '13567618608' AND role = 'REVIEWER';  -- 陈美芬
-- 陈昌贵  13757119185  (空) → B7
UPDATE user_accounts SET reviewer_group_code = 'B7' WHERE phone = '13757119185' AND role = 'REVIEWER';  -- 陈昌贵
-- 李益民  13777887810  (空) → B8
UPDATE user_accounts SET reviewer_group_code = 'B8' WHERE phone = '13777887810' AND role = 'REVIEWER';  -- 李益民
-- 周莹  13626530377  (空) → B8
UPDATE user_accounts SET reviewer_group_code = 'B8' WHERE phone = '13626530377' AND role = 'REVIEWER';  -- 周莹
-- 钱莎莎  13738141961  (空) → B9
UPDATE user_accounts SET reviewer_group_code = 'B9' WHERE phone = '13738141961' AND role = 'REVIEWER';  -- 钱莎莎
-- 朱胜春  13511332938  (空) → B9
UPDATE user_accounts SET reviewer_group_code = 'B9' WHERE phone = '13511332938' AND role = 'REVIEWER';  -- 朱胜春
-- 赵彩莲  13958061766  (空) → B10
UPDATE user_accounts SET reviewer_group_code = 'B10' WHERE phone = '13958061766' AND role = 'REVIEWER';  -- 赵彩莲
-- 徐敏慧  15957921677  (空) → B10
UPDATE user_accounts SET reviewer_group_code = 'B10' WHERE phone = '15957921677' AND role = 'REVIEWER';  -- 徐敏慧
-- 方玢茹  13616555849  (空) → B11
UPDATE user_accounts SET reviewer_group_code = 'B11' WHERE phone = '13616555849' AND role = 'REVIEWER';  -- 方玢茹
-- 张春梅  15957716111  (空) → B11
UPDATE user_accounts SET reviewer_group_code = 'B11' WHERE phone = '15957716111' AND role = 'REVIEWER';  -- 张春梅
-- 陈飞波  13989818108  (空) → B12
UPDATE user_accounts SET reviewer_group_code = 'B12' WHERE phone = '13989818108' AND role = 'REVIEWER';  -- 陈飞波
-- 吕娜  13588426741  (空) → B12
UPDATE user_accounts SET reviewer_group_code = 'B12' WHERE phone = '13588426741' AND role = 'REVIEWER';  -- 吕娜
-- 宁丽  13750848040  (空) → B13
UPDATE user_accounts SET reviewer_group_code = 'B13' WHERE phone = '13750848040' AND role = 'REVIEWER';  -- 宁丽
-- 杨军  18072963988  (空) → B13
UPDATE user_accounts SET reviewer_group_code = 'B13' WHERE phone = '18072963988' AND role = 'REVIEWER';  -- 杨军
-- 姚智萍  15857353615  (空) → B14
UPDATE user_accounts SET reviewer_group_code = 'B14' WHERE phone = '15857353615' AND role = 'REVIEWER';  -- 姚智萍
-- 庄一渝  13588708076  (空) → B14
UPDATE user_accounts SET reviewer_group_code = 'B14' WHERE phone = '13588708076' AND role = 'REVIEWER';  -- 庄一渝
-- 郭佳奕  13566781071  (空) → B15
UPDATE user_accounts SET reviewer_group_code = 'B15' WHERE phone = '13566781071' AND role = 'REVIEWER';  -- 郭佳奕
-- 程晓英  13666650508  (空) → B15
UPDATE user_accounts SET reviewer_group_code = 'B15' WHERE phone = '13666650508' AND role = 'REVIEWER';  -- 程晓英
-- 朱文俊  13606515730  (空) → B16
UPDATE user_accounts SET reviewer_group_code = 'B16' WHERE phone = '13606515730' AND role = 'REVIEWER';  -- 朱文俊
-- 徐辉  13758490818  (空) → B16
UPDATE user_accounts SET reviewer_group_code = 'B16' WHERE phone = '13758490818' AND role = 'REVIEWER';  -- 徐辉
-- 蔡雪黎  13857771605  (空) → B17
UPDATE user_accounts SET reviewer_group_code = 'B17' WHERE phone = '13857771605' AND role = 'REVIEWER';  -- 蔡雪黎
-- 封亚萍  13867134906  (空) → B17
UPDATE user_accounts SET reviewer_group_code = 'B17' WHERE phone = '13867134906' AND role = 'REVIEWER';  -- 封亚萍
-- 陈志良  13567534846  (空) → B18
UPDATE user_accounts SET reviewer_group_code = 'B18' WHERE phone = '13567534846' AND role = 'REVIEWER';  -- 陈志良
-- 潘红英  13587179166  (空) → B18
UPDATE user_accounts SET reviewer_group_code = 'B18' WHERE phone = '13587179166' AND role = 'REVIEWER';  -- 潘红英
-- 张国兵  13675851802  (空) → B19
UPDATE user_accounts SET reviewer_group_code = 'B19' WHERE phone = '13675851802' AND role = 'REVIEWER';  -- 张国兵
-- 兰美娟  13757119537  (空) → B19
UPDATE user_accounts SET reviewer_group_code = 'B19' WHERE phone = '13757119537' AND role = 'REVIEWER';  -- 兰美娟
-- 马楠  13958111928  (空) → B20
UPDATE user_accounts SET reviewer_group_code = 'B20' WHERE phone = '13958111928' AND role = 'REVIEWER';  -- 马楠
-- 潘红英  13857188922  (空) → B20
UPDATE user_accounts SET reviewer_group_code = 'B20' WHERE phone = '13857188922' AND role = 'REVIEWER';  -- 潘红英
-- 郑叶平  13732586305  (空) → B21
UPDATE user_accounts SET reviewer_group_code = 'B21' WHERE phone = '13732586305' AND role = 'REVIEWER';  -- 郑叶平
-- 冯济业  13958202082  (空) → B21
UPDATE user_accounts SET reviewer_group_code = 'B21' WHERE phone = '13958202082' AND role = 'REVIEWER';  -- 冯济业
-- 王建平  13588887369  (空) → B22
UPDATE user_accounts SET reviewer_group_code = 'B22' WHERE phone = '13588887369' AND role = 'REVIEWER';  -- 王建平
-- 李雅岑  13777466804  (空) → B22
UPDATE user_accounts SET reviewer_group_code = 'B22' WHERE phone = '13777466804' AND role = 'REVIEWER';  -- 李雅岑
-- 周琳  13857211964  (空) → A1
UPDATE user_accounts SET reviewer_group_code = 'A1' WHERE phone = '13857211964' AND role = 'REVIEWER';  -- 周琳
-- 叶小云  13605818530  (空) → A1
UPDATE user_accounts SET reviewer_group_code = 'A1' WHERE phone = '13605818530' AND role = 'REVIEWER';  -- 叶小云
-- 钱玮  13588330061  (空) → A2
UPDATE user_accounts SET reviewer_group_code = 'A2' WHERE phone = '13588330061' AND role = 'REVIEWER';  -- 钱玮
-- 朱良枫  13586464989  (空) → A2
UPDATE user_accounts SET reviewer_group_code = 'A2' WHERE phone = '13586464989' AND role = 'REVIEWER';  -- 朱良枫
-- 蔡建利  13735192050  (空) → A3
UPDATE user_accounts SET reviewer_group_code = 'A3' WHERE phone = '13735192050' AND role = 'REVIEWER';  -- 蔡建利
-- 沈杨  13957883107  (空) → A3
UPDATE user_accounts SET reviewer_group_code = 'A3' WHERE phone = '13957883107' AND role = 'REVIEWER';  -- 沈杨
-- 周尧英  13615758052  (空) → A4
UPDATE user_accounts SET reviewer_group_code = 'A4' WHERE phone = '13615758052' AND role = 'REVIEWER';  -- 周尧英
-- 严志瑜  13958365721  (空) → A4
UPDATE user_accounts SET reviewer_group_code = 'A4' WHERE phone = '13958365721' AND role = 'REVIEWER';  -- 严志瑜
-- 严涓  13588216288  (空) → A5
UPDATE user_accounts SET reviewer_group_code = 'A5' WHERE phone = '13588216288' AND role = 'REVIEWER';  -- 严涓
-- 陈雪琴  13957832316  (空) → A5
UPDATE user_accounts SET reviewer_group_code = 'A5' WHERE phone = '13957832316' AND role = 'REVIEWER';  -- 陈雪琴
-- 楼尉  13516743880  (空) → A6
UPDATE user_accounts SET reviewer_group_code = 'A6' WHERE phone = '13516743880' AND role = 'REVIEWER';  -- 楼尉
-- 袁惠萍  13957228318  (空) → A6
UPDATE user_accounts SET reviewer_group_code = 'A6' WHERE phone = '13957228318' AND role = 'REVIEWER';  -- 袁惠萍
-- 朱健倩  13516800991  (空) → A7
UPDATE user_accounts SET reviewer_group_code = 'A7' WHERE phone = '13516800991' AND role = 'REVIEWER';  -- 朱健倩
-- 吴海英  13758953542  (空) → A7
UPDATE user_accounts SET reviewer_group_code = 'A7' WHERE phone = '13758953542' AND role = 'REVIEWER';  -- 吴海英
*/

-- ── B. 修正机构 institution_id ─────────────────────────────────
-- 李伟  13958009748  institution_id: 25 → 24  (浙江大学医学院附属第二医院)
UPDATE user_accounts SET institution_id = 24 WHERE phone = '13958009748' AND role = 'REVIEWER';  -- 李伟

-- ── C. 新建账号：无需新建（所有 4.13 专家在生产库均有记录）

-- ── D. 执行后验证 ───────────────────────────────────────────────
SELECT ua.name, ua.phone, ua.reviewer_group_code,
       ua.institution_id, i.name AS institution_name
FROM user_accounts ua
LEFT JOIN institutions i ON i.id = ua.institution_id
WHERE ua.phone IN ('15868899348', '13586116171', '13867481815', '13606507266', '13957159415', '13867452301', '15068103880', '13906537115', '13588758501', '13505899996', '13867129329', '13958009748', '13505817318', '18958167819', '13588092636', '13605887912', '13666669123', '15990162166', '13606700679', '18072963066', '13754322649', '13067987798', '13757119617', '15657036200', '13567618608', '13757119185', '13777887810', '13626530377', '13738141961', '13511332938', '13958061766', '15957921677', '13616555849', '15957716111', '13989818108', '13588426741', '13750848040', '18072963988', '15857353615', '13588708076', '13566781071', '13666650508', '13606515730', '13758490818', '13857771605', '13867134906', '13567534846', '13587179166', '13675851802', '13757119537', '13958111928', '13857188922', '13732586305', '13958202082', '13588887369', '13777466804', '13857211964', '13605818530', '13588330061', '13586464989', '13735192050', '13957883107', '13615758052', '13958365721', '13588216288', '13957832316', '13516743880', '13957228318', '13516800991', '13758953542', '13958009748')
ORDER BY ua.reviewer_group_code, ua.name;