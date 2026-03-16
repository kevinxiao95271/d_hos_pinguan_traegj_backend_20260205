-- const_init_institutions 导入前约束修正
-- 说明：源数据中 uscc 存在重复（真实业务数据），不能使用唯一约束

ALTER TABLE `const_init_institutions`
  DROP INDEX `uk_uscc`;

-- 保留普通索引，支持检索性能
ALTER TABLE `const_init_institutions`
  ADD INDEX `idx_uscc` (`uscc`);
