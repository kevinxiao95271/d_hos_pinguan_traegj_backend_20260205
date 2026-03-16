-- institutions 约束修正（生产可执行）
-- 目标：
-- 1) 删除 uscc 单列唯一约束（无论索引名是什么）
-- 2) 增加 name + uscc 组合唯一约束
-- 3) 保留 uscc 普通索引

START TRANSACTION;

-- 可选：先看是否存在 name+uscc 重复（若 >0，下面 add unique 会失败）
-- SELECT name, uscc, COUNT(*) c
-- FROM institutions
-- GROUP BY name, uscc
-- HAVING c > 1;

-- 1) 删除 institutions 上 uscc 单列唯一索引（动态按实际索引名删除）
SET @drop_idx_sql = (
  SELECT CONCAT('ALTER TABLE `institutions` DROP INDEX `', s.INDEX_NAME, '`')
  FROM information_schema.STATISTICS s
  WHERE s.TABLE_SCHEMA = DATABASE()
    AND s.TABLE_NAME = 'institutions'
    AND s.NON_UNIQUE = 0
  GROUP BY s.INDEX_NAME
  HAVING COUNT(*) = 1
     AND MAX(s.COLUMN_NAME) = 'uscc'
  LIMIT 1
);
SET @drop_idx_sql = IFNULL(@drop_idx_sql, 'SELECT 1');
PREPARE stmt_drop_idx FROM @drop_idx_sql;
EXECUTE stmt_drop_idx;
DEALLOCATE PREPARE stmt_drop_idx;

-- 2) 增加 name + uscc 组合唯一索引（若已存在则跳过）
SET @add_uk_sql = (
  SELECT IF(
    EXISTS (
      SELECT 1
      FROM information_schema.STATISTICS s
      WHERE s.TABLE_SCHEMA = DATABASE()
        AND s.TABLE_NAME = 'institutions'
        AND s.INDEX_NAME = 'uk_name_uscc'
    ),
    'SELECT 1',
    'ALTER TABLE `institutions` ADD UNIQUE KEY `uk_name_uscc` (`name`, `uscc`)'
  )
);
PREPARE stmt_add_uk FROM @add_uk_sql;
EXECUTE stmt_add_uk;
DEALLOCATE PREPARE stmt_add_uk;

-- 3) 增加 uscc 普通索引（若不存在）
SET @add_idx_sql = (
  SELECT IF(
    EXISTS (
      SELECT 1
      FROM information_schema.STATISTICS s
      WHERE s.TABLE_SCHEMA = DATABASE()
        AND s.TABLE_NAME = 'institutions'
        AND s.INDEX_NAME = 'idx_uscc'
    ),
    'SELECT 1',
    'ALTER TABLE `institutions` ADD INDEX `idx_uscc` (`uscc`)'
  )
);
PREPARE stmt_add_idx FROM @add_idx_sql;
EXECUTE stmt_add_idx;
DEALLOCATE PREPARE stmt_add_idx;

COMMIT;
