-- 修复评委职称数据
-- 将 "Test Title" 更新为真实职称

-- 查看当前职称为 "Test Title" 的评委
SELECT 
    id,
    name,
    phone,
    title,
    institution_id
FROM user_accounts
WHERE role = 'REVIEWER' AND title = 'Test Title';

-- 更新李明华的职称（ID: 6）
-- 浙江大学医学院附属第二医院（浙二医院）
UPDATE user_accounts 
SET title = '主任医师' 
WHERE id = 6;

-- 更新孙丽娟的职称（ID: 17）
-- 浙江大学医学院附属邵逸夫医院（邵逸夫医院）
UPDATE user_accounts 
SET title = '副主任医师' 
WHERE id = 17;

-- 更新陈卫东的职称（ID: 14）
-- 浙江大学医学院附属第二医院（浙二医院）
UPDATE user_accounts 
SET title = '主任医师' 
WHERE id = 14;

-- 验证更新结果
SELECT 
    id,
    name,
    phone,
    title,
    institution_id
FROM user_accounts
WHERE id IN (6, 14, 17);

-- 检查是否还有其他 "Test Title"
SELECT COUNT(*) as remaining_test_titles
FROM user_accounts
WHERE role = 'REVIEWER' AND title = 'Test Title';
