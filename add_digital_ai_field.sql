-- 添加"是否与数字化/人工智能应用相关主题"字段
-- 执行前请确认数据库连接

USE pinguan_competition_23;

-- 添加 related_to_digital_ai 字段
ALTER TABLE activity_infos 
ADD COLUMN related_to_digital_ai BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否与数字化/人工智能应用相关主题' AFTER cross_department;

-- 验证字段是否添加成功
DESCRIBE activity_infos;

-- 查看现有数据（默认值为FALSE）
SELECT id, registration_id, theme, cross_department, related_to_digital_ai 
FROM activity_infos 
LIMIT 5;
