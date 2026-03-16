-- const_init_institutions 约束修正（推荐）
-- 规则：name + uscc 唯一；uscc 允许重复

-- 1) 删除旧的 uscc 唯一约束（若存在）
ALTER TABLE `const_init_institutions`
  DROP INDEX `uk_uscc`;

-- 2) 创建 name + uscc 组合唯一约束
ALTER TABLE `const_init_institutions`
  ADD UNIQUE KEY `uk_name_uscc` (`name`, `uscc`);

-- 3) 保留 uscc 普通索引（便于检索）
ALTER TABLE `const_init_institutions`
  ADD INDEX `idx_uscc` (`uscc`);
