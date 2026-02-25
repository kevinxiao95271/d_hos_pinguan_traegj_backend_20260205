-- 步骤1: 创建常量初始化机构表（存储全部36K+机构，仅用于注册搜索）
CREATE TABLE IF NOT EXISTS const_init_institutions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(64) NOT NULL COMMENT '机构代码',
    uscc VARCHAR(32) NOT NULL COMMENT '统一社会信用代码',
    name VARCHAR(200) NOT NULL COMMENT '机构名称',
    region VARCHAR(64) COMMENT '地区',
    city VARCHAR(50) COMMENT '城市',
    level VARCHAR(32) COMMENT '等级',
    category VARCHAR(64) COMMENT '类别',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    
    -- 索引（用于快速搜索）
    UNIQUE KEY uk_code (code),
    UNIQUE KEY uk_uscc (uscc),
    KEY idx_name (name),
    KEY idx_region (region),
    KEY idx_city (city),
    KEY idx_level (level),
    KEY idx_region_name (region, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='常量机构库（36K+，仅用于注册时搜索）';

-- 步骤2: 将现有 institutions 数据迁移到 const_init_institutions
INSERT INTO const_init_institutions (code, uscc, name, region, city, level, category, created_at)
SELECT code, uscc, name, region, city, level, 
       CASE 
           WHEN level = '三级' THEN '三级医院'
           WHEN level = '二级' THEN '二级医院'
           WHEN level = '一级' THEN '一级医院'
           ELSE '其他'
       END as category,
       created_at
FROM institutions;

-- 步骤3: 查找当前系统中已有用户关联的机构
-- 这些机构需要保留在 institutions 表中
SELECT DISTINCT i.id, i.code, i.uscc, i.name, i.region, i.city, i.level
FROM institutions i
INNER JOIN user_accounts u ON u.institution_id = i.id;

-- 步骤4: 备份后清理（见下一个脚本）
