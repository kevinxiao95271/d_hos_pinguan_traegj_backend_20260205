-- 修改评分字段为支持小数点后一位
-- 执行前请先备份数据库

USE d_hos_pinguan_traegj_20260205;

-- 修改review_scores表的分值字段
ALTER TABLE review_scores 
  MODIFY COLUMN plan DECIMAL(4,1) NOT NULL COMMENT '计划分值',
  MODIFY COLUMN problem DECIMAL(4,1) NOT NULL COMMENT '问题分值',
  MODIFY COLUMN action DECIMAL(4,1) NOT NULL COMMENT '行动分值',
  MODIFY COLUMN success DECIMAL(4,1) NOT NULL COMMENT '成功分值',
  MODIFY COLUMN review DECIMAL(4,1) NOT NULL COMMENT '评审分值',
  MODIFY COLUMN operation DECIMAL(4,1) NOT NULL COMMENT '操作分值',
  MODIFY COLUMN presentation DECIMAL(4,1) NOT NULL COMMENT '展示分值',
  MODIFY COLUMN total DECIMAL(5,1) NOT NULL COMMENT '总分';

-- 验证修改结果
DESCRIBE review_scores;

-- 查看现有数据（应该自动转换为小数格式）
SELECT id, plan, problem, action, success, review, operation, presentation, total 
FROM review_scores 
LIMIT 5;
