-- 创建活跃机构表（轻量级，用于报名等业务流程）
CREATE TABLE IF NOT EXISTS active_institutions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 从institutions表复制的基础信息
    source_institution_id BIGINT NOT NULL COMMENT '原始机构表ID',
    code VARCHAR(64) NOT NULL COMMENT '机构代码',
    uscc VARCHAR(32) NOT NULL COMMENT '统一社会信用代码',
    name VARCHAR(200) NOT NULL COMMENT '机构名称',
    region VARCHAR(64) COMMENT '地区',
    city VARCHAR(50) COMMENT '城市',
    level VARCHAR(32) COMMENT '等级',
    category VARCHAR(64) COMMENT '类别',
    
    -- 激活信息
    activated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '激活时间',
    activated_by BIGINT COMMENT '激活用户ID',
    
    -- 统计信息
    user_count INT DEFAULT 0 COMMENT '关联用户数',
    registration_count INT DEFAULT 0 COMMENT '报名数',
    
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    
    -- 索引
    UNIQUE KEY uk_source_institution_id (source_institution_id),
    UNIQUE KEY uk_code (code),
    UNIQUE KEY uk_uscc (uscc),
    KEY idx_name (name),
    KEY idx_region (region),
    KEY idx_city (city),
    KEY idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活跃机构表（注册用户所在机构）';

-- 说明：
-- 1. active_institutions 是轻量级表，只存储有用户注册的机构
-- 2. source_institution_id 关联原始的 institutions 表
-- 3. 用户注册时，从 institutions 搜索选择，自动添加到 active_institutions
-- 4. registrations、user_accounts 等表关联 active_institutions
-- 5. 预计数据量：几百条，性能极佳

-- 查询示例
SELECT COUNT(*) FROM active_institutions;
