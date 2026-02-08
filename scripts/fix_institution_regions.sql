-- 修正机构地区信息
-- 发现17个机构的地区信息错误，需要修正

-- 省级医院（应该在杭州）
UPDATE institutions SET region = '杭州' WHERE id = 7;   -- 浙江医院
UPDATE institutions SET region = '杭州' WHERE id = 8;   -- 浙江大学医学院附属第一医院（浙一医院）
UPDATE institutions SET region = '杭州' WHERE id = 9;   -- 浙江省人民医院
UPDATE institutions SET region = '杭州' WHERE id = 11;  -- 浙江大学医学院附属儿童医院（浙江省儿童医院）
UPDATE institutions SET region = '杭州' WHERE id = 13;  -- 浙江省肿瘤医院
UPDATE institutions SET region = '杭州' WHERE id = 14;  -- 浙江大学医学院附属口腔医院（浙江省口腔医院）

-- 杭州市医院
UPDATE institutions SET region = '杭州' WHERE id = 12;  -- 浙江省中西医结合医院（杭州市红十字会医院）
UPDATE institutions SET region = '杭州' WHERE id = 15;  -- 杭州市肝病研究所（西溪医院）

-- 宁波市医院
UPDATE institutions SET region = '宁波' WHERE id = 16;  -- 宁波市第一医院
UPDATE institutions SET region = '宁波' WHERE id = 18;  -- 宁波市医疗中心李惠利医院

-- 温州市医院
UPDATE institutions SET region = '温州' WHERE id = 19;  -- 温州医科大学附属第二医院（温医二院）

-- 绍兴市医院
UPDATE institutions SET region = '绍兴' WHERE id = 20;  -- 绍兴市人民医院

-- 嘉兴市医院
UPDATE institutions SET region = '嘉兴' WHERE id = 21;  -- 嘉兴市第一医院

-- 湖州市医院
UPDATE institutions SET region = '湖州' WHERE id = 22;  -- 湖州市中心医院

-- 金华市医院
UPDATE institutions SET region = '金华' WHERE id = 23;  -- 金华市中心医院

-- 衢州市医院
UPDATE institutions SET region = '衢州' WHERE id = 24;  -- 衢州市人民医院

-- 特殊情况：浙江省医疗健康集团衢州医院
-- 虽然名称包含"衢州"，但作为省级医疗集团，可能应该归为杭州
-- 请根据实际情况决定是否执行此条
-- UPDATE institutions SET region = '杭州' WHERE id = 40;  -- 浙江省医疗健康集团衢州医院（衢州中心医院）

-- 验证修正结果
SELECT 
    id,
    name,
    region
FROM institutions
WHERE id IN (7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24)
ORDER BY id;
