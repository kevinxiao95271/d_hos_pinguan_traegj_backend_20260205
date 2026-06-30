-- 为 competitions.name 添加唯一索引
-- 执行前请确认现有数据无重名，如有重名须先手动处理
ALTER TABLE competitions
    MODIFY COLUMN name VARCHAR(120) NOT NULL,
    ADD UNIQUE KEY uq_competitions_name (name);
