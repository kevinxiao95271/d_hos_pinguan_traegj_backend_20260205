-- 添加项目摘要的"运作"和"展示"字段
-- 执行前请确认数据库连接

USE pinguan_competition_23;

-- 添加 operation 字段（运作）
ALTER TABLE project_summaries 
ADD COLUMN operation VARCHAR(1000) NULL COMMENT '运作' AFTER discussion;

-- 添加 presentation 字段（展示）
ALTER TABLE project_summaries 
ADD COLUMN presentation VARCHAR(1000) NULL COMMENT '展示' AFTER operation;

-- 验证字段是否添加成功
DESCRIBE project_summaries;
